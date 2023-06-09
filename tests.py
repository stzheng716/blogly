from models import DEFAULT_IMAGE_URL, User
from app import app, db
from unittest import TestCase
import os

os.environ["DATABASE_URL"] = "postgresql:///blogly_test"


# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        # As you add more models later in the exercise, you'll want to delete
        # all of their records before each test just as we're doing with the
        # User model below.
        User.query.delete()

        self.client = app.test_client()

        test_user = User(
            first_name="test1_first",
            last_name="test1_last",
            image_url=None,
        )

        db.session.add(test_user)
        db.session.commit()

        # We can hold onto our test_user's id by attaching it to self (which is
        # accessible throughout this test class). This way, we'll be able to
        # rely on this user in our tests without needing to know the numeric
        # value of their id, since it will change each time our tests are run.
        self.user_id = test_user.id

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_list_users(self):
        """Tests for test_user on user page."""

        with self.client as c:
            resp = c.get("/users")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("test1_first", html)
            self.assertIn("test1_last", html)

    def test_new_user(self):
        """Test for new user page"""

        with self.client as c:
            resp = c.get("/users/new")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("new user test", html)

    def test_add_new_user(self):
        """Redirection test for new user post"""

        with self.client as c:
            resp = c.post("/users/new", data={
                "first": "bob",
                "last": "banana",
                "imgURL": "",
            })
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "/users")

    def test_redirection_followed(self):
        """Adding new user to DB and redirect to users"""

        with self.client as c:
            resp = c.post("/users/new", follow_redirects=True, data={
                "first": "bob",
                "last": "banana",
                "imgURL": "",
            })
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('banana', html)
            self.assertIn('<!-- TESTSTRING_USERS -->', html)

    def test_user_details_route(self):
        """Accessing user details page via URL user_id"""

        with self.client as c:
            resp = c.get(f"/users/{self.user_id}")
            html = resp.get_data(as_text=True)

            self.assertIn("test1_first", html)
            self.assertIn("test1_last", html)
            self.assertIn(DEFAULT_IMAGE_URL, html)

    def test_delete(self):
        with self.client as c:
            resp = c.post(f"/users/{self.user_id}/delete",
                          follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('test1_first', html)
            self.assertNotIn('test1_last', html)
