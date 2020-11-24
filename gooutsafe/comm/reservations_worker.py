from kombu.mixins import ConsumerMixin
from kombu import Producer, Queue, Connection
import json


class ReservationWorker(ConsumerMixin):
    """This class represents the background worker that listens for tasks in RabbitMQ queue called
        conf['RESERVATION_WORKER_QUEUE_NAME'].
        It should be run by background.py file.
    """

    class ExecutionException(Exception):
        """Exception raised during execution of function"""

        def __init__(self, message=''):
            super(ReservationWorker.ExecutionException, self).__init__(message)

    def __init__(self, connection, logger):
        from gooutsafe.comm import conf
        self.logger = logger
        self.connection = connection
        self.queues = [Queue(conf['RESERVATION_WORKER_QUEUE_NAME'])]
        self.producer = Producer(connection.clone().channel())

    def get_consumers(self, consumer, channel):
        return [consumer(queues=self.queues,
                         callbacks=[self.on_message])]

    def stop(self):
        self.should_stop = True

    def on_message(self, body, message):
        self.logger.info('Received new message in the queue for reservations worker')

        try:
            message_object = json.loads(body, parse_int=True)
            response_object = self.__function_dispatcher(message_object)
        except ValueError as ve:
            self.logger.error('Cannot parse JSON object, %s' % ve)
            response_object = dict(
                status='Cannot parse JSON object'
            )
        except NotImplementedError:
            self.logger.error('Received invalid operation, message=%s' % body)
            response_object = dict(
                status='Invalid Operation Received'
            )
        except self.ExecutionException:
            # exception already logged
            response_object = dict(
                status='Internal Server Error'
            )

        response: str
        try:
            response = json.dumps(response_object)
        except ValueError:
            self.logger.error('Cannot dump response_object into a JSON, response_object=%s' % response_object)

        # checking if the sender has set the reply_to
        if message.properties['reply_to'] is None:
            self.logger.error('Sender has not set the reply_to, so.. Where should I push the reply?')
            self.logger.error('BTW, the reply is this: %s' % response)
        else:
            self.producer.publish(
                body=response,
                exchange='',
                routing_key=message.properties['reply_to'],
                properties=dict(
                    correlation_id=message.properties['correlation_id']
                ),
            )

        message.ack()

    @staticmethod
    def __retrieve_by_customer_id(message):
        from gooutsafe.dao.reservation_manager import ReservationManager
        return ReservationManager.retrieve_by_customer_id(message['customer_id'])

    @staticmethod
    def __retrieve_all_contact_reservation_by_id(message):
        from gooutsafe.dao.reservation_manager import ReservationManager
        return ReservationManager.retrieve_all_contact_reservation_by_id(message['customer_id'])

    @staticmethod
    def __retrieve_by_customer_id_in_future(message):
        from gooutsafe.dao.reservation_manager import ReservationManager
        return ReservationManager.retrieve_by_customer_id_in_future(message['customer_id'])

    @staticmethod
    def __retrieve_by_customer_id_in_last_14_days(message):
        from gooutsafe.dao.reservation_manager import ReservationManager
        return ReservationManager.retrieve_by_customer_id_in_last_14_days(message['customer_id'])

    def __function_dispatcher(self, message):
        if 'func' not in message or 'customer_id' not in message:
            raise ValueError('Message object does not contain \'func\' or \'customer_id\'')

        try:
            if message['func'] == 'retrieve_by_customer_id':
                return self.__retrieve_by_customer_id(message)
            elif message['func'] == 'retrieve_all_contact_reservation_by_id':
                return self.__retrieve_all_contact_reservation_by_id(message)
            elif message['func'] == 'retrieve_by_customer_id_in_future':
                return self.__retrieve_by_customer_id_in_future(message)
            elif message['func'] == 'retrieve_by_customer_id_in_last_14_days':
                return self.__retrieve_by_customer_id_in_last_14_days(message)
        except RuntimeError as re:
            self.logger.error(re)
            raise self.ExecutionException('A RuntimeError was raised during execution of function dispatcher')
        except Exception as ex:
            self.logger.error(ex)
            raise self.ExecutionException('An exception was raised during execution of function dispatcher!')

        raise NotImplementedError('This operation is not implemented')
