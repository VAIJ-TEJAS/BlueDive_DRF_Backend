from django.contrib import admin
from .models import Trip

class TripAdmin(admin.ModelAdmin):
    list_display = ('package', 'start_date', 'end_date', 'available_seats', 'status')
    list_filter = ('package', 'start_date', 'end_date', 'status')
    search_fields = ('package__name',)

admin.site.register(Trip, TripAdmin)
