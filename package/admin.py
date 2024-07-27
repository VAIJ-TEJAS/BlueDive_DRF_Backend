from django.contrib import admin
from .models import BreakFastOption, LunchOption, DinnerOption, RoomSharingOption, WaterSportOption, Package, Amenity

@admin.register(BreakFastOption)
class BreakFastOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'status']

@admin.register(LunchOption)
class LunchOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'status']

@admin.register(DinnerOption)
class DinnerOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'status']

@admin.register(RoomSharingOption)
class RoomSharingOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'discount', 'status']

@admin.register(WaterSportOption)
class WaterSportOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'status']

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_price', 'duration']
    filter_horizontal = ['breakfast_options', 'lunch_options', 'dinner_options', 'room_sharing_options', 'water_sport_options']

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'package']
