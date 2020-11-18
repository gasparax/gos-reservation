from datetime import datetime, timedelta
from random import randint

from faker import Faker

from .dao_test import DaoTest


class TestReservationManager(DaoTest):
    faker = Faker('it_IT')

    @classmethod
    def setUpClass(cls):
        super(TestReservationManager, cls).setUpClass()

        from tests.models.test_reservation import TestReservation
        cls.test_reservation = TestReservation

        from gooutsafe.dao import reservation_manager
        cls.reservation_manager = reservation_manager.ReservationManager

    
    def test_create_reservation(self):
        reservation1, _ = self.test_reservation.generate_random_reservation()
        self.reservation_manager.create_reservation(reservation=reservation1)
        reservation2 = self.reservation_manager.retrieve_by_id(id_=reservation1.id)
        self.test_reservation.assertEqualReservations(reservation1, reservation2)

    def test_delete_reservation(self):
        base_reservation, _ = self.test_reservation.generate_random_reservation()
        self.reservation_manager.create_reservation(reservation=base_reservation)
        self.reservation_manager.delete_reservation(base_reservation)
        self.assertIsNone(self.reservation_manager.retrieve_by_id(base_reservation.id))

    def test_delete_reservation_by_id(self):
        base_reservation, _ = self.test_reservation.generate_random_reservation()
        self.reservation_manager.create_reservation(reservation=base_reservation)
        self.reservation_manager.delete_reservation_by_id(base_reservation.id)
        self.assertIsNone(self.reservation_manager.retrieve_by_id(base_reservation.id))

    def test_update_reservation(self):
        base_reservation, _ = self.test_reservation.generate_random_reservation()
        self.reservation_manager.create_reservation(reservation=base_reservation)
        base_reservation.set_people_number(self.faker.random_int(min=0,max=15))
        start_time = self.faker.date_time_between('now','+6w')
        base_reservation.set_start_time(start_time)
        updated_reservation = self.reservation_manager.retrieve_by_id(id_=base_reservation.id)
        self.test_reservation.assertEqualReservations(base_reservation, updated_reservation)

    def test_retrieve_by_user_id(self):
        reservation, _ = self.test_reservation.generate_random_reservation()
        user_id = reservation.user_id
        self.reservation_manager.create_reservation(reservation=reservation)
        retrieved_reservation = self.reservation_manager.retrieve_by_customer_id(user_id=user_id)
        for res in retrieved_reservation:
            self.test_reservation.assertEqualReservations(reservation, res)

    def test_retrieve_by_restaurant_id(self):
        reservation, _ = self.test_reservation.generate_random_reservation()
        restaurant_id = reservation.restaurant_id
        print(restaurant_id)
        self.reservation_manager.create_reservation(reservation=reservation)
        retrieved_reservation = self.reservation_manager.retrieve_by_restaurant_id(restaurant_id=restaurant_id)
        for res in retrieved_reservation:
            self.test_reservation.assertEqualReservations(reservation, res)
    
    def test_retrieve_by_table_id(self):
        reservation, _ = self.test_reservation.generate_random_reservation()
        table_id = reservation.table_id
        self.reservation_manager.create_reservation(reservation=reservation)
        retrieved_reservation = self.reservation_manager.retrieve_by_table_id(table_id=table_id)
        for res in retrieved_reservation:
            self.test_reservation.assertEqualReservations(reservation, res)
    
    def test_retrieve_by_customer_id(self):
        reservation, _ = self.test_reservation.generate_random_reservation()
        customer_id = reservation.user_id
        self.reservation_manager.create_reservation(reservation=reservation)
        retrieved_reservation = self.reservation_manager.retrieve_by_customer_id(user_id=customer_id)
        for res in retrieved_reservation:
            self.test_reservation.assertEqualReservations(reservation, res)

    def test_single_retrieve_by_customer_id_in_last_14_days(self):
        customer_id = self.faker.random_int(min=0,max=5000)
        valid_reservation, _ = self.test_reservation.generate_random_reservation(user_id=customer_id)
        self.reservation_manager.create_reservation(reservation=valid_reservation)
        invalid_reservation, _ = self.test_reservation.generate_random_reservation(user_id=customer_id)
        invalid_reservation.set_start_time(datetime.utcnow() - timedelta(days=randint(15, 100)))
        self.reservation_manager.create_reservation(reservation=invalid_reservation)
        retrieved_reservation = self.reservation_manager.retrieve_by_customer_id_in_last_14_days(user_id=customer_id)
        for res in retrieved_reservation:
            self.test_reservation.assertEqualReservations(valid_reservation, res)

    def test_multiple_retrieve_by_customer_id_in_last_14_days(self):
        customer_id = self.faker.random_int(min=0,max=5000)
        valid_reservations = []
        for _ in range(randint(2, 10)):
            valid_reservation, _ = self.test_reservation.generate_random_reservation(user_id=customer_id, start_time_mode='valid_past_contagion_time')
            self.reservation_manager.create_reservation(reservation=valid_reservation)
            valid_reservations.append(valid_reservation)
        for _ in range(randint(2, 10)):
            invalid_reservation, _ = self.test_reservation.generate_random_reservation(user_id=customer_id)
            invalid_reservation.set_start_time(datetime.utcnow() - timedelta(days=randint(15, 100)))
            self.reservation_manager.create_reservation(reservation=invalid_reservation)
        retrieved_reservations = self.reservation_manager.retrieve_by_customer_id_in_last_14_days(user_id=customer_id)
        for retrieved, valid in zip(retrieved_reservations, valid_reservations):
            self.test_reservation.assertEqualReservations(valid, retrieved)

    def test_retrieve_by_customer_id_in_future(self):
        customer_id = self.faker.random_int(min=0,max=5000)
        valid_reservations = []
        for _ in range(randint(2, 10)):
            valid_reservation, _ = self.test_reservation.generate_random_reservation(user_id=customer_id, start_time_mode='valid_future_contagion_time')
            self.reservation_manager.create_reservation(reservation=valid_reservation)
            valid_reservations.append(valid_reservation)
        for _ in range(randint(2, 10)):
            invalid_reservation, _ = self.test_reservation.generate_random_reservation(user_id=customer_id)
            invalid_reservation.set_start_time(datetime.utcnow() - timedelta(days=randint(1, 100)))
            self.reservation_manager.create_reservation(reservation=invalid_reservation)
        retrieved_reservations = self.reservation_manager.retrieve_by_customer_id_in_future(user_id=customer_id)
        for retrieved, valid in zip(retrieved_reservations, valid_reservations):
            self.test_reservation.assertEqualReservations(valid, retrieved)

    def test_retrieve_all_contact_reservation_by_id(self):
        from gooutsafe.models.reservation import Reservation
        restaurant = self.faker.random_int(min=0,max=5000)
        start_time_positive = datetime(year=2020, month=11, day=2, hour=11)
        end_time_positive = start_time_positive + timedelta(Reservation.MAX_TIME_RESERVATION)
        contacted_users = []
        for _ in range(0, self.faker.random_int(min=2, max=10)):
            table = self.faker.random_int(min=0,max=5000)
            start_time = datetime(year=2020, month=11, day=2, hour=self.faker.random_int(min=11,max=13), minute=self.faker.random_int(min=0,max=59))
            contacted_user = self.faker.random_int(min=0,max=5000)
            contacted_users.append(contacted_user)
            reservation = Reservation(contacted_user, table, restaurant, 1, start_time)
            self.reservation_manager.create_reservation(reservation)

        table1 = restaurant = self.faker.random_int(min=5000,max=10000)
        positive_user = self.faker.random_int(min=5000,max=10000)
        positive_reservation = Reservation(positive_user, table1, restaurant, 1, start_time_positive)
        self.reservation_manager.create_reservation(positive_reservation)
        retrieved_contacted_reservations = self.reservation_manager.retrieve_all_contact_reservation_by_id(positive_reservation.id)
        retrieved_contacted_users = []
        for res in retrieved_contacted_reservations:
            retrieved_contacted_users.append(res.user)
        retrieved_contacted_users.sort(key=lambda positive_user: positive_user)
        contacted_users.sort(key=lambda positive_user: positive_user)
        for retrieved_contacted_user, contacted_user in zip(retrieved_contacted_users, contacted_users):
            self.test_user.assertUserEquals(contacted_user, retrieved_contacted_user)

    def test_retrieve_by_date_and_time(self):
        from gooutsafe.models.reservation import Reservation
        restaurant_id = self.faker.random_int(min=0,max=5000)
        start_interval = datetime(year=2020, month=11, day=30, hour=0)
        end_interval = start_interval + timedelta(hours=23)
        reservations = []
        for i in range(0, self.faker.random_int(min=1, max=10)):
            table = self.faker.random_int(min=0,max=5000)
            start_time = datetime(year=2020, month=11, day=30, hour=i+1)
            user = self.faker.random_int(min=0,max=5000)
            reservation = Reservation(user, table, restaurant_id, 1, start_time)
            reservations.append(reservation)
            self.reservation_manager.create_reservation(reservation)
        retreived_res = self.reservation_manager.retrieve_by_date_and_time(restaurant_id, start_interval, end_interval)
        self.assertListEqual(reservations, retreived_res)