"""
Background entry point.
"""
from gooutsafe import create_app
from gooutsafe.comm import BackgroundWorkers
import logging

# creating application starting the broker
app = create_app(broker_start=True, log_level=logging.INFO)

# creating the manager object
background_workers = BackgroundWorkers()


def main():
    import signal

    def signal_handler(signo, frame):
        app.logger.info('Sending stop to background workers...')
        background_workers.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # starting workers
    background_workers.start()


if __name__ == '__main__':
    main()
