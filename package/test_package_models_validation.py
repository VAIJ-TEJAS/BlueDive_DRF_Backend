"""
F2P tests for package models validation improvements.
These tests would fail on the base branch and pass after the fixes.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from package.models import Package, Meal, Accommodation, Vehicle, PickupPoint, WaterSportOption


class PackageModelsF2PTest(TestCase):
    """Test package models validation improvements"""
    
    def test_package_name_minimum_length(self):
        """Bug: Should reject package name shorter than 3 characters"""
        package = Package(
            name='AB',  # Too short
            duration='3 days'
        )
        
        with self.assertRaises(ValidationError) as context:
            package.full_clean()
        
        self.assertIn('Package name must be at least 3 characters long', str(context.exception))
    
    def test_package_name_regex_validation(self):
        """Bug: Should reject package name with special characters"""
        package = Package(
            name='Test@Package',  # Contains special character
            duration='3 days'
        )
        
        with self.assertRaises(ValidationError) as context:
            package.full_clean()
        
        self.assertIn('Package name can only contain letters, numbers, spaces, and hyphens', str(context.exception))
    
    def test_package_name_valid_format(self):
        """Bug: Should accept valid package name format"""
        package = Package(
            name='Test Package 2025',  # Valid
            duration='3 days'
        )
        
        # Should not raise validation error
        package.full_clean()
        self.assertEqual(package.name, 'Test Package 2025')
    
    def test_package_duration_minimum_length(self):
        """Bug: Should reject duration shorter than 2 characters"""
        package = Package(
            name='Test Package',
            duration='3'  # Too short
        )
        
        with self.assertRaises(ValidationError) as context:
            package.full_clean()
        
        self.assertIn('Duration must be at least 2 characters long', str(context.exception))
    
    def test_package_duration_regex_validation(self):
        """Bug: Should reject invalid duration format"""
        package = Package(
            name='Test Package',
            duration='3 weeks'  # Invalid format
        )
        
        with self.assertRaises(ValidationError) as context:
            package.full_clean()
        
        self.assertIn('Duration must be in format like "3 days" or "2 hours"', str(context.exception))
    
    def test_package_duration_valid_formats(self):
        """Bug: Should accept valid duration formats"""
        valid_durations = ['3 days', '1 day', '5 hours', '2 hour']
        
        for duration in valid_durations:
            package = Package(
                name='Test Package',
                duration=duration
            )
            
            # Should not raise validation error
            package.full_clean()
            self.assertEqual(package.duration, duration)
    
    def test_package_description_max_length(self):
        """Bug: Should reject description exceeding 2000 characters"""
        long_description = 'A' * 2001  # 2001 characters
        
        package = Package(
            name='Test Package',
            duration='3 days',
            description=long_description
        )
        
        with self.assertRaises(ValidationError) as context:
            package.full_clean()
        
        self.assertIn('Description cannot exceed 2000 characters', str(context.exception))
    
    def test_package_description_valid_length(self):
        """Bug: Should accept description within limit"""
        description = 'A' * 1000  # 1000 characters
        
        package = Package(
            name='Test Package',
            duration='3 days',
            description=description
        )
        
        # Should not raise validation error
        package.full_clean()
        self.assertEqual(package.description, description)
    
    def test_package_display_price_negative(self):
        """Bug: Should reject negative display price"""
        package = Package(
            name='Test Package',
            duration='3 days',
            display_price=-1000
        )
        
        with self.assertRaises(ValidationError) as context:
            package.full_clean()
        
        self.assertIn('Display price cannot be negative', str(context.exception))
    
    def test_package_display_price_maximum(self):
        """Bug: Should reject display price exceeding limit"""
        package = Package(
            name='Test Package',
            duration='3 days',
            display_price=1000000  # Exceeds 999,999
        )
        
        with self.assertRaises(ValidationError) as context:
            package.full_clean()
        
        self.assertIn('Display price cannot exceed 999,999', str(context.exception))
    
    def test_package_display_price_valid_range(self):
        """Bug: Should accept valid display price range"""
        package = Package(
            name='Test Package',
            duration='3 days',
            display_price=50000  # Valid
        )
        
        # Should not raise validation error
        package.full_clean()
        self.assertEqual(package.display_price, 50000)
    
    def test_package_discount_percentage_negative(self):
        """Bug: Should reject negative discount percentage"""
        package = Package(
            name='Test Package',
            duration='3 days',
            display_discount_percentage=-10
        )
        
        with self.assertRaises(ValidationError) as context:
            package.full_clean()
        
        self.assertIn('Discount percentage cannot be negative', str(context.exception))
    
    def test_package_discount_percentage_over_100(self):
        """Bug: Should reject discount percentage over 100"""
        package = Package(
            name='Test Package',
            duration='3 days',
            display_discount_percentage=150
        )
        
        with self.assertRaises(ValidationError) as context:
            package.full_clean()
        
        self.assertIn('Discount percentage cannot exceed 100', str(context.exception))
    
    def test_package_discount_percentage_valid_range(self):
        """Bug: Should accept valid discount percentage range"""
        valid_percentages = [0, 10, 25, 50, 75, 100]
        
        for percentage in valid_percentages:
            package = Package(
                name='Test Package',
                duration='3 days',
                display_discount_percentage=percentage
            )
            
            # Should not raise validation error
            package.full_clean()
            self.assertEqual(package.display_discount_percentage, percentage)
    
    def test_package_code_regex_validation(self):
        """Bug: Should reject package code with invalid format"""
        package = Package(
            name='Test Package',
            duration='3 days',
            code='test-code'  # Contains lowercase letters
        )
        
        with self.assertRaises(ValidationError) as context:
            package.full_clean()
        
        self.assertIn('Package code can only contain uppercase letters, numbers, and hyphens', str(context.exception))
    
    def test_package_code_valid_format(self):
        """Bug: Should accept valid package code format"""
        package = Package(
            name='Test Package',
            duration='3 days',
            code='TEST-123-456'  # Valid
        )
        
        # Should not raise validation error
        package.full_clean()
        self.assertEqual(package.code, 'TEST-123-456')
    
    def test_package_complete_valid_data(self):
        """Bug: Should accept complete valid package data"""
        accommodation = Accommodation.objects.create(
            name='Test Hotel',
            details='Test details'
        )
        vehicle = Vehicle.objects.create(
            name='Test Bus',
            details='Test details'
        )
        
        package = Package(
            name='Test Package 2025',
            code='PKG-2025',
            duration='3 days',
            description='A wonderful package for testing',
            display_price=10000,
            display_discount_percentage=10,
            accommodation=accommodation,
            vehicle=vehicle
        )
        
        # Should not raise validation error
        package.full_clean()
        self.assertEqual(package.name, 'Test Package 2025')
        self.assertEqual(package.code, 'PKG-2025')
    
    def test_meal_model_validation(self):
        """Bug: Meal model should work without validation errors"""
        meal = Meal(
            name='Test Meal',
            description='Test meal description'
        )
        
        # Should not raise validation error
        meal.full_clean()
        self.assertEqual(meal.name, 'Test Meal')
    
    def test_accommodation_model_validation(self):
        """Bug: Accommodation model should work without validation errors"""
        accommodation = Accommodation(
            name='Test Hotel',
            details='Test hotel details'
        )
        
        # Should not raise validation error
        accommodation.full_clean()
        self.assertEqual(accommodation.name, 'Test Hotel')
    
    def test_vehicle_model_validation(self):
        """Bug: Vehicle model should work without validation errors"""
        vehicle = Vehicle(
            name='Test Bus',
            details='Test bus details'
        )
        
        # Should not raise validation error
        vehicle.full_clean()
        self.assertEqual(vehicle.name, 'Test Bus')
    
    def test_pickup_point_model_validation(self):
        """Bug: PickupPoint model should work without validation errors"""
        pickup = PickupPoint(
            name='Test Location',
            location='https://maps.example.com/test'
        )
        
        # Should not raise validation error
        pickup.full_clean()
        self.assertEqual(pickup.name, 'Test Location')
    
    def test_water_sport_option_model_validation(self):
        """Bug: WaterSportOption model should work without validation errors"""
        water_sport = WaterSportOption(
            name='Scuba Diving'
        )
        
        # Should not raise validation error
        water_sport.full_clean()
        self.assertEqual(water_sport.name, 'Scuba Diving')
