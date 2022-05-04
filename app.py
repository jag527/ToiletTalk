# app.py
# AUTHOR: Jonathan Grossman (jag527)

import json

from db import db, Location, Leaderboard, Message
from flask import Flask, request


# create db file
db_filename = "toilettalk.db"
app = Flask(__name__)


# setup config
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_filename}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True


# initialize app
db.init_app(app)
with app.app_context():
    db.create_all()


# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code


# --------- ROUTES ---------
@app.route("/")
def blank_route():
    """
    Endpoint for a blank route
    """
    pass


@app.route("/api/messages/")
def get_all_messages():
    """
    Endpoint for getting all messages
    """
    return success_response({"messages": [m.serialize_message() for m in Message.query.all()]})


@app.route("/api/messages/<int:message_id>/")
def get_message_by_id(message_id):
    """
    Endpoint for getting a specific message given its message_id
    """
    message = Message.query.filter_by(message_id=message_id)
    if message is None:
        return failure_response("Message does not exist.")
    return success_response(Message.serialize_message())


@app.route("/api/messages/", methods=["POST"])
def post_message():
    """
    Endpoint for posting a new message
    """
    body = json.loads(request.data)

    location = body.get("location_id")
    descr = body.get("description")

    # Checks if the Location ID is in the database (valid location)
    loc_check = Location.query.filter_by(location_id=location)
    if loc_check is None:
        return failure_response("Message from invalid location.")

    new_message = Message(location_id=location, description=descr)

    db.session.add(new_message)
    db.session.commit()

    return success_response(new_message.serialize_message(), 201)


@ app.route("/api/messages/<int:message_id>/", methods=["DELETE"])
def delete_message_by_id(message_id):
    """
    Endpoint for deleting a specific message given its message_id
    """
    message = Message.query.filter_by(message_id=message_id).first()
    if message is None:
        return failure_response("Messgae does not exist.")

    db.session.delete(message)
    db.session.commit()
    return success_response(message.serialize_message())


@ app.route("/api/locations/", methods=["POST"])
def log_in_attempt():
    """
    Endpoint for an attempted log into chat room
    """
    pass


@ app.route("/api/leaderboard/")
def get_leaderboard():
    """
    Endpoint for getting the leaderboard
    """
    return success_response({"leaderboard": [l.serialize_leaderboard() for l in Leaderboard.query.all()]})
