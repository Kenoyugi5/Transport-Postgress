from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Booking, Driver, Vehicle
from .forms import SignUpForm, ChangePasswordForm, BookingForm, BookingFormAdmin, VehicleForm, DriverForm
from django import forms
from django.contrib.auth.decorators import login_required
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from .utils import send_booking_notification, send_manager_notification, send_teacher_notification
from django.db.models import Q
import csv
# PDF Imports
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
# Pagination Imports
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def search(request):
    if request.method == "POST":
        searched_term = request.POST.get('searched', None)
        if searched_term:
            searched_results = Booking.objects.filter(
                Q(subject__icontains=searched_term) | 
                Q(destination__icontains=searched_term) | 
                Q(purpose__icontains=searched_term)
            )
            if not searched_results:
                messages.success(request, "Booking Does Not Exist...Please try Again.")
                return render(request, "search.html", {'searched': searched_term})
            else:
                return render(request, "search.html", {'bookings': searched_results, 'searched': searched_term})
        else:
            messages.error(request, "You forgot to search for a booking.")
            return redirect('home')
    else:
        return render(request, "search.html", {})


@login_required
def mark_as_notified(request, booking_id):
    if request.user.is_superuser:
        booking = get_object_or_404(Booking, pk=booking_id)
        booking.notified = True
        booking.save()
        messages.success(request, "Booking marked as read.")
        return redirect('booking_notifications')
    else:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('home')

@login_required
def booking_notifications(request):
    if request.user.is_superuser:
        new_bookings = Booking.objects.filter(approved=False, notified=False).order_by('-trip_date')
        return render(request, 'notifications.html', {'new_bookings': new_bookings})
    else:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')


def vehicle_booking(request, vehicle_id):
    # Grab the vehicle
    vehicle = Vehicle.objects.get(id=vehicle_id)
    # Grab the bookings from that vehicle
    bookings =  vehicle.booking_set.all()
    if bookings:
        return render(request, 'vehicle_booking.html', {
            "bookings": bookings
            })
    else:
        messages.success(request, ("Vehicle Currently Has No Booking"))
        return redirect('approval')


@login_required
def approval(request):
    vehicle_list = Vehicle.objects.all()
    booking_count = Booking.objects.all().count()
    vehicle_count = Vehicle.objects.all().count()
    driver_count = Vehicle.objects.all().count()
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    bookings_in_month = Booking.objects.filter(trip_date__year=current_year, trip_date__month=current_month).count()
    booking_list = Booking.objects.all().order_by('approved')

    if request.user.is_superuser:
        if request.method == "POST":
            id_list = request.POST.getlist('boxes')
            for booking in booking_list:
                booking.approved = booking.id in map(int, id_list)
                if booking.approved:
                    booking.approved_by = request.user
                    booking.save()
                    send_manager_notification(booking, request)
                    send_teacher_notification(booking)
                else:
                    booking.save()

            messages.success(request, "Bookings updated successfully.")
            return redirect('bookings-list')

        paginator = Paginator(booking_list, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'approval.html', {
            "booking_list": page_obj,
            "booking_count": booking_count,
            "vehicle_count": vehicle_count,
            "driver_count": driver_count,
            "bookings_in_month": bookings_in_month,
            "vehicle_list": vehicle_list,
        })
    else:
        messages.error(request, "You aren't authorised to view this page")
        return redirect('home')


def my_bookings(request):
    if request.user.is_authenticated:
        me = request.user.id
        booking_list = Booking.objects.filter(teacher=me).order_by('trip_date')

        paginator = Paginator(booking_list, 5)  # Show 5 bookings per page

        page = request.GET.get('page')
        try:
            bookings = paginator.page(page)
        except PageNotAnInteger:
            bookings = paginator.page(1)
        except EmptyPage:
            bookings = paginator.page(paginator.num_pages)

        return render(request, 'my_bookings.html', {
            "bookings": bookings
        })
    else:
        messages.success(request, ("You aren't authorised to view this page"))
        return redirect('home')


