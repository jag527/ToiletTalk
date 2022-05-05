# db.py
# AUTHOR: Jonathan Grossman

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Location(db.Model):
    """
    Locations model
    """
    __tablename__ = "locations"
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.String, nullable=False)
    passcode = db.Column(db.Integer, nullable=False)
    messages = db.relationship("Message")

    def __init__(self, **kwargs):
        """
        Creates a location from a given id and passcode
        """
        self.location_id = kwargs.get("location_id")
        self.passcode = kwargs.get("passcode")

    def serialize_location(self):
        """
        Serializes a location into dictionary/json form
        """
        return {
            "id": self.id,
            "location_id": self.location_id,
            "passcode": self.passcode,
            "messages": [m.serialize_message() for m in self.messages]
        }


class Message(db.Model):
    """
    Messages model
    """
    __tablename__ = "messages"
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String, nullable=False)
    location_id = db.Column(db.String, db.ForeignKey("locations.location_id"), nullable=False)

    def __init__(self, **kwargs):
        """
        Creates a message from a given location with a given description
        """
        self.description = kwargs.get("description", "")
        self.location_id = kwargs.get("location_id")

    def serialize_message(self):
        """
        Serializes a message into dictionary/json form
        """
        return {
            "message_id": self.message_id,
            "description": self.description,
            "location_id": self.location_id
        }


class Leaderboard(db.Model):
    """
    Leaderboards model
    """
    __tablename__ = "leaderboards"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location_id = db.Column(db.String, nullable=False)
    message_counter = db.Column(db.Integer, nullable=False)

    def __init__(self, **kwargs):
        """
        Creates a leaderboard spot for a certain location with initial message
        counter value 0
        """
        self.location_id = kwargs.get("location_id")
        self.message_counter = 0

    def serialize_leaderboard(self):
        """
        Serializes a leaderboard spot into dictionary/json form
        """
        return {
            "location_id": self.location_id,
            "message_counter": self.message_counter
        }

    def increment_message_counter(self):
        """
        Increases the message counter for a location by 1
        """
        self.message_counter = self.message_counter + 1
