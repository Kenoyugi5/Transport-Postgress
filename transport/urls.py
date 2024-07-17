from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('book.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Configure admin titles
admin.site.site_header = "Admin Page"
admin.site.site_title = "Transport System"
admin.site.index_title = "Welcome to the admin area"