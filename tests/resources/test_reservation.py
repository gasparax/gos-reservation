from .resource_test import ResourceTest
from faker import Faker
from datetime import time



class ReservationResTest(ResourceTest):
    faker = Faker()


    @classmethod
    def setUpClass(cls):
        super(ReservationResTest, cls).setUpClass()


    def test_create_reservation(self):

        pass   


    def test_delete_reservation(self):

        pass

    def test_get_all_reservation_restaurant(self):

        pass

    def test_get_all_reservation_customer(self):

        pass


    def test_edit_reservation(self):

        pass


    def test_confirm_reservation(self):

        pass


# Tests on helper methods (TODO: refactoring)

    def test_check_time_interval(self):
        from gooutsafe.views.reservation import check_time_interval
        start1 = datetime.datetime(year=2020, month=11, day=9)
        end1 = datetime.datetime(year=2020, month=11, day=15)
        start2 = datetime.datetime(year=2020, month=11, day=20)
        end2 = datetime.datetime(year=2020, month=11, day=22)
        self.assertFalse(check_time_interval(start1, end1, start2, end2))

        start2 = datetime.datetime(year=2020, month=11, day=8)
        end2 = datetime.datetime(year=2020, month=11, day=11)
        self.assertTrue(check_time_interval(start1, end1, start2, end2))

        start2 = datetime.datetime(year=2020, month=11, day=12)
        end2 = datetime.datetime(year=2020, month=11, day=25)
        self.assertTrue(check_time_interval(start1, end1, start2, end2))

    def test_check_time_interval(self):
        pass