import unittest
from datetime import datetime, timedelta

from faker import Faker

from .model_test import ModelTest


class TestReservation(ModelTest):
    faker = Faker('it_IT')

    @classmethod
    def setUpClass(cls):
        super(TestReservation, cls).setUpClass()

        from gooutsafe.models import reservation

        cls.reservation = reservation

    @staticmethod
    def generate_random_reservation(user_id=None, restaurant_id=None, start_time_mode=None):
        from gooutsafe.models.reservation import Reservation
        faker = Faker()

        if user_id is None:
            user_id = faker.random_int(min=1, max=50000)
        table_id = faker.random_int(min=1, max=50000)
        if restaurant_id is None:
            restaurant_id = faker.random_int(min=1, max=50000)
        people_number = faker.random_int(min=0,max=10)
        if start_time_mode == 'valid_past_contagion_time':
            start_time = faker.date_time_between_dates(datetime.utcnow()-timedelta(days=14), datetime.utcnow())
        elif start_time_mode == 'valid_future_contagion_time':
            start_time = faker.date_time_between('now', '+14d')
        else:
            start_time = TestReservation.faker.date_time_between('now', '+6w')
        reservation = Reservation(
            user_id = user_id,
            table_id = table_id,
            restaurant_id = restaurant_id,
            people_number = people_number,
            start_time = start_time
        )

        return reservation, (user_id, table_id, restaurant_id, start_time)

    @staticmethod
    def assertEqualReservations(r1, r2):
        t = unittest.FunctionTestCase(TestReservation)
        t.assertEqual(r1.user_id, r2.user_id)
        t.assertEqual(r1.table_id, r2.table_id)
        t.assertEqual(r1.restaurant_id, r2.restaurant_id)
        t.assertEqual(r1.people_number, r2.people_number)
        t.assertEqual(r1.start_time, r2.start_time)

    def test_reservation_init(self):
        reservation, (user_id, table_id, restaurant, start_time) = TestReservation.generate_random_reservation()
        self.assertEqual(reservation.user_id, user_id)
        self.assertEqual(reservation.table_id, table_id)
        self.assertEqual(reservation.start_time, start_time) 
        self.assertEqual(reservation.end_time, start_time+timedelta(hours=reservation.MAX_TIME_RESERVATION))

    """    
    def test_set_end_time_by_avg_stay(self):
        reservation, _ = TestReservation.generate_random_reservation()
        restaurant = reservation.restaurant
        restaurant.set_avg_stay(240)
        end_time = reservation.start_time + timedelta(hours=4)
        reservation.set_end_time_by_avg_stay(restaurant.avg_stay)
        self.assertEqual(reservation.end_time, end_time)
    """

    # def test_set_start_time(self):
    #     reservation, _ = TestReservation.generate_random_reservation()
    #     wrong_start_time = TestReservation.faker.date_time_between('-4y','now')
    #     with self.assertRaises(ValueError):
    #             reservation.set_start_time(wrong_start_time)

    def test_set_user(self):
        reservation,_= TestReservation.generate_random_reservation()
        user_id = self.faker.random_int(min=1, max=50000)
        reservation.set_user_id(user_id)
        self.assertEquals(user_id, reservation.user_id)

    def test_set_table(self):        
        reservation, _ = TestReservation.generate_random_reservation()
        table_id = self.faker.random_int(min=1, max=50000)
        reservation.set_table_id(table_id)
        self.assertEqual(table_id, reservation.table_id)

    def test_set_restaurant(self):
        reservation, _ = TestReservation.generate_random_reservation()
        restaurant_id  = self.faker.random_int(min=1, max=50000)
        reservation.set_restaurant_id(restaurant_id)
        self.assertEqual(restaurant_id, reservation.restaurant_id)


    def test_set_people_number(self):
        reservation, _ = TestReservation.generate_random_reservation()
        people_number = self.faker.random_int(min=0, max=10)
        reservation.set_people_number(people_number)
        self.assertEqual(people_number, reservation.people_number)

    def test_check_time(self):
        reservation, _ = TestReservation.generate_random_reservation()
        start_time = self.faker.date_time_between('now', '+14d')
        end_time = self.faker.date_time_between('-3d', 'now')
        with self.assertRaises(ValueError):
            reservation.check_time(start_time, end_time)

    def test_set_end_time(self):
        reservation, _ = TestReservation.generate_random_reservation()
        wrong_endtime = self.faker.date_time_between_dates(
            datetime_start=reservation.start_time - timedelta(days=3), 
            datetime_end=reservation.start_time
            )
        with self.assertRaises(ValueError):
                reservation.set_end_time(wrong_endtime)

    def test_set_is_confirmed(self):
        reservation, _ = TestReservation.generate_random_reservation()
        reservation.set_is_confirmed()
        self.assertTrue(reservation.is_confirmed)