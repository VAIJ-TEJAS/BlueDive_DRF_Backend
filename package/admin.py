from django.contrib import admin
from .models import (
    Meal, MealRecords, Option, Event, Day, EventRecord, 
    DayRecord, Package, PackageImages, PaxOptions, Vehicle, VehicleImage, 
    Accommodation, AccommodationImage
)
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

class VehicleInline(nested_admin.NestedTabularInline):
    model = Vehicle
    extra = 1

class AccommodationInline(nested_admin.NestedTabularInline):
    model = Accommodation
    extra = 1

class PackageImagesInline(nested_admin.NestedTabularInline):
    model = PackageImages
    extra = 1

class PackageAdmin(nested_admin.NestedModelAdmin):
    list_display = ('name', 'duration', 'description', 'accommodation', 'vehicle')
    search_fields = ('name', 'description', 'accommodation__name', 'vehicle__name')
    inlines = [PackageImagesInline, DayRecordInline, PaxOptionsInline]

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

class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1

class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'details')
    inlines = [VehicleImageInline]

class AccommodationImageInline(admin.TabularInline):
    model = AccommodationImage
    extra = 1

class AccommodationAdmin(admin.ModelAdmin):
    list_display = ('name', 'details')
    inlines = [AccommodationImageInline]

admin.site.register(Event, EventAdmin)
admin.site.register(Day, DayAdmin)
admin.site.register(Package, PackageAdmin)
admin.site.register(Meal)
# admin.site.register(Option, OptionAdmin)
# admin.site.register(EventRecord, EventRecordAdmin)
# admin.site.register(DayRecord, DayRecordAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Accommodation, AccommodationAdmin)
