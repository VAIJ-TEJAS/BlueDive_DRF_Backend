from django.contrib import admin

from booking.models import Booking
from .models import Trip

class BookingInline(admin.TabularInline):  
    model = Booking
    extra = 1

class TripAdmin(admin.ModelAdmin):
    list_display = ('package', 'start_date', 'end_date', 'available_seats', 'status')
    list_filter = ('package', 'start_date', 'end_date', 'status')
    search_fields = ('package__name',)

    inlines = [BookingInline]

admin.site.register(Trip, TripAdmin)
