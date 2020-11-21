"""
Background entry point.
"""
from gooutsafe import create_app

# creating application starting the broker
app = create_app(broker_start=True)


def main():
    """Since we have a single worker, we can just import it and execute it"""
    from gooutsafe.comm.worker import ReservationWorker
    worker = ReservationWorker()
    worker.run()


if __name__ == '__main__':
    main()
