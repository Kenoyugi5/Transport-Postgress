from .models import Booking

def new_booking_count(request):
    if request.user.is_superuser:
        count = Booking.objects.filter(approved=False, notified=False).count()
        return {'new_booking_count': count}
    return {}
