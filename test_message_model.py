"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from datetime import datetime
from psycopg2 import IntegrityError
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.drop_all()
db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User(email="test@test.com", username="testuser", password="HASHED_PASSWORD")

        db.session.add(u)
        db.session.commit()
        self.u = u

        self.client = app.test_client()

    def tearDown(self):
        response = super().tearDown()
        db.session.rollback()
        return response

    def test_message_model(self):
        msg = Message(id=1, text="test_text", user_id=self.u.id)

        db.session.add(msg)
        db.session.commit()

        self.assertIsNotNone(msg)
        self.assertEqual(msg.text, "test_text")
        self.assertEqual(msg.user_id, self.u.id)

    def test_text_length(self):
        with self.assertRaises(exc.DataError):
            msg = Message(
                text="A" * 141,
                timestamp=datetime.utcnow(),
                user_id=self.u.id,
            )
            db.session.add(msg)
            db.session.commit()

    def test_relationship(self):
        msg1 = Message(id=1, text="test_text", user_id=self.u.id)
        msg2 = Message(id=2, text="test_text_for_msg2", user_id=self.u.id)

        self.u.messages.append(msg1)
        self.u.messages.append(msg2)
        db.session.add(self.u)
        db.session.commit()

        self.assertEqual(len(self.u.messages), 2)
