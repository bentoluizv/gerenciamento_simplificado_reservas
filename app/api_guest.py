from flask import Blueprint, jsonify, make_response, request
from markupsafe import escape
from pydantic import ValidationError

from app.data.dao.GuestDAO import GuestDAO
from app.data.database.db import get_db
from app.data.repositories.GuestRepository import GuestRepository
from app.entity.Guests import Guest
from app.errors.AlreadyExists import AlreadyExistsError
from app.errors.NotFoundError import NotFoundError

bp = Blueprint("api_guest", __name__, url_prefix="/api/hospedes")


@bp.get("")
def get_guests():
    db = get_db()
    dao = GuestDAO(db)
    respository = GuestRepository(dao)

    try:
        guests = [guest.to_dict() for guest in respository.find_many()]
        return make_response(jsonify(guests), 200)

    except ValidationError as err:
        return make_response(jsonify(err.errors), 500)


@bp.post("/cadastro")
def create_guest():
    db = get_db()
    dao = GuestDAO(db)
    repository = GuestRepository(dao)
    guest = request.get_json()
    try:
        guest = Guest.from_dict(guest)
        repository.insert(guest)
        return make_response("CREATED", 201)

    except KeyError as err:
        return make_response(
            jsonify({"message": f"validation error: {err} is not a valid cpf"}), 400
        )

    except ValidationError as err:
        return make_response(jsonify({"message": err.title}), 400)

    except AlreadyExistsError as err:
        return make_response(jsonify({"message": err.message}), err.status)


@bp.get("/<document>")
def get_guest(document):
    db = get_db()
    dao = GuestDAO(db)
    repository = GuestRepository(dao)
    url_param = escape(document)

    try:
        guest = repository.findBy("document", str(url_param))
        return make_response(guest.to_json(), 200)

    except NotFoundError as err:
        return make_response(jsonify({"message": err.message}), err.status)


@bp.delete("/<document>")
def delete_guest(document):
    db = get_db()
    dao = GuestDAO(db)
    repository = GuestRepository(dao)
    url_param = escape(document)

    try:
        repository.delete(document=str(url_param))
        return make_response("DELETED", 200)

    except NotFoundError as err:
        return make_response(jsonify({"message": err.message}), err.status)


@bp.put("")
def update_guest():
    db = get_db()
    dao = GuestDAO(db)
    repository = GuestRepository(dao)
    raw = request.get_json()
    data = {
        "document": raw["document"],
        "name": raw["name"],
        "surname": raw["surname"],
        "phone": raw["phone"],
        "country": raw["country"],
    }

    try:
        guest = Guest.from_dict(data)
        repository.update(guest)
        return make_response("UPDATED", 201)

    except ValidationError as err:
        return make_response(jsonify({"message": err.title}), 400)

    except NotFoundError as err:
        return make_response(jsonify({"message": err.message}), err.status)
