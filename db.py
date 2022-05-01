# db.py
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Message(db.Model):
    """
    Messages model
    """
    __tablename__ = "messages"
    # TODO add in columns

    def __init__(self, **kwargs):
        pass

    def serialize_message(self):
        pass


class Location(db.Model):
    """
    Locations model
    """
    __tablename__ = "locations"
    # TODO add in columns

    def __init__(self, **kwargs):
        pass

    def serialize_location(self):
        pass


class Leaderboard(db.Model):
    """
    Leaderboards model
    """
    __tablename__ = "leaderboards"
    # TODO add in columns

    def __init__(self, **kwargs):
        pass

    def serialize_leaderboard(self):
        pass
