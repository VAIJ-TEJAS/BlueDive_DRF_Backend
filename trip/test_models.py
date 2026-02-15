from datetime import date, timedelta
from django.test import TestCase
from package.models import Package
from trip.models import Trip


class TripModelTest(TestCase):
    def setUp(self):
        self.package = Package.objects.create(name='Konkan Adventure', duration='3 Days / 2 Nights')
        self.trip = Trip.objects.create(
            package=self.package,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=33),
            available_seats=18,
            available_rooms=6,
            status='Scheduled',
        )

    def test_str(self):
        result = str(self.trip)
        self.assertIn('Konkan Adventure', result)
        self.assertIn('Scheduled', result)

    def test_default_seats(self):
        trip = Trip.objects.create(
            package=self.package,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=13),
        )
        self.assertEqual(trip.available_seats, 18)
        self.assertEqual(trip.available_rooms, 6)

    def test_default_status(self):
        trip = Trip.objects.create(
            package=self.package,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=13),
        )
        self.assertEqual(trip.status, 'Scheduled')

    def test_status_choices(self):
        for status_val in ['Scheduled', 'Ongoing', 'Completed', 'Cancelled', 'Omitted']:
            trip = Trip.objects.create(
                package=self.package,
                start_date=date.today() + timedelta(days=10),
                end_date=date.today() + timedelta(days=13),
                status=status_val,
            )
            self.assertEqual(trip.status, status_val)


class PackageModelTest(TestCase):
    def test_str(self):
        pkg = Package.objects.create(name='Beach Trip', duration='2 Days')
        self.assertEqual(str(pkg), 'Beach Trip')

    def test_optional_fields(self):
        pkg = Package.objects.create(name='Minimal', duration='1 Day')
        self.assertIsNone(pkg.code)
        self.assertIsNone(pkg.description)
        self.assertIsNone(pkg.display_price)
        self.assertIsNone(pkg.display_discount_percentage)

    def test_with_all_fields(self):
        pkg = Package.objects.create(
            name='Full Package',
            duration='5 Days / 4 Nights',
            code='FP001',
            description='A complete package',
            display_price=15000,
            display_discount_percentage=10,
        )
        self.assertEqual(pkg.code, 'FP001')
        self.assertEqual(pkg.display_price, 15000)
        self.assertEqual(pkg.display_discount_percentage, 10)
