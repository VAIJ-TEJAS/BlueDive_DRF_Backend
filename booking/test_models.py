from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from package.models import Package
from trip.models import Trip
from booking.models import Booking, PaxRecord, CustomerDetail, Payment


class BookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.package = Package.objects.create(name='Konkan Trip', duration='3 Days / 2 Nights')
        self.trip = Trip.objects.create(
            package=self.package,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=33),
            available_seats=18,
            available_rooms=6,
        )
        self.booking = Booking.objects.create(
            user=self.user,
            trip=self.trip,
            amount=Decimal('5000.00'),
            balance_amount=Decimal('2500.00'),
            status='Partially Confirmed',
        )

    def test_str(self):
        result = str(self.booking)
        self.assertIn('testuser', result)
        self.assertIn('Konkan Trip', result)

    def test_default_status(self):
        booking = Booking.objects.create(user=self.user, trip=self.trip)
        self.assertEqual(booking.status, 'Partially Confirmed')

    def test_default_amounts(self):
        booking = Booking.objects.create(user=self.user, trip=self.trip)
        self.assertEqual(booking.amount, Decimal('0.00'))
        self.assertEqual(booking.balance_amount, Decimal('0.00'))

    def test_scuba_default(self):
        booking = Booking.objects.create(user=self.user, trip=self.trip)
        self.assertFalse(booking.scuba_included)


class PaxRecordModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='paxuser', password='pass123')
        self.package = Package.objects.create(name='Beach Package', duration='2 Days')
        self.trip = Trip.objects.create(
            package=self.package,
            start_date=date.today() + timedelta(days=20),
            end_date=date.today() + timedelta(days=22),
        )
        self.booking = Booking.objects.create(user=self.user, trip=self.trip)
        self.pax_record = PaxRecord.objects.create(booking=self.booking, pax=3)

    def test_str(self):
        result = str(self.pax_record)
        self.assertIn('Pax record', result)

    def test_pax_value(self):
        self.assertEqual(self.pax_record.pax, 3)


class CustomerDetailModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='custuser', password='pass123')
        self.package = Package.objects.create(name='Hill Package', duration='4 Days')
        self.trip = Trip.objects.create(
            package=self.package,
            start_date=date.today() + timedelta(days=15),
            end_date=date.today() + timedelta(days=19),
        )
        self.booking = Booking.objects.create(user=self.user, trip=self.trip)
        self.pax_record = PaxRecord.objects.create(booking=self.booking, pax=1)
        self.customer = CustomerDetail.objects.create(
            pax_record=self.pax_record,
            name='John Doe',
            contact_number='9876543210',
            pick_up_point='Pune',
            meal_option='Veg',
            watersports_option='None',
            package_cost=Decimal('5000.00'),
            discounted_package_cost=Decimal('4000.00'),
        )

    def test_str(self):
        result = str(self.customer)
        self.assertIn('John Doe', result)
        self.assertIn('Hill Package', result)

    def test_fields(self):
        self.assertEqual(self.customer.name, 'John Doe')
        self.assertEqual(self.customer.contact_number, '9876543210')
        self.assertEqual(self.customer.pick_up_point, 'Pune')
        self.assertEqual(self.customer.package_cost, Decimal('5000.00'))


class PaymentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='payuser', password='pass123')
        self.package = Package.objects.create(name='Scuba Package', duration='3 Days')
        self.trip = Trip.objects.create(
            package=self.package,
            start_date=date.today() + timedelta(days=25),
            end_date=date.today() + timedelta(days=28),
        )
        self.booking = Booking.objects.create(user=self.user, trip=self.trip)
        self.payment = Payment.objects.create(
            booking=self.booking,
            payment_id='pay_test123',
            order_id='order_test456',
            signature='sig_test789',
            amount=Decimal('5000.00'),
            payment_method='Razorpay',
        )

    def test_str(self):
        result = str(self.payment)
        self.assertIn('pay_test123', result)

    def test_default_status(self):
        self.assertEqual(self.payment.status, 'Created')

    def test_amount(self):
        self.assertEqual(self.payment.amount, Decimal('5000.00'))
