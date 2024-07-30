from django.contrib import admin
from .models import Booking
from django.contrib.auth.models import User

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'trip', 'advance_payment', 'complete_payment', 'booking_date', 'status')
    list_filter = ('trip', 'status', 'booking_date')
    search_fields = ('user__username', 'trip__package__name')
    readonly_fields = ('booking_date',)

admin.site.register(Booking, BookingAdmin)
