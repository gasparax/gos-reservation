from .resource_test import ResourceTest
from faker import Faker
from datetime import time, timedelta, datetime



class ReservationResTest(ResourceTest):
    faker = Faker()


    @classmethod
    def setUpClass(cls):
        super(ReservationResTest, cls).setUpClass()


    def test_create_reservation_400(self):
        tables = []
        tables.append({'id': 1, 'capacity': 2, 'restaurant_id':1})
        times = []
        times.append({'id': 1, 
                'start_time': '10:00:00', 
                'end_time': '15:00:00', 
                'day':'Monday', 
                'restaurant_id': 1})
        start_datetime = '2020-11-30 19:54:15'
        people_number = 1
        data = {'user_id': 1,
                'start_time': start_datetime,
                'people_number': people_number,
                'tables': tables,
                'times': times}
        restaurant_id = 1
        self.reservation_manager.delete_all_restaurant_reservation(restaurant_id)
        response = self.client.post('/reservation/restaurants/create/' + str(restaurant_id), json=data)
        json_response = response.json
        assert response.status_code == 400

    def test_create_reservation_200(self):
        tables = []
        tables.append({'id': 1, 'capacity': 2, 'restaurant_id':1})
        times = []
        times.append({'id': 1, 
                'start_time': '10:00:00', 
                'end_time': '17:00:00', 
                'day':'Monday', 
                'restaurant_id': 1})
        start_datetime = '2020-11-30 16:00:00'
        people_number = 1
        data = {'user_id': 1,
                'start_time': start_datetime,
                'people_number': people_number,
                'tables': tables,
                'times': times}
        restaurant_id = 1
        self.reservation_manager.delete_all_restaurant_reservation(restaurant_id)
        response = self.client.post('/reservation/restaurants/create/' + str(restaurant_id), json=data)
        json_response = response.json
        assert response.status_code == 200  


    def test_delete_reservation_500(self):
        response = self.client.delete('/reservation/delete/' + str(0) + '/' + str(0))
        assert response.status_code == 500


    def test_delete_reservation_200(self):
        reservation, restaurant_id = self.add_reservation()
        reservation_id = reservation.id
        response = self.client.delete('/reservation/delete/' + str(restaurant_id) + '/' + str(reservation_id))
        assert response.status_code == 200

    def test_get_all_reservation_restaurant_400(self):
        response = self.client.get('/reservation/restaurant/' + str(0))
        assert response.status_code == 400

    def test_get_all_reservation_restaurant_200(self):
        reservation, restaurant_id = self.add_reservation()
        reservation_id = reservation.id
        response = self.client.get('/reservation/restaurant/' + str(restaurant_id))
        assert response.status_code == 200
        
    def test_get_all_reservation_customer_400(self):
        response = self.client.get('/reservation/customer/' + str(0))
        assert response.status_code == 400

    def test_get_all_reservation_customer_200(self):
        reservation, _ = self.add_reservation()
        reservation_id = reservation.id
        customer_id = reservation.user_id
        response = self.client.get('/reservation/customer/' + str(customer_id))
        assert response.status_code == 200

    def test_edit_reservation_400(self):
        tables = []
        tables.append({'id': 1, 'capacity': 2, 'restaurant_id':1})
        times = []
        times.append({'id': 1, 
                'start_time': '10:00:00', 
                'end_time': '15:00:00', 
                'day':'Monday', 
                'restaurant_id': 1})
        start_datetime = '2020-11-30 19:54:15'
        people_number = 1
        data = {'user_id': 1,
                'start_time': start_datetime,
                'people_number': people_number,
                'tables': tables,
                'times': times}
        reservation, restaurant_id = self.add_reservation()
        reservation_id = reservation.id
        response = self.client.put('/reservation/edit/' + str(restaurant_id) + '/' + str(reservation_id), json=data)
        json_response = response.json
        assert response.status_code == 400

    def test_edit_reservation_200(self):
        tables = []
        tables.append({'id': 1, 'capacity': 2, 'restaurant_id':1})
        times = []
        times.append({'id': 1, 
                'start_time': '10:00:00', 
                'end_time': '17:00:00', 
                'day':'Monday', 
                'restaurant_id': 1})
        start_datetime = '2020-11-30 16:00:00'
        people_number = 2
        data = {'user_id': 1,
                'start_time': start_datetime,
                'people_number': people_number,
                'tables': tables,
                'times': times}
        self.reservation_manager.delete_all_restaurant_reservation(1)
        old_reservation, _ = self.test_reservation.generate_random_reservation(restaurant_id=1)
        self.reservation_manager.create_reservation(old_reservation)
        reservation_id = old_reservation.id
        response = self.client.put('/reservation/edit/' + str(1) + '/' + str(reservation_id), json=data)
        assert response.status_code == 200
        

    def test_confirm_reservation_400(self):
        response = self.client.put('/reservation/confirm/' + str(1) + '/' + str(0))
        assert response.status_code == 400


    def test_confirm_reservation_200(self):
        reservation, restaurant_id = self.add_reservation()
        reservation_id = reservation.id
        print(reservation_id)
        response = self.client.put('/reservation/confirm/' + str(restaurant_id) + '/' + str(reservation_id))
        assert response.status_code == 200


