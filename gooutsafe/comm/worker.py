import pika


class ReservationWorker:
    """This class represents the background worker that listens for tasks in RabbitMQ queue called
    conf['RESERVATION_WORKER_QUEUE_NAME'].
    It should be run by background.py file.1
    """

    def __init__(self):
        from gooutsafe.comm import amqp_connection, conf
        self.queue_name = conf['RESERVATION_WORKER_QUEUE_NAME']
        self.exchange_name = conf['RABBIT_MQ_EXCHANGE_NAME']
        self.channel = amqp_connection.channel()
        self.channel.queue_declare(
            self.queue_name
        )

    def on_request(self, ch, method, props, body):
        print('received body=%s' % body)

        response = 'maboh'
        ch.basic_publish(exchange=self.exchange_name,
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(
                             correlation_id=props.correlation_id
                         ),
                         body=response)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name,
            consumer_tag='worker',
            on_message_callback=self.on_request
        )
        self.channel.start_consuming()
