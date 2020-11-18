from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for, jsonify)
from gooutsafe.dao.reservation_manager import ReservationManager

from gooutsafe.models.reservation import Reservation
from datetime import datetime


reservation = Blueprint('reservation', __name__)


def create_reservation(restaurant_id):
    """This method is used to create a new reservation
        Linked to route /reservation/restaurants/{restaurant_id} [POST]
    Args:
        restaurant_id (int): univocal identifier of the restaurant
    Returns: 
        Invalid request if the creation of the reservation is not successful
        A json specifying the info needed to render the reservation page otherwise
    """
    pass   


def delete_reservation(reservation_id, restaurant_id):
    """This method is used to delete a reservation
        Linked to route /reservation/delete/{restaurant_id}/{reservation_id} [DELETE]
    Args:
        reservation_id (int): univocal identifier of the reservation
        restaurant_id (int): univocal identifier of the restaurant
    Returns: 
        Invalid request if the deletion of the reservation is not successful
        A json specifying the info needed to render the reservation page otherwise
    """
    pass

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
    pass

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
    pass


def edit_reservation(reservation_id, customer_id):
    """Allows the customer to edit a single reservation,
    if there's an available table within the opening hours
    of the restaurant.
    Linked to route reservation/edit/{restaurant_id}/{reservation_id} [PUT]

    Args:
        reservation_id (int): univocal identifier of the reservation
        customer_id (int): univocal identifier of the customer

    Returns:
        Invalid request for wrong data or if the reservation doesn't exists
        The json of the edited reservation
    """    
    pass


def confirm_reservation(restaurant_id, reservation_id):
    """
    This method is used to confirm reservation
    Linked to route /reservation/confirm/{restaurant_id}/{reservation_id} [PUT]
    Args:
        reservation_id (Integer): the restaurant id of the reservation
        restaurant_id (Integer): univocal identifier of the restaurant


    Returns:
        Invalid request if the reservation doesn't exists
        A success message
    """
    pass


# Helper Methods (TODO: refactoring)
def validate_reservation(restaurant, start_datetime, people_number):
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
    avg_stay = restaurant.avg_stay
    if avg_stay is None:
        end_datetime = start_datetime + timedelta(hours = 3)
    else:
        h_avg_stay = avg_stay//60
        m_avg_stay = avg_stay - (h_avg_stay*60)
        end_datetime = start_datetime + timedelta(hours=h_avg_stay, minutes=m_avg_stay)
    print(start_datetime)
    print(end_datetime)
    if check_rest_ava(restaurant, start_datetime, end_datetime):
        tables = TableManager.retrieve_by_restaurant_id(restaurant.id).order_by(Table.capacity)
        for table in tables:
            if table.capacity >= people_number:
                reservation_table = table
                table_reservations = ReservationManager.retrieve_by_table_id(table_id=table.id)
                if len(table_reservations) != 0:
                    for r in table_reservations:
                        old_start_datetime = r.start_time
                        old_end_datetime = r.end_time
                        print(old_start_datetime)
                        print(old_end_datetime)
                        if start_datetime.date() == old_start_datetime.date():
                            if check_time_interval(start_datetime.time(), end_datetime.time(),
                                                   old_start_datetime.time(), old_end_datetime.time()):
                                continue
                            else:
                                return reservation_table
                        else:
                            return reservation_table
                else:
                    return reservation_table
            else:
                continue
    return False


def check_rest_ava(restaurant, start_datetime, end_datetime):
    """
    This method check if the reservation datetime fall in the retaurant opening hours
    
    Args:
        restaurant (Restaurant): the restaurant in whitch we are booking
        start_datetime (datetime): reservation datetime 
        end_datetime (datetime): reservation end datetime

    Returns:
        [Boolean]: True if the restaurant is open or False if the restaurant is close
    """
    availabilities = restaurant.availabilities
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for ava in availabilities:
        ava_day = ava.day
        res_day = week_days[start_datetime.weekday()]
        if ava_day == res_day:
            if check_time_interval(start_datetime.time(), end_datetime.time(), ava.start_time, ava.end_time):
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
