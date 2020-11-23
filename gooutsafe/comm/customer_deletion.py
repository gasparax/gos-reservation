from gooutsafe import app
from kombu.mixins import ConsumerMixin
from kombu import Exchange, Queue
from gooutsafe.dao.reservation_manager import ReservationManager


class CustomerDeletionWorker(ConsumerMixin):
    def __init__(self, connection):
        self.connection = connection

        exchange = Exchange(
            app.config.get('RABMQ_SEND_EXCHANGE_NAME'),
            type='topic',
            channel=connection.channel()
        )

        exchange.declare(nowait=False)
        self.queues = [Queue('CustomerDeletionQueue', exchange, routing_key='CUSTOMER_DELETION')]

    def on_message(self, body, message):
        message.ack()
        app.logger.info('Received a message of user deletion.')
        user_id = body['user_id']
        ReservationManager.delete_all_user_reservation(user_id=user_id)

    def get_consumers(self, consumer, channel):
        return [consumer(queues=self.queues,
                         callbacks=[self.on_message])]
