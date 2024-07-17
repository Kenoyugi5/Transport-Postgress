from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def send_booking_notification(booking, user, request):
    subject = 'New Booking Created'
    approval_url = request.build_absolute_uri(reverse('approval'))
    message = (
        f'A new booking has been created by {user.username}.\n\n'
        f'Details:\n'
        f'Subject: {booking.subject}\n'
        f'Class: {booking.class_involved}\n'
        f'Trip Date: {booking.trip_date}\n'
        f'Destination: {booking.destination}\n'
        f'\nYou can approve the booking here: {approval_url}'
    )
    principal_email = settings.ADMIN_EMAIL
    send_mail(subject, message, settings.EMAIL_HOST_USER, [principal_email])

def send_manager_notification(booking, request):
    subject = 'Booking Approved'
    assign_url = request.build_absolute_uri(reverse('bookings-list'))  # Change to the appropriate URL for assigning vehicles and drivers
    message = (
        f'The booking with the following details has been approved:\n\n'
        f'Subject: {booking.subject}\n'
        f'Class: {booking.class_involved}\n'
        f'Trip Date: {booking.trip_date}\n'
        f'Destination: {booking.destination}\n'
        f'\nPlease assign vehicles and drivers here: {assign_url}'
    )
    send_mail(subject, message, settings.EMAIL_HOST_USER, [settings.MANAGER_EMAIL])

def send_teacher_notification(booking):
    subject = 'Your Booking Has Been Approved'
    message = (
        f'Dear {booking.teacher},\n\n'
        f'Your booking with the following details has been approved:\n\n'
        f'Subject: {booking.subject}\n'
        f'Class: {booking.class_involved}\n'
        f'Trip Date: {booking.trip_date}\n'
        f'Destination: {booking.destination}\n\n'
        f'Please contact the administration for further details.'
    )
    send_mail(subject, message, settings.EMAIL_HOST_USER, [booking.teacher.email])