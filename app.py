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
    pass


@app.route("/api/messages/<int:message_id>")
def get_message_by_id():
    """
    Endpoint for getting a specific message given its message_id
    """
    pass
