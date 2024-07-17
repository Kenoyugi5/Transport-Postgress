from django.db import models
from django.contrib.auth.models import User
import datetime
from datetime import date

# Create your models here.
class Vehicle(models.Model):
	licence_plate = models.CharField(max_length=10)
	description = models.CharField(max_length=50)
	vehicle_image = models.ImageField(null=True, blank=True, upload_to="images/")

	def __str__(self):
		return self.licence_plate

class Driver(models.Model):
	first_name = models.CharField(max_length=25)
	last_name = models.CharField(max_length=25)
	phone = models.CharField(max_length=15)
	driver_image = models.ImageField(null=True, blank=True, upload_to="images/")

	def __str__(self):
		return self.first_name + ' ' + self.last_name

class Booking(models.Model):
	teacher = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
	subject = models.CharField('Subject', max_length=75)
	class_involved = models.CharField('Classes Involved', max_length=75)
	no_of_people = models.IntegerField()
	purpose = models.CharField('Purpose', max_length=75, blank=True)
	trip_date = models.DateField()
	destination = models.CharField('Destination', max_length=75)
	departure_time = models.TimeField()
	transport_back = models.BooleanField(default=True)
	approx_time_back = models.TimeField(blank=True, null=True)
	date_created = models.DateTimeField(auto_now_add=True)
	approved = models.BooleanField('Approved', default=False)
	approved_by = models.ForeignKey(User, related_name='approved_bookings', blank=True, null=True, on_delete=models.SET_NULL)
	vehicle = models.ManyToManyField(Vehicle, blank=True)
	driver = models.ManyToManyField(Driver, blank=True)
	notified = models.BooleanField(default=False)

	def __str__(self):
		return self.subject

	@property
	def Days_till(self):
		today = date.today()
		days_till = self.trip_date - today
		days_till_stripped = str(days_till).split(",", 1)[0]
		return days_till_stripped

	@property
	def Is_Past(self):
		today = date.today()
		if self.trip_date < today:
			return "Past"
		else:
			return ""