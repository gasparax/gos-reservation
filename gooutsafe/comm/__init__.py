"""
This package contains all the classes
that manage the communications with other microservices.
"""
import os
import logging
from kombu import Connection
from pika import BlockingConnection, URLParameters
from kombu.mixins import ConsumerMixin
import threading

__REQUIRED_CONFIG_KEYS = ['RABBIT_MQ_HOST', 'RABBIT_MQ_PORT',
                          'RABBIT_MQ_VHOST', 'RESERVATION_WORKER_QUEUE_NAME']
conf = dict
disabled: bool
logger: logging.Logger


def init_rabbit_mq(app):
    """
    Initialize Rabbit MQ Connection
    :return: None
    """
    global conf
    global logger

    # configuring logger
    logger = app.logger

    # loading configuration
    conf = dict()
    for key in __REQUIRED_CONFIG_KEYS:
        value = os.getenv(key, None)

        if value is None:
            raise RuntimeError('Cannot find the environment variable %s for Rabbit MQ Configuration' % key)

        conf[key] = value

    # Getting parameters
    conf['RABBIT_MQ_URL'] = 'amqp://%s:%s/%s' % (
        conf['RABBIT_MQ_HOST'], conf['RABBIT_MQ_PORT'], conf['RABBIT_MQ_VHOST']
    )

    # loading background workers classes
    BackgroundWorkers.load_workers()

    logger.info('AMQP Configuration initialized!')


class BackgroundWorkers(object):
    """This class represents the manager of background workers"""
    background_workers = []

    # State variable
    started = False

    @classmethod
    def load_workers(cls):
        try:
            from gooutsafe.comm.reservations_worker import ReservationWorker
            from gooutsafe.comm.customer_deletion import CustomerDeletionWorker
            from gooutsafe.comm.restaurant_deletion import RestaurantDeletionWorker

            cls.background_workers.append(ReservationWorker)
            cls.background_workers.append(CustomerDeletionWorker)
            cls.background_workers.append(RestaurantDeletionWorker)
        except ImportError as ie:
            raise RuntimeError('Cannot load workers because due to an ImportError %s' % ie)

    @classmethod
    def start(cls):
        """It starts all background workers"""
        if cls.started:
            return
        cls.started = True

        if len(cls.background_workers) < 1:
            raise RuntimeError('Background Workers are not loaded!')

        logger.info('Starting background workers...')

        # worker connections
        cls.workers_conn = []
        # workers
        cls.workers = []

        for worker_class in cls.background_workers:

            if issubclass(worker_class, ConsumerMixin):
                # using kombu conn
                conn = Connection(conf['RABBIT_MQ_URL'], heartbeat=4)
                # creating worker and worker thread
                worker = worker_class(conn, logger)
                worker_thread = threading.Thread(target=worker.run)
            elif issubclass(worker_class, threading.Thread):
                # using standard blocking connection with pika
                conn = BlockingConnection(parameters=URLParameters(conf['RABBIT_MQ_URL']))
                # creating worker and worker thread
                worker = worker_class(conn, logger)
                worker_thread = worker
            else:
                raise RuntimeError('Unsupported worker type!')

            worker_thread.setName('BackgroundWorker %s' % worker_class)
            worker_thread.start()

            cls.workers_conn.append(conn)
            cls.workers.append(worker)
            logger.info('Worker %s started!' % worker_class)

        logger.info('Background workers started!')

    @classmethod
    def stop(cls):
        """It stops all background workers"""
        if not cls.started:
            return

        logger.info('Stopping background workers...')
        # closing connections triggers the workers stop procedure
        for worker, conn in zip(cls.workers, cls.workers_conn):
            if isinstance(conn, Connection):
                # closing directly
                worker.stop()

            elif isinstance(conn, BlockingConnection) and isinstance(worker, threading.Thread):
                # we need to stop the consumer
                worker.stop()
            else:
                raise RuntimeError('Unsopported worker!')

        cls.started = False
        logger.info('Background workers stopped!')
