"""
Background entry point.
"""
from gooutsafe import create_app
import signal
import sys

# creating application starting the broker
app = create_app(broker_start=True)


def main():
    """Since we have a single worker, we can just import it and execute it"""
    from gooutsafe.comm.worker import ReservationWorker
    worker = ReservationWorker()

    def signal_handler(signo, frame):
        worker.stop_run()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    worker.run()


if __name__ == '__main__':
    main()
