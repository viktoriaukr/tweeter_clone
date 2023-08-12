"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from psycopg2 import IntegrityError
from models import db, User, Message, Follows
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        response = super().tearDown()
        db.session.rollback()
        return response

    def test_user_model(self):
        """Does basic model work?"""

        u = User(email="test@test.com", username="testuser", password="HASHED_PASSWORD")

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """Does the repr method work as expected?"""

        user = User(id=1, username="testuser", email="test@test.com")

        expected_repr = "<User #1: testuser, test@test.com>"
        self.assertEqual(repr(user), expected_repr)

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""

        user1 = User(
            id=1,
            username="testuser1",
            email="test@test1.com",
            password="HASHED_PASSWORD",
        )
        user2 = User(
            id=2,
            username="testuser2",
            email="test@test2.com",
            password="HASHED_PASSWORD",
        )
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        user1.following.append(user2)
        db.session.commit()
        follows = user1.is_following(user2)
        self.assertTrue(follows)

    def test_is_not_following(self):
        """Does is_following successfully detect when user1 is not following user2?"""

        user1 = User(
            id=1,
            username="testuser1",
            email="test@test1.com",
            password="HASHED_PASSWORD",
        )
        user2 = User(
            id=2,
            username="testuser2",
            email="test@test2.com",
            password="HASHED_PASSWORD",
        )
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        follows = user1.is_following(user2)
        self.assertFalse(follows)

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?
        Does is_followed_by successfully detect when user1 is not followed by user2?"""

        user1 = User(
            id=1,
            username="testuser1",
            email="test@test1.com",
            password="HASHED_PASSWORD",
        )
        user2 = User(
            id=2,
            username="testuser2",
            email="test@test2.com",
            password="HASHED_PASSWORD",
        )
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        user1.following.append(user2)
        db.session.commit()
        f1 = user1.is_followed_by(user2)
        f2 = user2.is_followed_by(user1)
        self.assertTrue(f2)
        self.assertFalse(f1)

    def test_signup(self):
        """Does User.create successfully create a new user given valid credentials?"""

        user = User.signup(
            "testuser1",
            "test@test1.com",
            "HASHED_PASSWORD",
            "/static/images/default-pic.png",
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser1")
        self.assertEqual(user.email, "test@test1.com")
        self.assertEqual(user.image_url, "/static/images/default-pic.png")
        self.assertTrue(bcrypt.check_password_hash(user.password, "HASHED_PASSWORD"))

    def test_failure(self):
        with self.assertRaises(TypeError):
            User.signup("testuser1", "test@test1.com", "HASHED_PASSWORD")

    def test_authentication(self):
        user = User.signup(
            "testuser1",
            "test@test1.com",
            "HASHED_PASSWORD",
            "/static/images/default-pic.png",
        )
        db.session.add(user)
        db.session.commit()

        u = User.authenticate("testuser1", "HASHED_PASSWORD")
        self.assertIsNotNone(u)
        self.assertTrue("testuser1", "HASHED_PASSWORD")


def test_wrong_password(self):
    u = User.authenticate("testuser1", "WRONG_PASSWORD")
    self.assertIsNone(u)
    self.assertFalse("testuser1", "HASHED_PASSWORD")


def test_wrong_username(self):
    u = User.authenticate("testuser1", "HASHED_PASSWORD")
    self.assertIsNone(u)
    self.assertFalse("new_user1", "HASHED_PASSWORD")
