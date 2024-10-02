from rest_framework import serializers

from trip.serializers import TripOverviewSerializer
from .models import (
    FoodOption,
    FoodRecord,
    MealFoodRecord,
    Option,
    Event,
    Day,
    EventRecord,
    DayRecord,
    Package,
    Meal,
    PackageImages,
    PaxOptions,
    MealRecords,
    PickupPoint,
    Vehicle,
    VehicleImage,
    Accommodation,
    AccommodationImage,
    WaterSportOption,
)


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = "__all__"


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = "__all__"


class EventRecordSerializer(serializers.ModelSerializer):
    event = EventSerializer()
    day = serializers.StringRelatedField()

    class Meta:
        model = EventRecord
        fields = "__all__"


class FoodOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodOption
        fields = "__all__"


class MealFoodRecordSerializer(serializers.ModelSerializer):
    food_record = serializers.StringRelatedField(read_only=True)  
    food_options = FoodOptionSerializer(many=True, read_only=True)

    class Meta:
        model = MealFoodRecord
        fields = "__all__"

class FoodRecordSerializer(serializers.ModelSerializer):
    meal_food_records = MealFoodRecordSerializer(many=True, read_only=True)
    meal = MealSerializer()

    class Meta:
        model = FoodRecord
        fields = "__all__"


class DaySerializer(serializers.ModelSerializer):
    event_records = EventRecordSerializer(many=True, read_only=True)
    food_records = FoodRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Day
        fields = "__all__"


class DayRecordSerializer(serializers.ModelSerializer):
    day = DaySerializer()

    class Meta:
        model = DayRecord
        fields = "__all__"


class MealRecordsSerializer(serializers.ModelSerializer):
    meal = MealSerializer()

    class Meta:
        model = MealRecords
        fields = "__all__"


class PaxOptionsSerializer(serializers.ModelSerializer):
    meal_records = MealRecordsSerializer(many=True, read_only=True)

    class Meta:
        model = PaxOptions
        fields = "__all__"


class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = "__all__"


class VehicleSerializer(serializers.ModelSerializer):
    images = VehicleImageSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = "__all__"


class AccommodationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccommodationImage
        fields = "__all__"


class AccommodationSerializer(serializers.ModelSerializer):
    images = AccommodationImageSerializer(many=True, read_only=True)

    class Meta:
        model = Accommodation
        fields = "__all__"


class PackageImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageImages
        fields = "__all__"


class PickupPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupPoint
        fields = "__all__"


class WaterSportOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterSportOption
        fields = "__all__"


class PackageSerializer(serializers.ModelSerializer):
    day_records = DayRecordSerializer(many=True, read_only=True)
    meals = MealSerializer(many=True, read_only=True)
    pax_options = PaxOptionsSerializer(many=True, read_only=True)
    meals = serializers.SerializerMethodField()
    default_meal_option = MealSerializer(read_only=True)
    meal_records = MealRecordsSerializer(many=True, read_only=True)
    vehicle = VehicleSerializer(read_only=True)
    accommodation = AccommodationSerializer(read_only=True)
    images = PackageImagesSerializer(many=True, read_only=True)
    pickup_points = PickupPointSerializer(many=True, read_only=True)
    water_sport_options = WaterSportOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Package
        fields = "__all__"

    def get_meals(self, obj):
        meal_ids = (
            MealRecords.objects.filter(pax_option__package=obj)
            .values_list("meal_id", flat=True)
            .distinct()
        )
        meals = Meal.objects.filter(id__in=meal_ids)
        return MealSerializer(meals, many=True).data


class PackageOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = "__all__"


class PackageTripsSerializer(serializers.ModelSerializer):
    trips = TripOverviewSerializer(many=True, read_only=True)
    day_records = DayRecordSerializer(many=True, read_only=True)
    meals = MealSerializer(many=True, read_only=True)
    pax_options = PaxOptionsSerializer(many=True, read_only=True)
    meals = serializers.SerializerMethodField()
    default_meal_option = MealSerializer(read_only=True)
    meal_records = MealRecordsSerializer(many=True, read_only=True)
    vehicle = VehicleSerializer(read_only=True)
    accommodation = AccommodationSerializer(read_only=True)
    images = PackageImagesSerializer(many=True, read_only=True)
    pickup_points = PickupPointSerializer(many=True, read_only=True)
    water_sport_options = WaterSportOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Package
        fields = "__all__"

    def get_meals(self, obj):
        meal_ids = (
            MealRecords.objects.filter(pax_option__package=obj)
            .values_list("meal_id", flat=True)
            .distinct()
        )
        meals = Meal.objects.filter(id__in=meal_ids)
        return MealSerializer(meals, many=True).data


class FoodOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodOption
        fields = "__all__"
