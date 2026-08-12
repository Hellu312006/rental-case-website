from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from properties.models import Country, State, City, PropertyCategory, Property
from bookings.models import BookingRequest
from wishlist.models import Wishlist

User = get_user_model()

class RentEaseSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # 1. Create Location Data
        self.country = Country.objects.create(name="India")
        self.state = State.objects.create(country=self.country, name="Gujarat")
        self.city = City.objects.create(state=self.state, name="Surat")
        
        # 2. Create Property Category
        self.category = PropertyCategory.objects.create(category_name="Flat", description="Apartments")
        
        # 3. Create Owner and Tenant accounts
        self.owner = User.objects.create_user(
            username='owner@test.com',
            email='owner@test.com',
            password='password123',
            first_name='John',
            last_name='Owner',
            role='Owner'
        )
        
        self.other_owner = User.objects.create_user(
            username='other@test.com',
            email='other@test.com',
            password='password123',
            first_name='Alex',
            last_name='Morgan',
            role='Owner'
        )

        self.tenant = User.objects.create_user(
            username='tenant@test.com',
            email='tenant@test.com',
            password='password123',
            first_name='Jane',
            last_name='Tenant',
            role='Tenant'
        )

        # 4. Create Property listing
        self.property = Property.objects.create(
            owner=self.owner,
            category=self.category,
            property_name="Ocean View Apartment",
            description="Lovely flat near beach",
            address="Dumas Road",
            city=self.city,
            state=self.state,
            country=self.country,
            rent_per_month=15000,
            security_deposit=30000,
            available_rooms=2,
            total_rooms=3,
            property_type='Flat',
            image='dummy.jpg'
        )

    # --- Section A: Authentication Tests ---
    def test_registration_success(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@test.com',
            'role': 'Tenant',
            'password': 'password123',
            'confirm_password': 'password123',
        })
        self.assertEqual(response.status_code, 302)  # Redirects to login
        self.assertTrue(User.objects.filter(email='newuser@test.com').exists())

    def test_registration_duplicate_email(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'Jane',
            'last_name': 'Tenant',
            'email': 'tenant@test.com',  # Existing email
            'role': 'Tenant',
            'password': 'password123',
            'confirm_password': 'password123',
        })
        self.assertEqual(response.status_code, 200)  # Re-renders form
        self.assertFalse(User.objects.filter(email='tenant@test.com').count() > 1)

    def test_registration_password_mismatch(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'Jane',
            'last_name': 'Tenant',
            'email': 'jane2@test.com',
            'role': 'Tenant',
            'password': 'password123',
            'confirm_password': 'mismatchedpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='jane2@test.com').exists())

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'email': 'tenant@test.com',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, 302)  # Redirects to dashboard_redirect
        self.assertRedirects(response, reverse('dashboard_redirect'), target_status_code=302)

    def test_login_invalid(self):
        response = self.client.post(reverse('login'), {
            'email': 'tenant@test.com',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)  # Re-renders login
        self.assertFalse(self.client.session.get('_auth_user_id'))

    def test_logout(self):
        self.client.login(email='tenant@test.com', password='password123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))

    # --- Section B: Authorization & Access Control Tests ---
    def test_unauthenticated_user_denied_dashboard(self):
        response = self.client.get(reverse('dashboard_redirect'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_tenant_cannot_access_owner_dashboard(self):
        self.client.login(email='tenant@test.com', password='password123')
        response = self.client.get(reverse('owner_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('tenant_dashboard'))

    def test_owner_cannot_access_tenant_dashboard(self):
        self.client.login(email='owner@test.com', password='password123')
        response = self.client.get(reverse('tenant_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('owner_dashboard'))

    def test_owner_cannot_edit_other_owners_property(self):
        self.client.login(email='other@test.com', password='password123')
        response = self.client.get(reverse('edit_property', args=[self.property.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard_redirect'), target_status_code=302)

    # --- Section C: GET-based State Changes Mitigation Tests ---
    def test_toggle_wishlist_get_request_returns_405(self):
        self.client.login(email='tenant@test.com', password='password123')
        response = self.client.get(reverse('toggle_wishlist', args=[self.property.id]))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_booking_action_get_request_returns_405(self):
        # Create a booking request
        booking = BookingRequest.objects.create(
            tenant=self.tenant,
            property=self.property,
            move_in_date="2026-09-01",
            duration_months=6,
            status='Pending'
        )
        self.client.login(email='owner@test.com', password='password123')
        response = self.client.get(reverse('booking_action', args=[booking.id, 'approve']))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
        
        # Verify status did not change
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'Pending')
