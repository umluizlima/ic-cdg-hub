"""Reservations API.

This module maps the API endpoints for the Reservation data model, implementing
the POST, GET, PUT and DELETE http methods for its CRUD operations,
respectively.

Endpoints
    GET - /reservations - return the collection of all reservations.
    GET - /reservations/<id> - return a reservation with given id number.
    POST - /reservations - register a new reservation.
    PUT - /reservations/<id> - modify a reservation with given id number.
    DELETE - /reservations/<id> - remove a reservation with id number.

"""
from datetime import datetime as dt
from flask import (
    jsonify, request
)
from app.model import (
    db, Reservation, User, Thirdparty
)
from app.controller.errors import (
    bad_request, internal_server, not_found
)
from app.controller.api import api


# Create
@api.route('/reservations', methods=['POST'])
def create_reservation():
    """Create new reservation."""
    data = request.get_json() or {}

    error = Reservation.check_data(data=data, new=True)
    if 'user_id' in data and data['user_id'] is not None and \
            User.query.get(data['user_id']) is None:
        error = 'usuário não existe'
    if 'thirdparty_id' in data and data['thirdparty_id'] is not None and \
            Thirdparty.query.get(data['thirdparty_id']) is None:
        error = 'terceiro não existe'
    if error:
        return bad_request(error)

    print(data)

    reservation = Reservation()
    reservation.from_dict(data)

    try:
        db.session.add(reservation)
        db.session.commit()
    except Exception:
        return internal_server()

    return jsonify(reservation.to_dict()), 201


# Read
@api.route('/reservations', methods=['GET'])
def get_reservations():
    """Return list of reservations."""
    return jsonify(
        [reservation.to_dict() for reservation in Reservation.query.all()]
    )


# Read
@api.route('/reservations/<int:id>', methods=['GET'])
def get_reservation(id: int):
    """Return reservation with given id."""
    reservation = Reservation.query.filter_by(id=id).first()
    if reservation is None:
        return not_found('reserva não encontrada')
    return jsonify(reservation.to_dict())


@api.route('/reservations/<int:id>', methods=['PUT'])
def update_reservation(id: int):
    """Update given reservation, if exists."""
    reservation = Reservation.query.filter_by(id=id).first()
    if reservation is None:
        return not_found('reserva não encontrada')

    data = request.get_json() or {}

    error = Reservation.check_data(data=data)
    if 'user_id' in data and data['user_id'] is not None and \
            User.query.get(data['user_id']) is None:
        error = 'usuário não existe'
    if 'thirdparty_id' in data and data['thirdparty_id'] is not None and \
            Thirdparty.query.get(data['thirdparty_id']) is None:
        error = 'terceiro não existe'
    if error:
        return bad_request(error)

    reservation.from_dict(data)
    try:
        db.session.commit()
    except Exception:
        return internal_server()

    return jsonify(reservation.to_dict())


# Delete
@api.route('/reservations/<int:id>', methods=['DELETE'])
def delete_reservation(id: int):
    """Delete given reservation, if exists."""
    reservation = Reservation.query.filter_by(id=id).first()
    if reservation is None:
        return not_found('reserva não encontrada')

    try:
        db.session.delete(reservation)
        db.session.commit()
    except Exception:
        return internal_server()

    return '', 204