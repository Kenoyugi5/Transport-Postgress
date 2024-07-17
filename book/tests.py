from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Booking, Driver, Vehicle
from datetime import datetime, time

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            username='admin', password='adminpass', email='admin@example.com')
        self.user = User.objects.create_user(
            username='user', password='userpass', email='user@example.com')
        
        self.vehicle = Vehicle.objects.create(
            licence_plate='ABC123', description='Test Vehicle')
        
        self.driver = Driver.objects.create(
            first_name='John', last_name='Doe', phone='123456789')
        
        self.booking = Booking.objects.create(
            subject='Math', class_involved='Class A', no_of_people=20,
            purpose='Field Trip', trip_date=datetime.now(), destination='Park',
            departure_time=time(10, 0),  # Correct time format
            transport_back=True, approx_time_back=time(14, 0))  # Correct time format
        self.booking.vehicle.add(self.vehicle)
        self.booking.driver.add(self.driver)

    def test_mark_as_notified_superuser(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('mark_as_notified', args=[self.booking.id]))
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertTrue(self.booking.notified)

    def test_mark_as_notified_non_superuser(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('mark_as_notified', args=[self.booking.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_booking_notifications_superuser(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('booking_notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications.html')

    def test_booking_notifications_non_superuser(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('booking_notifications'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_vehicle_booking_view(self):
        response = self.client.get(reverse('vehicle-booking', args=[self.vehicle.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vehicle_booking.html')

    def test_approval_view_superuser(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('approval'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'approval.html')

    def test_approval_view_non_superuser(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('approval'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_my_bookings_view(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('my-bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_bookings.html')

    def test_add_driver(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('add-driver'), {
            'first_name': 'Jane', 'last_name': 'Doe', 'phone': '987654321'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Driver.objects.filter(first_name='Jane').exists())

    def test_update_driver(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('update-driver', args=[self.driver.id]), {
            'first_name': 'Johnny', 'last_name': 'Doe', 'phone': '123456789'})
        self.assertEqual(response.status_code, 302)
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.first_name, 'Johnny')

    def test_delete_driver(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('delete-driver', args=[self.driver.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Driver.objects.filter(id=self.driver.id).exists())

    def test_pdf_generation(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('spec_driver_pdf', args=[self.driver.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_csv_generation(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('spec_driver_csv', args=[self.driver.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
