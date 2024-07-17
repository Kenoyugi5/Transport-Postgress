from django.contrib import admin
from .models import Booking, Driver, Vehicle

admin.site.register(Driver)
admin.site.register(Vehicle)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
	fields = ('teacher', 'subject', ('class_involved', 'no_of_people'), 'purpose', 'destination', ('trip_date', 'departure_time'), ('transport_back', 'approx_time_back'), ('approved', 'approved_by'), ('vehicle', 'driver'))
	list_display = ('subject', 'class_involved', 'trip_date', 'destination', 'approved_by')
	list_filter = ('teacher', 'subject', 'trip_date', 'date_created', 'approved')
	ordering = ('-trip_date',)
	search_fields = ('subject', 'trip_date', 'destination')

# Name = Admin, Pass = Transport5