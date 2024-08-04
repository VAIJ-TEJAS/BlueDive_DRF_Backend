from django.contrib import admin
from .models import Meal, MealRecords, Option, Event, Day, EventRecord, DayRecord, Package, PaxOptions, Vehicle, VehicleImage, Accommodation, AccommodationImage
import nested_admin

class OptionInline(admin.TabularInline):
    model = Option
    extra = 1

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'standard_option', 'description')
    search_fields = ('name', 'description')
    inlines = [OptionInline]

class DayRecordInline(nested_admin.NestedTabularInline):
    model = DayRecord
    extra = 1

class EventRecordInline(admin.TabularInline):
    model = EventRecord
    extra = 1

class MealRecordsInline(nested_admin.NestedTabularInline):
    model = MealRecords
    extra = 1
    fields = ('meal', 'price', 'discounted_price')

class PaxOptionsInline(nested_admin.NestedTabularInline):  
    model = PaxOptions
    extra = 1
    inlines = [MealRecordsInline]

class VehicleImageInline(nested_admin.NestedTabularInline):
    model = VehicleImage
    extra = 1

class VehicleInline(nested_admin.NestedTabularInline):
    model = Vehicle
    extra = 1
    inlines = [VehicleImageInline]

class AccommodationImageInline(nested_admin.NestedTabularInline):
    model = AccommodationImage
    extra = 1

class AccommodationInline(nested_admin.NestedTabularInline):
    model = Accommodation
    extra = 1
    inlines = [AccommodationImageInline]

class PackageAdmin(nested_admin.NestedModelAdmin):
    list_display = ('name', 'duration', 'description')
    search_fields = ('name', 'description')
    inlines = [DayRecordInline, PaxOptionsInline, VehicleInline, AccommodationInline]

class OptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'event')
    list_filter = ('event',)
    search_fields = ('name', 'event__name')

class DayAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    inlines = [EventRecordInline]  

class EventRecordAdmin(admin.ModelAdmin):
    list_display = ('event', 'day')
    list_filter = ('event', 'day')
    search_fields = ('event__name', 'day__name')

class DayRecordAdmin(admin.ModelAdmin):
    list_display = ('day', 'package')
    list_filter = ('day', 'package')
    search_fields = ('day__name', 'package__name')

admin.site.register(Event, EventAdmin)
admin.site.register(Day, DayAdmin)
admin.site.register(Package, PackageAdmin)
admin.site.register(Meal)
