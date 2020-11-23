import pika
from gooutsafe import app
from gooutsafe.dao.reservation_manager import ReservationManager
import json


class ReservationWorker:
    """This class represents the background worker that listens for tasks in RabbitMQ queue called
    conf['RESERVATION_WORKER_QUEUE_NAME'].
    It should be run by background.py file.1
    """

    def __init__(self):
        from gooutsafe.comm import amqp_connection, conf
        self.queue_name = conf['RESERVATION_WORKER_QUEUE_NAME']
        self.channel = amqp_connection.channel()
        self.channel.queue_declare(
            self.queue_name
        )

    def retrieve_by_customer_id(self, message):
        return ReservationManager.retrieve_by_customer_id(message['customer_id'])

    def retrieve_all_contact_reservation_by_id(self, message):
        return ReservationManager.retrieve_all_contact_reservation_by_id(message['customer_id'])

    def retrieve_by_customer_id_in_future(self, message):
        return ReservationManager.retrieve_by_customer_id_in_future(message['customer_id'])

    def retrieve_by_customer_id_in_last_14_days(self, message):
        return ReservationManager.retrieve_by_customer_id_in_last_14_days(message['customer_id'])

    def function_dispatcher(self, message):
        if message['func'] == 'retrieve_by_customer_id':
            return self.retrieve_by_customer_id(message)
        elif message['func'] == 'retrieve_all_contact_reservation_by_id':
            return self.retrieve_all_contact_reservation_by_id(message)
        elif message['func'] == 'retrieve_by_customer_id_in_future':
            return self.retrieve_by_customer_id_in_future(message)
        elif message['func'] == 'retrieve_by_customer_id_in_last_14_days':
            return self.retrieve_by_customer_id_in_last_14_days(message)
        else:
            raise ValueError('This operation is not implemented')

    def on_request(self, ch, method, props, body):
        app.logger.info('Received new message in the queue')

        try:
            message = json.loads(body)
            response = json.dumps(self.function_dispatcher(message))
        except ValueError:
            app.logger.error('Received invalid message, message=%s' % body)
            response = json.loads(dict(status='Invalid Message Received'))
        except NotImplementedError:
            app.logger.error('Received invalido operation, message=%s' % body)
            response = json.loads(dict(status='Invalid Operation Received'))

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(
                             correlation_id=props.correlation_id
                         ),
                         body=response)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        app.logger.info('Worker [START] received...')
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name,
            consumer_tag='worker',
            on_message_callback=self.on_request
        )
        app.logger.info('Worker is now [STARTED]!')
        self.channel.start_consuming()

    def stop_run(self):
        app.logger.info('Worker [STOP] received...')
        self.channel.stop_consuming()
        self.channel.close()
        app.logger.info('Worker is now [STOPPED]!')
