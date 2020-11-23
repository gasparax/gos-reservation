from gooutsafe import app
from kombu.mixins import ConsumerMixin
from kombu import Exchange, Queue
from gooutsafe.dao.reservation_manager import ReservationManager


class RestaurantDeletionWorker(ConsumerMixin):
    def __init__(self, connection):
        self.connection = connection

        exchange = Exchange(
            app.config.get('RABMQ_SEND_EXCHANGE_NAME'),
            type='topic',
            channel=connection.channel()
        )

        exchange.declare(nowait=False)
        self.queues = [Queue('RestaurantDeletionQueue', exchange, routing_key='RESTAURANT_DELETION')]

    def on_message(self, body, message):
        message.ack()
        app.logger.info('Received a message of restaurant deletion.')
        print(body)
        restaurant_id = body['restaurant_id']
        ReservationManager.delete_all_restaurant_reservation(restaurant_id=restaurant_id)

    def get_consumers(self, consumer, channel):
        return [consumer(queues=self.queues,
                         callbacks=[self.on_message])]
