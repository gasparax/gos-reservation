import unittest


class ResourceTest(unittest.TestCase):
    """
    This class should be implemented by
    all classes that tests resources
    """
    client = None

    @classmethod
    def setUpClass(cls):
        from gooutsafe import create_app
        app = create_app()
        cls.client = app.test_client()
        from tests.models.test_reservation import TestReservation
        cls.test_reservation = TestReservation
        from gooutsafe.dao import reservation_manager
        cls.reservation_manager = reservation_manager.ReservationManager