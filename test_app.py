from app import app
from app import app, register_user
from app import init_db
from flask import Flask
from flask import Flask, jsonify
import json
import os
import pytest
import sqlite3
import unittest

class TestApp:

    def test_get_users_database_connection_error(self):
        """
        Test the get_users function when there's a database connection error.
        This test verifies that the function handles database connection issues gracefully.
        """
        with unittest.mock.patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = sqlite3.Error("Unable to connect to database")

            with app.test_client() as client:
                response = client.get('/users')

                self.assertEqual(response.status_code, 500)
                self.assertIn("Database error", response.get_json()['error'])

    def test_get_users_empty_database(self):
        """
        Test the get_users function when the database is empty.
        This test ensures that the function returns an empty list when there are no users.
        """
        with unittest.mock.patch('sqlite3.connect') as mock_connect:
            mock_cursor = mock_connect.return_value.cursor.return_value
            mock_cursor.fetchall.return_value = []

            with app.test_client() as client:
                response = client.get('/users')

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_json(), [])

    def test_get_users_returns_json_list(self):
        """
        Test that get_users() returns a JSON list of users.

        This test verifies that:
        1. The /users endpoint returns a 200 status code
        2. The response content type is JSON
        3. The response body is a non-empty list
        4. Each user in the list has 'id' and 'email' fields
        """
        with app.test_client() as client:
            response = client.get('/users')
            assert response.status_code == 200
            assert response.content_type == 'application/json'

            users = json.loads(response.data)
            assert isinstance(users, list)
            assert len(users) > 0

            for user in users:
                assert 'id' in user
                assert 'email' in user

    def test_init_db_1(self):
        """
        Test that init_db creates the users table if it doesn't exist.

        This test verifies that the init_db function successfully creates
        the users table with the correct schema when called. It checks if
        the table exists and has the expected structure after initialization.
        """
        # Remove the database file if it exists
        if os.path.exists('users.db'):
            os.remove('users.db')

        # Call the init_db function
        init_db()

        # Connect to the database and check if the users table exists
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Query to check if the users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone() is not None

        # Query to get the table schema
        cursor.execute("PRAGMA table_info(users)")
        schema = cursor.fetchall()

        conn.close()

        # Assert that the table exists
        assert table_exists, "The users table was not created"

        # Assert that the table has the correct schema
        expected_schema = [
            (0, 'id', 'INTEGER', 0, None, 1),
            (1, 'email', 'TEXT', 1, None, 0),
            (2, 'password', 'TEXT', 1, None, 0)
        ]
        assert schema == expected_schema, "The users table schema is incorrect"

    def test_register_user_2(self):
        """
        Test successful user registration when both email and password are provided.

        This test verifies that when valid email and password are supplied,
        the register_user function returns a success message with a 201 status code.
        """
        client = app.test_client()
        response = client.post('/register', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert response.status_code == 201
        assert response.get_json() == {"message": "User registered successfully!"}

    def test_register_user_duplicate_email(self):
        """
        Test registering a user with an email that already exists in the database.
        This tests the explicit handling of sqlite3.IntegrityError in the focal method.
        """
        client = app.test_client()

        # Register a user first
        client.post('/register', json={'email': 'test@example.com', 'password': 'testpass'})

        # Try to register the same email again
        response = client.post('/register', json={'email': 'test@example.com', 'password': 'newpass'})
        assert response.status_code == 400
        assert json.loads(response.data)['error'] == "Email already registered"

    def test_register_user_missing_credentials(self):
        """
        Test registration with missing email or password.
        Ensures that the API returns a 400 error with the correct message
        when either email or password is not provided.
        """
        client = app.test_client()

        # Test with missing email
        response = client.post('/register', json={'password': 'testpass'})
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Email and password are required"}

        # Test with missing password
        response = client.post('/register', json={'email': 'test@example.com'})
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Email and password are required"}

        # Test with both email and password missing
        response = client.post('/register', json={})
        assert response.status_code == 400
        assert json.loads(response.data) == {"error": "Email and password are required"}

    def test_register_user_missing_credentials_2(self):
        """
        Test registering a user with missing email or password.
        This tests the explicit check in the focal method for empty email or password.
        """
        client = app.test_client()

        # Test missing email
        response = client.post('/register', json={'password': 'testpass'})
        assert response.status_code == 400
        assert json.loads(response.data)['error'] == "Email and password are required"

        # Test missing password
        response = client.post('/register', json={'email': 'test@example.com'})
        assert response.status_code == 400
        assert json.loads(response.data)['error'] == "Email and password are required"
