from django.contrib import admin
from .models import (
    FoodOption,
    FoodRecord,
    Meal,
    MealFoodRecord,
    MealRecords,
    Option,
    Event,
    Day,
    EventRecord,
    DayRecord,
    Package,
    PackageImages,
    PaxOptions,
    PickupPoint,
    Vehicle,
    VehicleImage,
    Accommodation,
    AccommodationImage,
    WaterSportOption,
)
import nested_admin


class FoodOptionAdmin(admin.ModelAdmin):
    list_display = ("name",)  # Display the name in the list view
    search_fields = ("name",)  # Allow search by name


class OptionInline(admin.TabularInline):
    model = Option
    extra = 1


class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "standard_option", "description")
    search_fields = ("name", "description")
    inlines = [OptionInline]


class DayRecordInline(nested_admin.NestedTabularInline):
    model = DayRecord
    extra = 1


class EventRecordInline(nested_admin.NestedTabularInline):
    model = EventRecord
    extra = 1


class MealRecordsInline(nested_admin.NestedTabularInline):
    model = MealRecords
    extra = 1
    fields = ("meal", "price", "discounted_price")


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
    list_display = ("name", "duration", "description", "accommodation", "vehicle")
    search_fields = ("name", "description", "accommodation__name", "vehicle__name")
    inlines = [PackageImagesInline, DayRecordInline, PaxOptionsInline]


class OptionAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "event")
    list_filter = ("event",)
    search_fields = ("name", "event__name")


class MealFoodRecordInline(nested_admin.NestedTabularInline):
    model = MealFoodRecord
    extra = 1
    fields = ("meal_type", "food_options")  # Display the meal type and food options
    autocomplete_fields = ("food_options",)  # Enables searching for food options


class FoodRecordInline(nested_admin.NestedTabularInline):
    model = FoodRecord
    extra = 1
    inlines = [MealFoodRecordInline]


class DayAdmin(nested_admin.NestedModelAdmin):
    list_display = ('get_package_name', 'name', 'description')
    inlines = [EventRecordInline, FoodRecordInline]

    def get_package_name(self, obj):
        return obj.package.name
    get_package_name.short_description = 'Package' 

class EventRecordAdmin(admin.ModelAdmin):
    list_display = ("event", "day")
    list_filter = ("event", "day")
    search_fields = ("event__name", "day__name")


class DayRecordAdmin(admin.ModelAdmin):
    list_display = ("day", "package")
    list_filter = ("day", "package")
    search_fields = ("day__name", "package__name")


class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1


class VehicleAdmin(admin.ModelAdmin):
    list_display = ("name", "details")
    inlines = [VehicleImageInline]


class AccommodationImageInline(admin.TabularInline):
    model = AccommodationImage
    extra = 1


class AccommodationAdmin(admin.ModelAdmin):
    list_display = ("name", "details")
    inlines = [AccommodationImageInline]


class PickupPointAdmin(admin.ModelAdmin):
    list_display = ("name", "location")
    search_fields = ("name", "location")


class WaterSportOptionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


admin.site.register(Event, EventAdmin)
admin.site.register(Day, DayAdmin)
admin.site.register(Package, PackageAdmin)
admin.site.register(Meal)
# admin.site.register(Option, OptionAdmin)
# admin.site.register(EventRecord, EventRecordAdmin)
# admin.site.register(DayRecord, DayRecordAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Accommodation, AccommodationAdmin)
admin.site.register(PickupPoint, PickupPointAdmin)
admin.site.register(WaterSportOption, WaterSportOptionAdmin)
admin.site.register(FoodOption, FoodOptionAdmin)
