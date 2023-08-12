"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config["WTF_CSRF_ENABLED"] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        user = User.signup(
            username="testuser",
            email="test@test.com",
            password="testuser",
            image_url=None,
        )
        db.session.add(user)
        db.session.commit()
        self.testuser = user

        self.user_id = user.id

    def test_user_list(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

                resp = c.get("/users")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn(self.testuser.username, html)

    def test_show_user(self):
        msg = Message(id=1, text="test_text", user_id=self.testuser.id)
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

                resp = c.get(f"/users/{self.user_id}")
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn(self.testuser.username, html)
                self.assertIn(msg.text, html)

    def test_following(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

                resp = c.get(f"/users/{self.user_id}/following", follow_redirects=True)
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                for followed_user in self.testuser.following:
                    self.assertIn(followed_user.username, html)
                    self.assertIn(followed_user.bio, html)
                    self.assertIn(
                        '<form method="POST" action="/users/stop-following/{{followed_user.id }}"><button class="btn btn-primary btn-sm">Unfollow<button></form>',
                        html,
                    )

    def test_unauthorized_following(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 807098

                resp = c.get(f"/users/{807098}/following", follow_redirects=True)
                html = resp.get_data(as_text=True)

                self.assertNotEqual(resp.status_code, 302)
                self.assertIn("Access unauthorized", str(resp.data))
                for followed_user in self.testuser.following:
                    self.assertNotIn(followed_user.username, html)
                    self.assertNotIn(followed_user.bio, html)
                    self.assertNotIn(
                        '<form method="POST" action="/users/stop-following/{{followed_user.id }}"><button class="btn btn-primary btn-sm">Unfollow<button></form>',
                        html,
                    )

    def test_followers(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

                resp = c.get(f"/users/{self.user_id}/followers", follow_redirects=True)
                html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                for follower in self.testuser.followers:
                    self.assertIn(follower.username, html)
                    self.assertIn(follower.bio, html)

    def test_unauthorized_followers(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 78

                resp = c.get(f"/users/{78}/followers", follow_redirects=True)
                html = resp.get_data(as_text=True)

                self.assertNotEqual(resp.status_code, 302)
                self.assertIn("Access unauthorized", str(resp.data))
                for follower in self.testuser.followers:
                    self.assertNotIn(follower.username, html)
                    self.assertNotIn(follower.bio, html)

    