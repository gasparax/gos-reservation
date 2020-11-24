from kombu.mixins import ConsumerMixin
from kombu import Exchange, Queue
import json


class RestaurantDeletionWorker(ConsumerMixin):
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
        self.queues = [Queue('RestaurantDeletionQueue', exchange, routing_key='RESTAURANT_DELETION')]

    def on_message(self, body, message):
        message_object = None
        try:
            message_object = json.loads(body)
        except ValueError:
            self.logger.error('Cannot decode json message! Message=%s' % body)
            message.ack()
            return

        if 'restaurant_id' not in message_object:
            self.logger.error('restaurant_id must be a property of message! Message=%s' % body)
        else:
            self.logger.info('Received a message of restaurant deletion with id=%s' % message_object['restaurant_id'])
            from gooutsafe.dao.reservation_manager import ReservationManager
            try:
                ReservationManager.delete_all_restaurant_reservation(restaurant_id=message_object['restaurant_id'])
            except Exception as re:
                self.logger.error(
                    'A runtime error is raised during delete_all_restaurant_reservations invocation! Exception=%s' % re)

        message.ack()

    def get_consumers(self, consumer, channel):
        return [consumer(queues=self.queues,
                         callbacks=[self.on_message])]

    def stop(self):
        self.should_stop = True
