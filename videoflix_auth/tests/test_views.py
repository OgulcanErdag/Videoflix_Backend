from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from videoflix_auth.models import PasswordResetToken
import uuid
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.timezone import now
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status


class RegistrationViewTests(TestCase):

    def test_registration_success(self):
        url = reverse('register')
        data = {
            "email": "testuser@example.com",
            "password": "Password123",
            "repeated_password": "Password123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.filter(email="testuser@example.com").count(), 1)

    def test_registration_existing_email(self):
        User.objects.create_user(email="testuser@example.com", username="testuser", password="Password123")
        url = reverse('register')
        data = {
            "email": "testuser@example.com",
            "password": "Password123",
            "repeated_password": "Password123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("User with this email already exists", response.json()["email"])

    def test_registration_passwords_dont_match(self):
        url = reverse('register')
        data = {
            "email": "testuser@example.com",
            "password": "Password123",
            "repeated_password": "Password456"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Passwords don't match", response.json()["password"])


class ActivateAccountViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="testuser@example.com", username="testuser", password="Password123")
        self.user.is_active = False
        self.user.save()

    def test_activate_account_success(self):
        uid = self.user.pk
        token = default_token_generator.make_token(self.user)
        url = reverse('activate', args=[urlsafe_base64_encode(force_bytes(uid)), token])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_activate_account_invalid_token(self):
        uid = self.user.pk
        url = reverse('activate', args=[urlsafe_base64_encode(force_bytes(uid)), "invalidtoken"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
    
    def test_user_does_not_exist(self):
        nonexistent_uid = urlsafe_base64_encode(force_bytes(9999))  
        token = default_token_generator.make_token(self.user)
        url = reverse('activate', args=[nonexistent_uid, token])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Invalid user."})


class LoginViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="testuser@example.com", username="testuser", password="Password123")

    def test_login_success(self):
        url = reverse('login')
        data = {"email": "testuser", "password": "Password123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())

    def test_login_invalid_credentials(self):
        url = reverse('login')
        data = {"email": "testuser", "password": "WrongPassword"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 401)

    def test_login_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        url = reverse('login')
        data = {"email": "testuser", "password": "Password123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403)
        
    def test_login_nonexistent_user(self):
        """Test login for a user that does not exist."""
        url = reverse('login')
        data = {"email": "nonexistent@example.com", "password": "Password123"}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"message": "Invalid username or password."})


class PasswordResetTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="testuser@example.com", username="testuser", password="Password123")

    def test_password_reset_request_success(self):
        url = reverse('password_reset')
        data = {"email": "testuser@example.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PasswordResetToken.objects.filter(user=self.user).count(), 1)

    def test_password_reset_request_invalid_email(self):
        url = reverse('password_reset')
        data = {"email": "nonexistent@example.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)


class PasswordResetConfirmTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="testuser@example.com", username="testuser", password="Password123")
        self.token = str(uuid.uuid4())
        PasswordResetToken.objects.create(user=self.user, token=self.token)

    def test_password_reset_confirm_success(self):
        url = reverse('password_reset_confirm', args=[self.token])
        data = {
            "password": "NewPassword123",
            "repeated_password": "NewPassword123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPassword123"))

    def test_password_reset_confirm_invalid_token(self):
        url = reverse('password_reset_confirm', args=["invalidtoken"])
        data = {
            "password": "NewPassword123",
            "repeated_password": "NewPassword123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_passwords_dont_match(self):
        url = reverse('password_reset_confirm', args=[self.token])
        data = {
            "password": "NewPassword123",
            "repeated_password": "WrongPassword123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_missing_password_fields(self):
        url = reverse('password_reset_confirm', args=[self.token])
    
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Both password fields are required'})

        data = {"password": "NewPassword123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Both password fields are required'})

        data = {"repeated_password": "NewPassword123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Both password fields are required'})
        
    def test_password_reset_confirm_invalid_or_expired_token(self):
        url = reverse('password_reset_confirm', args=["invalidtoken"])
        data = {
            "password": "NewPassword123",
            "repeated_password": "NewPassword123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Invalid or expired token'})
        
    def test_password_reset_confirm_invalid_token_is_valid(self):
        expired_token = PasswordResetToken.objects.create(
            user=self.user,
            token=str(uuid.uuid4())
        )
        expired_token.created_at = now() - timedelta(minutes=16)
        expired_token.save(update_fields=['created_at'])
        self.assertFalse(expired_token.is_valid(), "The token should be invalid, but is_valid() returned True")
        url = reverse('password_reset_confirm', args=[expired_token.token])
        data = {
            "password": "NewPassword123",
            "repeated_password": "NewPassword123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Invalid or expired token'})


class TokenLoginViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="testuser@example.com", username="testuser", password="Password123")
        self.token_object = Token.objects.create(user=self.user)
        self.valid_token = self.token_object.key
        self.url = reverse('token_login')

    def test_valid_token_login(self):
        response = self.client.post(self.url, data={'token': self.valid_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['token'], self.valid_token)

    def test_invalid_token_login(self):
        invalid_token = str(uuid.uuid4())
        response = self.client.post(self.url, data={'token': invalid_token})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], "Invalid token.")

    def test_missing_token_in_request(self):
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], "Invalid token.")