from django.utils.html import format_html
from booking.models import Booking
from django.contrib import admin
from django.urls import reverse
from .models import Trip

class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    readonly_fields = ('view_booking_link',)  # Make the link field readonly
    fields = ('user', 'trip', 'status', 'view_booking_link')  # Display the link in the inline

    def view_booking_link(self, obj):
        if obj.id:
            link = reverse('admin:bookings_booking_change', args=[obj.id])
            return format_html('<a href="{}">View Details</a>', link)
        return "No Details Available"

    view_booking_link.short_description = 'Booking Details' 

class TripAdmin(admin.ModelAdmin):
    list_display = ('package', 'start_date', 'end_date', 'available_seats', 'status')
    list_filter = ('package', 'start_date', 'end_date', 'status')
    search_fields = ('package__name',)

    inlines = [BookingInline]

admin.site.register(Trip, TripAdmin)
