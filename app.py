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


def baseline_toilettalk_tables():
    """
    Creates Location table with predetermined values
    Creates blank leaderboard
    """
    loc_test = Location.query.filter_by(location_id="Cocktail Lounge").first()
    if loc_test is None:
        locations = [
            "Duffield First Floor",
            "Duffield Second Floor",
            "Cocktail Lounge",
            "Hollister First Floor",
            "Statler Hall Second Floor"
        ]

        passcodes = [1111, 2222, 3333, 4444, 5555]

        for i in range(5):
            db.session.add(Location(location_id=locations[i], passcode=passcodes[i]))
            db.session.add(Leaderboard(location_id=locations[i]))

        db.session.commit()

    else:
        pass


# initialize app
db.init_app(app)
with app.app_context():
    print("HERE")
    db.create_all()

    # add baseline values to tables
    baseline_toilettalk_tables()


# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code


# ------------------ ROUTES ------------------
@ app.route("/")
def blank_route():
    """
    Endpoint for a blank route/homescreen
    """
    return success_response({"homescreen": "hello world"})


@ app.route("/api/messages/")
def get_all_messages():
    """
    Endpoint for getting all messages
    """
    return success_response(
        {"messages": [m.serialize_message() for m in Message.query.all()]}
    )


@ app.route("/api/messages/<int:message_id>/")
def get_message_by_id(message_id):
    """
    Endpoint for getting a specific message given its message_id
    """
    message = Message.query.filter_by(message_id=message_id).first()

    if message is None:
        return failure_response("Message does not exist.")

    return success_response(Message.serialize_message())


@ app.route("/api/messages/", methods=["POST"])
def post_message():
    """
    Endpoint for posting a new message
    """
    body = json.loads(request.data)

    location = body.get("location_id")
    descr = body.get("description")

    # Checks if the Location ID is in the database (valid location)
    loc_check = Location.query.filter_by(location_id=location).first()
    if loc_check is None:
        return failure_response("Message from invalid location.")

    # Make new message object
    new_message = Message(location_id=location, description=descr)

    # Add message to the location's list of messages
    loc_check.messages.append(new_message)

    # Increment the location's message counter on the leaderboard
    loc_leaderboard = Leaderboard.query.filter_by(location_id=location).first()
    loc_leaderboard.increment_message_counter()

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
def enter_toilettalk():
    """
    Endpoint for an attempted log into ToiletTalk
    """
    body = json.loads(request.data)

    location = body.get("location")
    password = body.get("password")

    if location is None or password is None:
        return failure_response("Invalid input.")

    # Checking if the location and its passcode line up
    location_db = Location.query.filter_by(location_id=location).first()

    # Checking if location entered as input is in the database
    if location_db is None:
        return failure_response("Invalid input.")

    if location_db.passcode == password:
        return success_response({"valid?": True})
    elif location_db.passcode != password:
        return success_response({"valid?": False})


@ app.route("/api/leaderboard/")
def get_leaderboard():
    """
    Endpoint for getting the leaderboard
    """
    return success_response(
        {"leaderboard": [l.serialize_leaderboard() for l in Leaderboard.query.all()]}
    )


@app.route("/api/locations/")
def get_location_passcodes():
    """
    Endpoint for getting all locations and their passcodes
    """
    return success_response(
        {"locations": [l.serialize_location() for l in Location.query.all()]}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
