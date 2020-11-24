from kombu.mixins import ConsumerMixin
import json
from kombu import Exchange, Queue


class CustomerDeletionWorker(ConsumerMixin):
    def __init__(self, connection, logger):
        self.connection = connection
        self.logger = logger
        from gooutsafe import app

        exchange = Exchange(
            app.config.get('RABMQ_SEND_EXCHANGE_NAME'),
            type='topic',
            channel=connection.channel()
        )

        exchange.declare(nowait=False)
        self.queues = [Queue('CustomerDeletionQueue', exchange, routing_key='CUSTOMER_DELETION')]

    def on_message(self, body, message):
        message_object = None
        try:
            message_object = json.loads(body)
        except ValueError:
            self.logger.error('Cannot decode json message! Message=%s' % body)
            message.ack()
            return

        if 'user_id' not in message_object:
            self.logger.error('Message does not contain user_id!')
        else:
            self.logger.info('Received a message of user deletion with user_id=%s', message_object['user_id'])
            from gooutsafe.dao.reservation_manager import ReservationManager
            try:
                ReservationManager.delete_all_user_reservation(user_id=message_object['user_id'])
            except Exception as re:
                self.logger.error('Runtime error during deleting all_user_reservations, %s' % re)

        # send ack to message
        message.ack()

    def get_consumers(self, consumer, channel):
        return [consumer(queues=self.queues,
                         callbacks=[self.on_message])]

    def stop(self):
        self.should_stop = True
