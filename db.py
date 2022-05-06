# db.py
# AUTHOR: Jonathan Grossman

from flask_sqlalchemy import SQLAlchemy
import base64
import boto3
import datetime
import io
from io import BytesIO
from mimetypes import guess_extension, guess_type
import os
from PIL import Image
import random
import re
import string


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

    def decrement_message_counter(self):
        """
        Decreases the message counter for a location by 1
        """
        self.message_counter = self.message_counter - 1


class ToiletPic(db.Model):
    """
    ToiletPic model
    """
    __tablename__ = "toiletpics"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    base_url = db.Column(db.String, nullable=False)
    salt = db.Column(db.String, nullable=False)
    extension = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def create(self, image_data):
        """
        Given an image in the base64 form, it does:
        1. Rejects image if not in right form
        2. Generates a random string for the image filename
        3. Decodes the image and attempts to upload it to AWS
        """

        try:
            ext = guess_extension(guess_type(image_data)[0])[1:]

            # only accept image if it is a supported file type
            if ext not in EXTENSIONS:
                raise Exception(f"Unsupported file type: {ext}")

            # secure way of generating random string for filename
            salt = "".join(
                random.SystemRandom().choice(
                    string.ascii_uppercare + string.digits
                )
                for _ in range(16)
            )

            # remove header of base64 string
            img_str = re.sub("^data:image/.+base64,", "", image_data)
            img_data = base64.b64decode(img_str)
            img = Image.open(BytesIO(img_data))

            self.base_url = S3_BASE_URL
            self.salt = salt
            self.extension = ext
            self.width = img.width
            self.height = img.height
            self.created_at = datetime.datetime.now()

            img_filename = f"{self.salt}.{self.extension}"
            self.upload(img, img_filename)

        except Exception as e:
            print(f"Error when creating image: {e}")

    def upload(self, img, img_filename):
        """
        """
        try:
            # save image temporarily on server
            img_temploc = f"{BASE_DIR}/{img_filename}"
            img.save(img_temploc)

            # upload the image to S3
            s3_client = boto3.client("s3")
            s3_client.upload_file(img_temploc, S3_BUCKET_NAME, img_filename)

            # make S3 image url is public
            s3_resource = boto3.resource("s3")
            object_acl = s3_resource.ObjectAcl(S3_BUCKET_NAME, img_filename)
            object_acl.put(ACL="public-read")

            # remove image from server
            os.remove(img_temploc)

        except Exception as e:
            print(f"Error when uploading image: {e}")

    def serialize(self):
        """
        """
        return {
            "url": f"{self.base_url}/{self.salt}.{self.extension}",
            "created": str(self.created_at)
        }
