from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm
from django import forms
from django.forms import ModelForm
from .models import Booking, Vehicle, Driver

class DriverForm(ModelForm):
    class Meta:
        model = Driver
        fields = ('first_name', 'last_name', 'phone', 'driver_image')
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone': 'Phone Number',
            'driver_image': '',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        }

class VehicleForm(ModelForm):
    class Meta:
        model = Vehicle
        fields = ('licence_plate', 'description', 'vehicle_image')
        labels = {
            'licence_plate': 'Licence Plate',
            'description': 'Description',
            'vehicle_image': '',
        }
        widgets = {
            'licence_plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Licence Plate'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
        }

# Teacher Event Form
class BookingForm(ModelForm):
    class Meta:
        model = Booking
        fields = (
            'subject', 'class_involved', 'no_of_people', 'purpose', 
            'destination', 'trip_date', 'departure_time', 'transport_back', 
            'approx_time_back'
        )
        labels = {
            'subject': 'Subject',
            'class_involved': 'Classes Involved',
            'no_of_people': 'Number of People',
            'purpose': 'Purpose',
            'destination': 'Destination',
            'trip_date': 'Trip Date',
            'departure_time': 'Departure Time',
            'transport_back': 'Transport Back',
            'approx_time_back': 'Aprrox.Time Back',
        }
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject/Department'}),
            'class_involved': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Classes Involved'}),
            'no_of_people': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total No. of people'}),
            'purpose': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Purpose'}),
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Destination'}),
            'trip_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'departure_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'transport_back': forms.NullBooleanSelect(attrs={'class': 'form-control'}),
            'approx_time_back': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

# Admin/Manager Event Form
class BookingFormAdmin(ModelForm):
    class Meta:
        model = Booking
        fields = (
            'teacher', 'subject', 'class_involved', 'no_of_people', 'purpose', 
            'destination', 'trip_date', 'departure_time', 'transport_back', 
            'approx_time_back', 'vehicle', 'driver'
        )
        labels = {
            'teacher': 'Teacher',
            'subject': 'Subject',
            'class_involved': 'Classes Involved',
            'no_of_people': 'Number of People',
            'purpose': 'Purpose',
            'destination': 'Destination',
            'trip_date': 'Trip Date',
            'departure_time': 'Departure Time',
            'transport_back': 'Transport Back',
            'approx_time_back': 'Aprrox.Time Back',
            'vehicle': 'Vehicle Assigned',
            'driver': 'Name of Driver Assigned',
        }
        widgets = {
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject/Department'}),
            'class_involved': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Classes Involved'}),
            'no_of_people': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total No. of people'}),
            'purpose': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Purpose'}),
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Destination'}),
            'trip_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'departure_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'transport_back': forms.NullBooleanSelect(attrs={'class': 'form-control'}),
            'approx_time_back': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'vehicle': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'driver': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }



class ChangePasswordForm(SetPasswordForm):
	class Meta:
		model = User
		fields = ['new_password1', 'new_password2']

	def __init__(self, *args, **kwargs):
		super(ChangePasswordForm, self).__init__(*args, **kwargs)

		self.fields['new_password1'].widget.attrs['class'] = 'form-control'
		self.fields['new_password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['new_password1'].label = ''
		self.fields['new_password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['new_password2'].widget.attrs['class'] = 'form-control'
		self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['new_password2'].label = ''
		self.fields['new_password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


class SignUpForm(UserCreationForm):
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'User Name'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password1'].label = ''
		self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['password2'].label = ''
		self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'