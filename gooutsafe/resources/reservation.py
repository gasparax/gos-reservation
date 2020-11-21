from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for, jsonify)
from gooutsafe.dao.reservation_manager import ReservationManager

from gooutsafe.models.reservation import Reservation
from datetime import time, timedelta, datetime


reservation = Blueprint('reservation', __name__)


def create_reservation():
    """This method is used to create a new reservation
        Linked to route /reservation/ [POST]

    Returns: 
        Invalid request if the creation of the reservation is not successful
        A json specifying the info needed to render the reservation page otherwise
    """
    try:
        json_data = request.get_json()
        user_id = json_data['user_id']
        restaurant_id = json_data['restaurant_id']
        start_time = json_data['start_time']
        people_number = json_data['people_number']
        tables = json_data['tables']
        times = json_data['times']
        table_id, start_time = validate_reservation(tables, times, start_time, people_number)
        if table_id is False:
            raise ValueError 
        reservation = Reservation(user_id, table_id, restaurant_id, people_number, start_time) 
        ReservationManager.create_reservation(reservation)
    except Exception as e:
        return jsonify({'status': 'Bad request',
                        'message': 'The data provided were not correct.\n' + str(e)
                        }), 400
    
    return jsonify({'status': 'Success',
                    'message': 'Reservation succesfully added'
                    }), 200   


def delete_reservation(reservation_id):
    """This method is used to delete a reservation
        Linked to route /reservation/{reservation_id} [DELETE]
    Args:
        reservation_id (int): univocal identifier of the reservation
    Returns: 
        Invalid request if the deletion of the reservation is not successful
        A json specifying the info needed to render the reservation page otherwise
    """
    try:
        ReservationManager.delete_reservation_by_id(reservation_id)
    except Exception as e:
        return jsonify({'message': 'Error during avg stay updating\n' + str(e),
                        'status': 'Internal Server Error'
                        }), 500
    return jsonify({'message': 'Restaurant successfully deleted'
                    }), 200



def get_all_reservation_restaurant(restaurant_id):
    """Returns the whole list of reservations, given a restaurant.
    It also gives to the operator the opportunity to filter reservations
    by date, so it's possible to count people.
    Linked to route /reservation/restaurant/{restaurant_id} [GET]

    Args:
        restaurant_id (int): univocal identifier of the restaurant

    Returns:
        Invalid request if restaurant doesn't exists
        The list of json of the reservations.
    """
    reservations = ReservationManager.retrieve_by_restaurant_id(restaurant_id)
    reservations = [reservation.serialize() for reservation in reservations]
    if not reservations:
        return jsonify({'message': 'No reservation for this restaurant\n',
                'status': 'Bad Request'
                }), 400
    return jsonify({'status': 'Success',
                    'message': 'The reservations were correctly loaded',
                    'reservations': reservations
                    }), 200
    


def get_all_reservation_customer(customer_id):
    """Returns the whole list of reservations, given a customer.
    It also gives to the operator the opportunity to filter reservations
    by date, so it's possible to count people.
    Linked to route /reservation/customer/{customer_id} [GET]

    Args:
        customer_id (int): univocal identifier of the customer

    Returns:
        Invalid request if customer doesn't exists
        The list of json of the reservations.
    """
    reservations = ReservationManager.retrieve_by_customer_id(customer_id)
    reservations = [reservation.serialize() for reservation in reservations]
    if not reservations:
        return jsonify({'message': 'No reservation for this customer\n',
                'status': 'Bad Request'
                }), 400
    return jsonify({'status': 'Success',
                    'message': 'The reservations were correctly loaded',
                    'reservations': reservations
                    }), 200

def edit_reservation(reservation_id):
    """Allows the customer to edit a single reservation,
    if there's an available table within the opening hours
    of the restaurant.
    Linked to route reservation/{reservation_id} [PUT]

    Args:
        reservation_id (int): univocal identifier of the reservation
        restaurant_id (int): univocal identifier of the restaurant

    Returns:
        Invalid request for wrong data or if the reservation doesn't exists
        The json of the edited reservation
    """    
    try:
        json_data = request.get_json()
        user_id = json_data['user_id']
        start_time = json_data['start_time']
        people_number = json_data['people_number']
        tables = json_data['tables']
        times = json_data['times']
        old_reservation = ReservationManager.retrieve_by_id(reservation_id)
        restaurant_id = old_reservation.restaurant_id
        ReservationManager.delete_reservation(old_reservation)
        table_id, start_time = validate_reservation(tables, times, start_time, people_number)
        if table_id is False:
            ReservationManager.create_reservation(old_reservation)
            raise ValueError
        reservation = Reservation(user_id, table_id, restaurant_id, people_number, start_time) 
        ReservationManager.create_reservation(reservation)
    except Exception as e:
        return jsonify({'status': 'Bad request',
                        'message': 'The data provided were not correct.\n' + str(e)
                        }), 400
    
    return jsonify({'status': 'Success',
                    'message': 'Reservation succesfully added'
                    }), 200  