# Tests on helper methods (TODO: refactoring)

    def test_validate_reservation_restaurant_close(self):
        from gooutsafe.resources.reservation import validate_reservation
        #Close restaurant
        tables = {'id': 1, 'capacity': 2, 'restaurant_id':1}
        times = []
        times.append({'id': 1, 
                'start_time': '10:00:00', 
                'end_time': '15:00:00', 
                'day':'Monday', 
                'restaurant_id': 1})
        start_datetime = '2020-11-30 19:54:15'
        people_number = 4
        self.assertFalse(validate_reservation(tables, times, start_datetime, people_number))
    
    def test_validate_reservation_no_table(self):
        from gooutsafe.resources.reservation import validate_reservation
        # No tables
        tables = {}
        times = []
        times.append({'id': 1, 
                'start_time': '10:00:00', 
                'end_time': '15:00:00', 
                'day':'Monday', 
                'restaurant_id': 1})
        start_datetime = '2020-11-23 12:54:15'
        people_number = 2
        self.assertFalse(validate_reservation(tables, times, start_datetime, people_number))

    def test_validate_reservation_small_table(self):
        from gooutsafe.resources.reservation import validate_reservation
        #Small Tables
        tables = []
        tables.append({'id': 1, 'capacity': 2, 'restaurant_id':1})
        times = []
        times.append({'id': 1, 
                'start_time': '10:00:00', 
                'end_time': '15:00:00', 
                'day':'Monday', 
                'restaurant_id': 1})
        start_datetime = '2020-11-30 12:54:15'
        people_number = 4
        self.assertFalse(validate_reservation(tables, times, start_datetime, people_number))

    def test_validate_reservation_occupied_table(self):
        from gooutsafe.resources.reservation import validate_reservation
        from gooutsafe.models.reservation import Reservation
        #Occupied tables
        start = datetime.strptime('2020-11-30 12:00:00', "%Y-%m-%d %H:%M:%S")
        reservation = Reservation(1, 1, 1, 2, start)
        self.reservation_manager.create_reservation(reservation)
        tables = []
        tables.append({'id': 1, 'capacity': 2, 'restaurant_id':1})
        times = []
        times.append({'id': 1, 
                'start_time': '10:00:00', 
                'end_time': '15:00:00', 
                'day':'Monday', 
                'restaurant_id': 1})
        start_datetime = '2020-11-30 12:00:00'
        people_number = 1
        self.assertFalse(validate_reservation(tables, times, start_datetime, people_number))
        self.reservation_manager.delete_reservation(reservation)

    def test_validate_reservation_success(self):
        from gooutsafe.resources.reservation import validate_reservation
        tables = []
        tables.append({'id': 1, 'capacity': 2, 'restaurant_id':1})
        times = []
        times.append({'id': 1, 
                'start_time': '10:00:00', 
                'end_time': '17:00:00', 
                'day':'Monday', 
                'restaurant_id': 1})
        start_datetime = '2020-11-30 16:00:00'
        people_number = 1
        self.reservation_manager.delete_all_restaurant_reservation(1)
        retrieved_table_id, _ = validate_reservation(tables, times, start_datetime, people_number)
        print(retrieved_table_id)
        
        self.assertEqual(retrieved_table_id, 1)

    def test_validate_reservation_success_more_table(self):
        from gooutsafe.resources.reservation import validate_reservation
        from gooutsafe.models.reservation import Reservation
        start = datetime.strptime('2020-11-30 12:00:00', "%Y-%m-%d %H:%M:%S")
        reservation = Reservation(1, 1, 1, 2, start)
        self.reservation_manager.create_reservation(reservation)
        tables = []
        tables.append({'id': 1, 'capacity': 2, 'restaurant_id':1})
        tables.append({'id': 2, 'capacity': 2, 'restaurant_id':1})
        times = []
        times.append({'id': 1, 
                'start_time': '10:00:00', 
                'end_time': '17:00:00', 
                'day':'Monday', 
                'restaurant_id': 1})
        start_datetime = '2020-11-30 12:00:00'
        people_number = 1
        retrieved_table_id, _ = validate_reservation(tables, times, start_datetime, people_number)
        self.assertEqual(retrieved_table_id, 2)
        self.reservation_manager.delete_reservation(reservation)

    def test_check_time_interval(self):
        from gooutsafe.resources.reservation import check_time_interval
        start1 = datetime(year=2020, month=11, day=9)
        end1 = datetime(year=2020, month=11, day=15)
        start2 = datetime(year=2020, month=11, day=20)
        end2 = datetime(year=2020, month=11, day=22)
        self.assertFalse(check_time_interval(start1, end1, start2, end2))

        start2 = datetime(year=2020, month=11, day=8)
        end2 = datetime(year=2020, month=11, day=11)
        self.assertTrue(check_time_interval(start1, end1, start2, end2))

        start2 = datetime(year=2020, month=11, day=12)
        end2 = datetime(year=2020, month=11, day=25)
        self.assertTrue(check_time_interval(start1, end1, start2, end2))

    def test_check_time_interval_false(self):
        from gooutsafe.resources.reservation import check_rest_ava
        times = []
        times.append({'id': 1, 
                'start_time': '10:00:00', 
                'end_time': '17:00:00', 
                'day':'Monday', 
                'restaurant_id': 1})
        start = datetime.strptime('2020-11-30 20:00:00', "%Y-%m-%d %H:%M:%S")
        check_rest_ava(times, start)
        start = datetime.strptime('2020-11-29 20:00:00', "%Y-%m-%d %H:%M:%S")
        check_rest_ava(times, start)

    def test_check_time_interval_true(self):
        from gooutsafe.resources.reservation import check_rest_ava
        times = []
        times.append({'id': 1, 
                'start_time': '10:00:00', 
                'end_time': '17:00:00', 
                'day':'Monday', 
                'restaurant_id': 1})
        start = datetime.strptime('2020-11-30 12:00:00', "%Y-%m-%d %H:%M:%S")
        check_rest_ava(times, start)
    

    #Helper Methods
    def add_reservation(self):
        reservation, _  = self.test_reservation.generate_random_reservation()
        restaurant_id =  reservation.restaurant_id
        self.reservation_manager.create_reservation(reservation)
        return reservation, restaurant_id