# Generate specific PDF files
def spec_driver_pdf(request, driver_id):
    driver = get_object_or_404(Driver, pk=driver_id)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Times-Roman", 12)

    lines = []
    lines.append(driver.first_name)
    lines.append(driver.last_name)
    lines.append(driver.phone)
    lines.append(" ")

    for line in lines:
        textob.textLine(line)

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    filename = f'{driver.last_name}.pdf'

    return FileResponse(buf, as_attachment=True, filename=filename)

def spec_vehicle_pdf(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Times-Roman", 12)

    lines = []
    lines.append(vehicle.licence_plate)
    lines.append(vehicle.description)
    lines.append(" ")

    for line in lines:
        textob.textLine(line)

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    filename = f'{vehicle.licence_plate}.pdf'

    return FileResponse(buf, as_attachment=True, filename=filename)

def spec_booking_pdf(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Times-Roman", 14)

    lines = []
    lines.append("Booking Report")
    lines.append("")

    lines.append(f'Subject/Department: {booking.subject}')
    lines.append(f'Classes Involved: {booking.class_involved}')
    lines.append(f'Total No. of People: {booking.no_of_people}')
    lines.append(f'Purpose: {booking.purpose}')
    lines.append(f'Trip Date: {booking.trip_date}')
    lines.append(f'Destination: {booking.destination}')
    lines.append(f'Departure Time: {booking.departure_time}')
    lines.append(f'Transport Back: {"Yes" if booking.transport_back else "No"}')

    if booking.transport_back:
        lines.append(f'Approx. Time Back: {booking.approx_time_back}')

    vehicles = ", ".join([vehicle.licence_plate for vehicle in booking.vehicle.all()])
    lines.append(f'Vehicles Assigned: {vehicles}')

    drivers = ", ".join([f"{driver.first_name} {driver.last_name}" for driver in booking.driver.all()])
    lines.append(f'Drivers Assigned: {drivers}')

    lines.append("")
    lines.append("")

    for line in lines:
        textob.textLine(line)

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    filename = f'{booking.subject}.pdf'

    return FileResponse(buf, as_attachment=True, filename=filename)


# Generate PDF files
def driver_pdf(request):
	buf = io.BytesIO()
	c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
	textob = c.beginText()
	textob.setTextOrigin(inch, inch)
	textob.setFont("Times-Roman", 12)

	drivers = Driver.objects.all()

	lines = []
	for driver in drivers:
		lines.append(driver.first_name)
		lines.append(driver.last_name)
		lines.append(driver.phone)
		lines.append(" ")

	for line in lines:
		textob.textLine(line)

	c.drawText(textob)
	c.showPage()
	c.save()
	buf.seek(0)

	return FileResponse(buf, as_attachment=True, filename='Drivers.pdf')

def vehicle_pdf(request):
	buf = io.BytesIO()
	c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
	textob = c.beginText()
	textob.setTextOrigin(inch, inch)
	textob.setFont("Times-Roman", 12)

	vehicles = Vehicle.objects.all()

	lines = []
	for vehicle in vehicles:
		lines.append(vehicle.licence_plate)
		lines.append(vehicle.description)
		lines.append(" ")

	for line in lines:
		textob.textLine(line)

	c.drawText(textob)
	c.showPage()
	c.save()
	buf.seek(0)

	return FileResponse(buf, as_attachment=True, filename='Vehicles.pdf')

def booking_pdf(request):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Times-Roman", 12)

    bookings = Booking.objects.all()

    lines = []
    lines.append("Bookings Report")
    lines.append("")

    for booking in bookings:
    	lines.append(f'Subject/Department: {booking.subject}')
    	lines.append(f'Classes Involved: {booking.class_involved}')
    	lines.append(f'Total No. of People: {booking.no_of_people}')
    	lines.append(f'Purpose: {booking.purpose}')
    	lines.append(f'Trip Date: {booking.trip_date}')
    	lines.append(f'Destination: {booking.destination}')
    	lines.append(f'Departure Time: {booking.departure_time}')
    	lines.append(f'Transport Back: {"Yes" if booking.transport_back else "No"}')

    	if booking.transport_back:
    		lines.append(f'Approx. Time Back: {booking.approx_time_back}')

    	vehicles = ", ".join([vehicle.licence_plate for vehicle in booking.vehicle.all()])
    	lines.append(f'Vehicles Assigned: {vehicles}')

    	drivers = ", ".join([f"{driver.first_name} {driver.last_name}" for driver in booking.driver.all()])
    	lines.append(f'Drivers Assigned: {drivers}')

    	lines.append("")
    	lines.append("")

    for line in lines:
        textob.textLine(line)

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='Bookings.pdf')

# Generate specific CSV files
def spec_driver_csv(request, driver_id):
    driver = get_object_or_404(Driver, pk=driver_id)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={driver.last_name}.csv'

    writer = csv.writer(response)

    writer.writerow(['First Name', 'Last Name', 'Phone Number',])
        
    writer.writerow([driver.first_name, driver.last_name, driver.phone])

    return response

def spec_vehicle_csv(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={vehicle.licence_plate}.csv'

    writer = csv.writer(response)

    # Add column headings to the csv file
    writer.writerow(['Licence Plate', 'Description'])

    # Write vehicle data
    writer.writerow([vehicle.licence_plate, vehicle.description])

    return response

def spec_booking_csv(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={booking.subject}.csv'

    writer = csv.writer(response)

    # Add column headings to the csv file
    writer.writerow([
        'Subject/Department',
        'Classes Involved',
        'Total No. of People',
        'Purpose',
        'Trip Date',
        'Destination',
        'Departure Time',
        'Transport Back',
        'Approx. Time Back',
        'Vehicles Assigned',
        'Drivers',
    ])

    vehicles = ", ".join([vehicle.licence_plate for vehicle in booking.vehicle.all()])
    drivers = ", ".join([f"{driver.first_name} {driver.last_name}" for driver in booking.driver.all()])

    writer.writerow([
        booking.subject,
        booking.class_involved,
        booking.no_of_people,
        booking.purpose,
        booking.trip_date,
        booking.destination,
        booking.departure_time,
        "Yes" if booking.transport_back else "No",
        booking.approx_time_back if booking.transport_back else "",
        vehicles,
        drivers
    ])

    return response


# Generate CSV files
def driver_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Drivers.csv'

    writer = csv.writer(response)

    drivers = Driver.objects.all()

    # Add column headings to the csv file
    writer.writerow([
        'First Name',
        'Last Name',
        'Phone Number',
    ])

    for driver in drivers:        
        writer.writerow([
            driver.first_name,
            driver.last_name,
            driver.phone
        ])

    return response

def vehicle_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Vehicles.csv'

    writer = csv.writer(response)

    vehicles = Vehicle.objects.all()

    # Add column headings to the csv file
    writer.writerow([
        'Licence Plate',
        'Description',
    ])

    for vehicle in vehicles:        
        writer.writerow([
            vehicle.licence_plate,
            vehicle.description,
        ])

    return response

def booking_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Bookings.csv'

    writer = csv.writer(response)

    bookings = Booking.objects.all()

    # Add column headings to the csv file
    writer.writerow([
        'Subject/Department',
        'Classes Involved',
        'Total No. of People',
        'Purpose',
        'Trip Date',
        'Destination',
        'Departure Time',
        'Transport Back',
        'Approx. Time Back',
        'Vehicles Assigned',
        'Drivers',
    ])

    for booking in bookings:
        vehicles = ", ".join([vehicle.licence_plate for vehicle in booking.vehicle.all()])
        drivers = ", ".join([f"{driver.first_name} {driver.last_name}" for driver in booking.driver.all()])

        writer.writerow([
            booking.subject,
            booking.class_involved,
            booking.no_of_people,
            booking.purpose,
            booking.trip_date,
            booking.destination,
            booking.departure_time,
            "Yes" if booking.transport_back else "No",
            booking.approx_time_back if booking.transport_back else "",
            vehicles,
            drivers
        ])

    return response

# Generate specific text files
def spec_driver_text(request, driver_id):
	driver = get_object_or_404(Driver, pk=driver_id)

	response = HttpResponse(content_type='text/plain')
	response['Content-Disposition'] = f'attachment; filename={driver.first_name} {driver.last_name}.txt'

	drivers = Driver.objects.all()

	lines = [
	f'First Name: {driver.first_name}\n',
	f'Last Name: {driver.last_name}\n',
	f'Phone Number: {driver.phone}\n',
	]

	response.writelines(lines)
	return response

def spec_vehicle_text(request, vehicle_id):
	vehicle = get_object_or_404(Vehicle, pk=vehicle_id)

	response = HttpResponse(content_type='text/plain')
	response['Content-Disposition'] = f'attachment; filename={vehicle.licence_plate}.txt'

	lines = [
	f'Licence Plate: {vehicle.licence_plate}\n',
	f'Description: {vehicle.description}\n'
	]

	response.writelines(lines)
	return response

def spec_booking_text(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)

    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={booking.subject}.txt'

    lines = [
        f'Subject/Department: {booking.subject}\n',
        f'Classes Involved: {booking.class_involved}\n',
        f'Total No. of People: {booking.no_of_people}\n',
        f'Purpose: {booking.purpose}\n',
        f'Trip Date: {booking.trip_date}\n',
        f'Destination: {booking.destination}\n',
        f'Departure Time: {booking.departure_time}\n',
        f'Transport Back: {"Yes" if booking.transport_back else "No"}\n',
    ]
    
    if booking.transport_back:
        lines.append(f'Approx. Time Back: {booking.approx_time_back}\n')

    vehicles = ", ".join([vehicle.licence_plate for vehicle in booking.vehicle.all()])
    lines.append(f'Vehicles Assigned: {vehicles}\n')

    drivers = ", ".join([f"{driver.first_name} {driver.last_name}" for driver in booking.driver.all()])
    lines.append(f'Drivers Assigned: {drivers}\n')

    response.writelines(lines)
    return response


# Generate text files
def driver_text(request):
	response = HttpResponse(content_type='text/plain')
	response['Content-Disposition'] = 'attachment; filename=Driver.txt'

	drivers = Driver.objects.all()

	lines = []

	for driver in drivers:
		lines.append(f'First Name: {driver.first_name}\nLast Name: {driver.first_name}\nPhone Number: {driver.phone}\n\n')

	response.writelines(lines)
	return response

def vehicle_text(request):
	response = HttpResponse(content_type='text/plain')
	response['Content-Disposition'] = 'attachment; filename=Vehicles.txt'

	vehicles = Vehicle.objects.all()

	lines = []

	for vehicle in vehicles:
		lines.append(f'Licence Plate: {vehicle.licence_plate}\nDescription: {vehicle.description}\n\n')

	response.writelines(lines)
	return response

def booking_text(request):
	response = HttpResponse(content_type='text/plain')
	response['Content-Disposition'] = 'attachment; filename=Booking.txt'

	bookings = Booking.objects.all()

	lines = []

	for booking in bookings:
		lines.append(f'Subject/Department: {booking.subject}\n')
		lines.append(f'Classes Involved: {booking.class_involved}\n')
		lines.append(f'Total No. of People: {booking.no_of_people}\n')
		lines.append(f'Purpose: {booking.purpose}\n')
		lines.append(f'Trip Date: {booking.trip_date}\n')
		lines.append(f'Destination: {booking.destination}\n')
		lines.append(f'Departure Time: {booking.departure_time}\n')
		lines.append(f'Transport Back: {"Yes" if booking.transport_back else "No"}\n')

		if booking.transport_back:
			lines.append(f'Approx. Time Back: {booking.approx_time_back}\n')

		vehicles = ", ".join([vehicle.licence_plate for vehicle in booking.vehicle.all()])
		lines.append(f'Vehicles Assigned: {vehicles}\n')

		drivers = ", ".join([f"{driver.first_name} {driver.last_name}" for driver in booking.driver.all()])
		lines.append(f'Drivers Assigned: {drivers}\n')

		lines.append('\n')	

	response.writelines(lines)
	return response


def delete_driver(request, driver_id):
	driver = Driver.objects.get(pk=driver_id)
	driver.delete()
	return redirect('drivers-list')

def delete_vehicle(request, vehicle_id):
	vehicle = Vehicle.objects.get(pk=vehicle_id)
	vehicle.delete()
	return redirect('vehicles-list')

def delete_booking(request, booking_id):
    booking = Booking.objects.get(pk=booking_id)
    if request.user == booking.teacher:
        booking.delete()
        messages.success(request, ("Booking deleted!"))
        return redirect('bookings-list')
    else:
        messages.success(request, ("You aren't authorised to delete the booking"))
        return redirect('bookings-list')


def update_driver(request, driver_id):
	driver = Driver.objects.get(pk=driver_id)
	form = DriverForm(request.POST or None, request.FILES or None, instance=driver)
	if form.is_valid():
		form.save()
		return redirect('drivers-list')
		
	return render(request, 'update_driver.html', 
		{
		"driver":driver,
		"form":form,
		})

def update_vehicle(request, vehicle_id):
	vehicle = Vehicle.objects.get(pk=vehicle_id)
	form = VehicleForm(request.POST or None, request.FILES or None, instance=vehicle)
	if form.is_valid():
		form.save()
		return redirect('vehicles-list')
		
	return render(request, 'update_vehicle.html', 
		{
		"vehicle":vehicle,
		"form":form,
		})

def update_booking(request, booking_id):
    booking = Booking.objects.get(pk=booking_id)
    if request.user.is_superuser:
        form = BookingFormAdmin(request.POST or None, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('bookings-list')
    else:
        form = BookingForm(request.POST or None, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('bookings-list')

    return render(request, 'update_booking.html', 
		{
		"booking":booking,
		"form":form,
		})


def show_driver(request, driver_id):
	driver = Driver.objects.get(pk=driver_id)
	return render(request, 'show_driver.html', 
		{
		"driver":driver
		})

def show_vehicle(request, vehicle_id):
    vehicle = Vehicle.objects.get(pk=vehicle_id)

    bookings = vehicle.booking_set.all()

    return render(request, 'show_vehicle.html', {
        "vehicle":vehicle,
        "bookings": bookings,
        })

def show_booking(request, booking_id):
	booking = Booking.objects.get(pk=booking_id)
	return render(request, 'show_booking.html', 
		{
		"booking":booking
		})


def add_driver(request):
    if request.method == "POST":
        form = DriverForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Driver added successfully.')
            return HttpResponseRedirect(reverse('drivers-list'))
    else:
        form = DriverForm()
    
    return render(request, 'add_driver.html', {'form': form})

def add_vehicle(request):
    if request.method == "POST":
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle added successfully.')
            return HttpResponseRedirect(reverse('vehicles-list'))
    else:
        form = VehicleForm()
    
    return render(request, 'add_vehicle.html', {'form': form})

@login_required
def add_booking(request):
    if request.method == "POST":
        if request.user.is_superuser:
            form = BookingFormAdmin(request.POST)
        else:
            form = BookingForm(request.POST)
        
        if form.is_valid():
            booking = form.save(commit=False)
            if not request.user.is_superuser:
                booking.teacher = request.user  # logged in user
            booking.notified = False  # Set notification status to False
            booking.save()

            # Send email notification to the principal
            send_booking_notification(booking, request.user, request)

            messages.success(request, 'Booking submitted successfully.')
            return HttpResponseRedirect(reverse('my-bookings'))
    else:
        if request.user.is_superuser:
            form = BookingFormAdmin()
        else:
            form = BookingForm()
    
    return render(request, 'add_booking.html', {'form': form})


def all_drivers(request):
	driver_list = Driver.objects.all().order_by('last_name')
	return render(request, 'drivers_list.html', 
		{
		"driver_list":driver_list,
		})

def all_vehicles(request):
	vehicle_list = Vehicle.objects.all().order_by('description')
	return render(request, 'vehicles_list.html', 
		{
		"vehicle_list":vehicle_list,
		})

def all_bookings(request):
    booking_list = Booking.objects.filter(approved=True).order_by('-date_created')
    paginator = Paginator(booking_list, 2)  # Number of items per page

    page = request.GET.get('page')

    try:
        bookings = paginator.page(page)
    except PageNotAnInteger:
        bookings = paginator.page(1)
    except EmptyPage:
        bookings = paginator.page(paginator.num_pages)

    return render(request, 'bookings_list.html', {'bookings': bookings})


class BookingHTMLCalendar(HTMLCalendar):
    def __init__(self, bookings):
        super().__init__()
        self.bookings = bookings

    def formatday(self, day, weekday):
        if day != 0:
            date = datetime(self.year, self.month, day)
            cssclass = self.cssclasses[weekday]
            if date in self.bookings:
                cssclass += ' booking-day'
            return f'<td class="{cssclass}">{day}</td>'
        return '<td class="noday">&nbsp;</td>'

    def formatmonth(self, year, month, withyear=True):
        self.year, self.month = year, month
        return super().formatmonth(year, month, withyear)

def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            month = month.capitalize()
            # Convert month from name to number
            month_number = list(calendar.month_name).index(month)
            month_number = int(month_number)

            # Get current year
            now = datetime.now()
            current_year = now.year

            # Query the Booking model for dates
            bookings = Booking.objects.filter(
                trip_date__year=year,
                trip_date__month=month_number,
            )
            booking_dates = [booking.trip_date for booking in bookings]

             # Create a custom calendar
            cal = BookingHTMLCalendar(booking_dates).formatmonth(year, month_number)

            # Pagination
            paginator = Paginator(bookings, 5)  # 3 bookings per page
            page = request.GET.get('page', 1)

            try:
                bookings = paginator.page(page)
            except PageNotAnInteger:
                bookings = paginator.page(1)
            except EmptyPage:
                bookings = paginator.page(paginator.num_pages)

            # Get current time
            time = now.strftime('%I:%M %p')

            return render(request, 'home.html', {
                "year": year,
                "month": month,
                "month_number": month_number,
                "cal": cal,
                "current_year": current_year,
                "time": time,
                "booking_list": bookings,
            })
        else:
           return redirect('my-bookings')
    else:
        return render(request, 'login.html', {})


def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, ("You have been logged in"))
			return redirect('home')
		else:
			messages.success(request, ("There was an error, please try again"))
			return redirect('login')

	else:
		return render(request, 'login.html', {})

def logout_user(request):
	logout(request)
	messages.success(request, ("You have been logged out"))
	return redirect('home')

def register_user(request):
	form = SignUpForm()
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']

			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, ("User Registered Successfully."))
			return redirect('home')
		else:
			messages.success(request, ("There was a problem registering. Please try again"))
			return redirect('register')
	else:
		return render(request, 'register.html', {'form': form})

def update_password(request):
	if request.user.is_authenticated:
		current_user = request.user
		# Did they fill out the form
		if request.method == 'POST':
			form = ChangePasswordForm(current_user, request.POST)
			# Is the form valid
			if form.is_valid():
				form.save()
				messages.success(request, "Your Password Has Been Updated")
				login(request, current_user)
				return redirect('login')
			else:
				for error in list(form.errors.values()):
					messages.error(request, error)
					return redirect('update_password')
		else:
			form = ChangePasswordForm(current_user)
			return render(request, "update_password.html", {"form": form})
	else:
		messages.success(request, "You Must Be Logged In to Access That Page.")
		return redirect('home')