def confirm_reservation(reservation_id):
    """
    This method is used to confirm reservation
    Linked to route /reservation/confirm/{reservation_id} [PUT]
    Args:
        reservation_id (Integer): the restaurant id of the reservation
        restaurant_id (Integer): univocal identifier of the restaurant


    Returns:
        Invalid request if the reservation doesn't exists
        A success message
    """
    reservation = ReservationManager.retrieve_by_id(reservation_id)
    if reservation is None:
        return jsonify({'status': 'Bad Request',
                        'message': 'There is not reservation with this id'
        }), 400
    reservation.set_is_confirmed()
    ReservationManager.update_reservation(reservation)
    return jsonify({'status': 'Success',
                'message': 'Reservation succesfully confirmed'
                }), 200  



# Helper Methods (TODO: avg_stay check)
def validate_reservation(tables, times, start_datetime, people_number):
    """
    This method checks if the new reservation overlap with other already 
    present for the restaurant.
    Args:
        restaurant (Restaurant): the reservation restaurant
        start_datetime (datetime): the datetime of the reservation
        people_number (Integer): number of people declered in the reservation

    Returns:
        Teble, Boolean: false in case there are overlap or a table if the restaurant is open and there aren't overlap
    """
    start_datetime = datetime.strptime(start_datetime,"%Y-%m-%d %H:%M:%S")
    end_datetime = start_datetime + timedelta(hours = 3)
    if not check_rest_ava(times, start_datetime):
        print('RISTORANTE CHIUSO')
        return False
    valid_tables = [table for table in tables if table.get('capacity') >= people_number]
    for table in valid_tables:
        reservation_table = table
        print("CONTROLLO PRENOTAZIONI PER IL TAVOLO " + str(table.get('id')))
        table_reservations = ReservationManager.retrieve_by_date_time_table(table.get('id'), start_datetime, end_datetime)
        print("PRENOTAZIONI PRESENTI")
        print(table_reservations)
        if len(table_reservations) != 0:
            print('TAVOLO OCCUPATO')
            continue
            #return False
        else:
            print('TAVOLO DISPONIBILE')
            print('TAVOLO N ' + str(reservation_table.get('id')))
            return reservation_table.get('id'), start_datetime
    return False
    



def check_rest_ava(restaurant_avas, start_datetime):
    """
    This method check if the reservation datetime fall in the retaurant opening hours
    
    Args:
        restaurant (Restaurant): the restaurant in whitch we are booking
        start_datetime (datetime): reservation datetime 
        end_datetime (datetime): reservation end datetime

    Returns:
        [Boolean]: True if the restaurant is open or False if the restaurant is close
    """
    end_datetime = start_datetime + timedelta(hours = 3)
    availabilities = restaurant_avas
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for ava in availabilities:
        ava_day = ava.get('day')
        res_day = week_days[start_datetime.weekday()]
        open_time = datetime.strptime(ava.get('start_time'), "%H:%M:%S")
        close_time = datetime.strptime(ava.get('end_time'), "%H:%M:%S")
        if ava_day == res_day:
            if check_time_interval(start_datetime.time(), end_datetime.time(), open_time.time(), close_time.time()):
                return True
    return False


def check_time_interval(start_time1, end_time1, start_time2, end_time2):
    """
    This method check if start_time1 and end_time1 overlap
    the intervall between startime2 and end_time2

    Args:
        start_time1 (datetime)
        end_time1 (datetime)
        start_time2 (datetime)
        end_time2 (datetime)

    Returns:
        Boolean
    """
    if start_time1 >= start_time2 and start_time1 < end_time2:
        return True
    elif end_time1 > start_time2 and end_time1 <= end_time2:
        return True
    return False
