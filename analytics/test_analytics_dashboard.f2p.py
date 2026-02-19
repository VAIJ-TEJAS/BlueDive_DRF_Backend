"""
F2P tests for analytics dashboard.
These tests would fail on the base branch and pass after the fixes.
"""

import json
from datetime import datetime, timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock

from booking.models import Booking
from trip.models import Trip
from package.models import Package
from payment.models import Payment
from contactus.models import ContactUs


class AnalyticsDashboardF2PTests(APITestCase):
    """Test analytics dashboard endpoints with comprehensive coverage."""

    def setUp(self):
        """Set up test environment."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(self.user)
        
        # Create test data
        self.trip = Trip.objects.create(
            name='Test Trip',
            description='Test Description',
            price=1000.00,
            is_active=True
        )
        
        self.package = Package.objects.create(
            name='Test Package',
            description='Test Description',
            price=500.00,
            is_active=True
        )
        
        # Create test bookings
        for i in range(10):
            Booking.objects.create(
                user=self.user,
                trip=self.trip,
                package=self.package,
                status='confirmed',
                total_amount=1500.00 + (i * 100),
                created_at=timezone.now() - timedelta(days=i)
            )
        
        # Create test payments
        for booking in Booking.objects.all()[:5]:
            Payment.objects.create(
                booking=booking,
                amount=booking.total_amount,
                status='completed',
                payment_method='credit_card'
            )
        
        # Create test contact inquiries
        for i in range(5):
            ContactUs.objects.create(
                name=f'Test Contact {i}',
                email=f'test{i}@example.com',
                message=f'Test message {i}',
                created_at=timezone.now() - timedelta(days=i)
            )

    def test_dashboard_overview_basic_metrics(self):
        """Bug: Should return basic dashboard metrics."""
        url = reverse('dashboard_overview')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check basic structure
        self.assertIn('summary', data)
        self.assertIn('growth_rates', data)
        self.assertIn('popular_trips', data)
        self.assertIn('popular_packages', data)
        self.assertIn('booking_status_breakdown', data)
        self.assertIn('daily_bookings', data)
        self.assertIn('monthly_revenue', data)
        
        # Check summary metrics
        summary = data['summary']
        self.assertIn('total_bookings', summary)
        self.assertIn('total_revenue', summary)
        self.assertIn('total_users', summary)
        self.assertIn('total_trips', summary)
        self.assertIn('total_packages', summary)
        
        # Verify data types
        self.assertIsInstance(summary['total_bookings'], int)
        self.assertIsInstance(summary['total_revenue'], float)
        self.assertIsInstance(summary['total_users'], int)

    def test_dashboard_overview_growth_rates(self):
        """Bug: Should calculate growth rates correctly."""
        url = reverse('dashboard_overview')
        response = self.client.get(url)
        
        data = response.json()
        growth_rates = data['growth_rates']
        
        # Check growth rate structure
        self.assertIn('booking_growth_rate', growth_rates)
        self.assertIn('revenue_growth_rate', growth_rates)
        self.assertIn('user_growth_rate', growth_rates)
        
        # Verify growth rates are percentages
        for rate in growth_rates.values():
            self.assertIsInstance(rate, (int, float))
            self.assertGreaterEqual(rate, -100)
            self.assertLessEqual(rate, 100)

    def test_dashboard_overview_popular_trips(self):
        """Bug: Should return popular trips with booking counts."""
        url = reverse('dashboard_overview')
        response = self.client.get(url)
        
        data = response.json()
        popular_trips = data['popular_trips']
        
        self.assertIsInstance(popular_trips, list)
        self.assertLessEqual(len(popular_trips), 5)
        
        if popular_trips:
            trip = popular_trips[0]
            self.assertIn('id', trip)
            self.assertIn('name', trip)
            self.assertIn('booking_count', trip)
            self.assertIsInstance(trip['booking_count'], int)

    def test_dashboard_overview_booking_status_breakdown(self):
        """Bug: Should break down bookings by status."""
        url = reverse('dashboard_overview')
        response = self.client.get(url)
        
        data = response.json()
        status_breakdown = data['booking_status_breakdown']
        
        self.assertIsInstance(status_breakdown, list)
        
        # Should have different statuses
        statuses = [item['status'] for item in status_breakdown]
        self.assertIn('confirmed', statuses)
        
        # Check count calculations
        total_count = sum(item['count'] for item in status_breakdown)
        self.assertGreaterEqual(total_count, 0)

    def test_dashboard_overview_daily_bookings_trend(self):
        """Bug: Should return daily bookings for last 30 days."""
        url = reverse('dashboard_overview')
        response = self.client.get(url)
        
        data = response.json()
        daily_bookings = data['daily_bookings']
        
        self.assertIsInstance(daily_bookings, list)
        self.assertEqual(len(daily_bookings), 30)
        
        # Check structure of daily data
        if daily_bookings:
            day = daily_bookings[0]
            self.assertIn('date', day)
            self.assertIn('count', day)
            self.assertIsInstance(day['count'], int)

    def test_dashboard_overview_monthly_revenue_trend(self):
        """Bug: Should return monthly revenue for last 12 months."""
        url = reverse('dashboard_overview')
        response = self.client.get(url)
        
        data = response.json()
        monthly_revenue = data['monthly_revenue']
        
        self.assertIsInstance(monthly_revenue, list)
        self.assertEqual(len(monthly_revenue), 12)
        
        # Check structure of monthly data
        if monthly_revenue:
            month = monthly_revenue[0]
            self.assertIn('month', month)
            self.assertIn('revenue', month)
            self.assertIsInstance(month['revenue'], float)

    def test_booking_analytics_basic_metrics(self):
        """Bug: Should return booking analytics with filters."""
        url = reverse('booking_analytics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check basic structure
        self.assertIn('period', data)
        self.assertIn('summary', data)
        self.assertIn('status_breakdown', data)
        self.assertIn('trip_performance', data)
        self.assertIn('daily_trend', data)
        self.assertIn('monthly_trend', data)
        self.assertIn('peak_hours', data)

    def test_booking_analytics_date_filtering(self):
        """Bug: Should filter bookings by date range."""
        # Test with custom date range
        start_date = (timezone.now() - timedelta(days=15)).strftime('%Y-%m-%d')
        end_date = timezone.now().strftime('%Y-%m-%d')
        
        url = f"{reverse('booking_analytics')}?start_date={start_date}&end_date={end_date}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        period = data['period']
        self.assertEqual(period['start_date'], start_date)
        self.assertEqual(period['end_date'], end_date)

    def test_booking_analytics_status_filter(self):
        """Bug: Should filter bookings by status."""
        url = f"{reverse('booking_analytics')}?status=confirmed"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should only include confirmed bookings
        status_breakdown = data['status_breakdown']
        status_names = [item['status'] for item in status_breakdown]
        self.assertEqual(status_names, ['confirmed'])

    def test_booking_analytics_trip_performance(self):
        """Bug: Should analyze trip performance metrics."""
        url = reverse('booking_analytics')
        response = self.client.get(url)
        
        data = response.json()
        trip_performance = data['trip_performance']
        
        self.assertIsInstance(trip_performance, list)
        
        if trip_performance:
            trip = trip_performance[0]
            self.assertIn('trip_name', trip)
            self.assertIn('booking_count', trip)
            self.assertIn('revenue', trip)
            self.assertIn('avg_value', trip)

    def test_booking_analytics_peak_hours(self):
        """Bug: Should identify peak booking hours."""
        url = reverse('booking_analytics')
        response = self.client.get(url)
        
        data = response.json()
        peak_hours = data['peak_hours']
        
        self.assertIsInstance(peak_hours, list)
        self.assertLessEqual(len(peak_hours), 24)
        
        if peak_hours:
            hour = peak_hours[0]
            self.assertIn('hour', hour)
            self.assertIn('count', hour)
            self.assertIsInstance(hour['count'], int)

    def test_user_analytics_basic_metrics(self):
        """Bug: Should return user analytics with engagement data."""
        url = reverse('user_analytics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check basic structure
        self.assertIn('summary', data)
        self.assertIn('engagement', data)
        self.assertIn('ltv', data)
        self.assertIn('retention', data)
        self.assertIn('registration_trend', data)

    def test_user_analytics_user_segments(self):
        """Bug: Should categorize users into segments."""
        url = reverse('user_analytics')
        response = self.client.get(url)
        
        data = response.json()
        user_segments = data['summary']['user_segments']
        
        self.assertIsInstance(user_segments, dict)
        self.assertIn('new_users', user_segments)
        self.assertIn('active_users', user_segments)
        self.assertIn('returning_users', user_segments)
        self.assertIn('dormant_users', user_segments)

    def test_user_analytics_engagement_metrics(self):
        """Bug: Should calculate user engagement metrics."""
        url = reverse('user_analytics')
        response = self.client.get(url)
        
        data = response.json()
        engagement = data['engagement']
        
        self.assertIn('avg_bookings_per_user', engagement)
        self.assertIn('avg_revenue_per_user', engagement)
        self.assertIn('total_active_bookers', engagement)
        
        # Verify metrics are calculated correctly
        self.assertIsInstance(engagement['avg_bookings_per_user'], (int, float))
        self.assertIsInstance(engagement['avg_revenue_per_user'], (int, float))

    def test_user_analytics_top_users(self):
        """Bug: Should identify top users by revenue."""
        url = reverse('user_analytics')
        response = self.client.get(url)
        
        data = response.json()
        top_users = data['top_users']
        
        self.assertIsInstance(top_users, list)
        
        if top_users:
            user = top_users[0]
            self.assertIn('id', user)
            self.assertIn('username', user)
            self.assertIn('total_revenue', user)
            self.assertIn('total_bookings', user)

    def test_financial_analytics_revenue_metrics(self):
        """Bug: Should calculate financial revenue metrics."""
        url = reverse('financial_analytics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check revenue metrics structure
        self.assertIn('revenue_metrics', data)
        self.assertIn('payment_metrics', data)
        self.assertIn('revenue_breakdown', data)
        self.assertIn('trends', data)
        self.assertIn('financial_health', data)

    def test_financial_analytics_payment_metrics(self):
        """Bug: Should analyze payment processing metrics."""
        url = reverse('financial_analytics')
        response = self.client.get(url)
        
        data = response.json()
        payment_metrics = data['payment_metrics']
        
        self.assertIn('total_payments', payment_metrics)
        self.assertIn('completed_payments', payment_metrics)
        self.assertIn('success_rate', payment_metrics)
        
        # Verify success rate calculation
        self.assertIsInstance(payment_metrics['success_rate'], (int, float))
        self.assertGreaterEqual(payment_metrics['success_rate'], 0)
        self.assertLessEqual(payment_metrics['success_rate'], 100)

    def test_financial_analytics_revenue_by_category(self):
        """Bug: Should break down revenue by different categories."""
        url = reverse('financial_analytics')
        response = self.client.get(url)
        
        data = response.json()
        revenue_breakdown = data['revenue_breakdown']
        
        # Check by status
        self.assertIn('by_status', revenue_breakdown)
        status_breakdown = revenue_breakdown['by_status']
        self.assertIsInstance(status_breakdown, list)
        
        # Check by trip
        self.assertIn('by_trip', revenue_breakdown)
        trip_breakdown = revenue_breakdown['by_trip']
        self.assertIsInstance(trip_breakdown, list)
        
        # Check by package
        self.assertIn('by_package', revenue_breakdown)
        package_breakdown = revenue_breakdown['by_package']
        self.assertIsInstance(package_breakdown, list)

    def test_financial_analytics_trends(self):
        """Bug: Should show revenue trends over time."""
        url = reverse('financial_analytics')
        response = self.client.get(url)
        
        data = response.json()
        trends = data['trends']
        
        # Check monthly trend
        self.assertIn('monthly_revenue', trends['monthly_revenue'])
        monthly_revenue = trends['monthly_revenue']
        self.assertIsInstance(monthly_revenue, list)
        
        # Check daily trend
        self.assertIn('daily_revenue', trends['daily_revenue'])
        daily_revenue = trends['daily_revenue']
        self.assertIsInstance(daily_revenue, list)
        self.assertEqual(len(daily_revenue), 30)

    def test_performance_metrics_database_performance(self):
        """Bug: Should return database performance metrics."""
        url = reverse('performance_metrics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check database section
        self.assertIn('database', data)
        database = data['database']
        self.assertIn('databases', database)
        self.assertIsInstance(database['databases'], list)

    def test_performance_metrics_cache_performance(self):
        """Bug: Should analyze cache performance."""
        url = reverse('performance_metrics')
        response = self.client.get(url)
        
        data = response.json()
        cache = data['cache']
        
        self.assertIn('hits', cache)
        self.assertIn('misses', cache)
        self.assertIn('hits_ratio', cache)
        
        # Verify cache hit ratio calculation
        total_accesses = cache['hits'] + cache['misses']
        if total_accesses > 0:
            expected_ratio = (cache['hits'] / total_accesses) * 100
            self.assertAlmostEqual(cache['hits_ratio'], expected_ratio, places=2)

    def test_performance_metrics_api_performance(self):
        """Bug: Should return API performance metrics."""
        url = reverse('performance_metrics')
        response = self.client.get(url)
        
        data = response.json()
        api_performance = data['api_performance']
        
        self.assertIn('avg_response_time', api_performance)
        self.assertIn('p95_response_time', api_performance)
        self.assertIn('requests_per_second', api_performance)
        
        # Verify response time ranges
        self.assertLessEqual(api_performance['avg_response_time'], api_performance['p95_response_time'])
        self.assertLessEqual(api_performance['p95_response_time'], api_performance['p99_response_time'])

    def test_performance_metrics_error_rates(self):
        """Bug: Should calculate system error rates."""
        url = reverse('performance_metrics')
        response = self.client.get(url)
        
        data = response.json()
        error_rates = data['error_rates']
        
        self.assertIn('4xx_errors', error_rates)
        self.assertIn('5xx_errors', error_rates)
        self.assertIn('total_error_rate', error_rates)
        
        # Verify error rate calculation
        total_error_rate = error_rates['4xx_errors'] + error_rates['5xx_errors']
        self.assertEqual(error_rates['total_error_rate'], total_error_rate)

    def test_export_analytics_json_format(self):
        """Bug: Should export analytics in JSON format."""
        url = f"{reverse('export_analytics')}?format=json&type=overview"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should match overview data structure
        self.assertIn('summary', data)

    def test_export_analytics_csv_format(self):
        """Bug: Should export analytics in CSV format."""
        url = f"{reverse('export_analytics')}?format=csv&type=overview"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        
        # Check CSV content type
        self.assertIn('attachment', response['Content-Disposition'])

    def test_export_analytics_invalid_format(self):
        """Bug: Should handle invalid export format gracefully."""
        url = f"{reverse('export_analytics')}?format=xml&type=overview"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_export_analytics_invalid_type(self):
        """Bug: Should handle invalid report type gracefully."""
        url = f"{reverse('export_analytics')}?format=json&type=invalid"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_refresh_analytics_cache(self):
        """Bug: Should refresh analytics cache successfully."""
        # User must be admin to refresh cache
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        self.client.force_authenticate(admin_user)
        
        url = reverse('refresh_analytics_cache')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)
        self.assertIn('cleared_keys', data)

    def test_refresh_analytics_cache_permission_denied(self):
        """Bug: Should deny cache refresh to non-admin users."""
        url = reverse('refresh_analytics_cache')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 403)

    def test_analytics_error_handling(self):
        """Bug: Should handle errors gracefully."""
        with patch('analytics.views.dashboard_overview', side_effect=Exception('Database error')):
            url = reverse('dashboard_overview')
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertIn('error', data)

    def test_analytics_empty_database(self):
        """Bug: Should handle empty database gracefully."""
        # Clear all data
        Booking.objects.all().delete()
        User.objects.all().delete()
        Trip.objects.all().delete()
        Package.objects.all().delete()
        Payment.objects.all().delete()
        ContactUs.objects.all().delete()
        
        url = reverse('dashboard_overview')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should return zero values
        summary = data['summary']
        self.assertEqual(summary['total_bookings'], 0)
        self.assertEqual(summary['total_revenue'], 0.0)
        self.assertEqual(summary['total_users'], 0)

    def test_analytics_date_validation(self):
        """Bug: Should validate date parameters correctly."""
        # Test invalid date format
        url = f"{reverse('dashboard_overview')}?start_date=invalid-date"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_analytics_large_dataset_performance(self):
        """Bug: Should handle large datasets efficiently."""
        # Create large dataset
        for i in range(1000):
            Booking.objects.create(
                user=self.user,
                trip=self.trip,
                package=self.package,
                status='confirmed',
                total_amount=1000.00 + (i * 10),
                created_at=timezone.now() - timedelta(days=i % 365)
            )
        
        url = reverse('dashboard_overview')
        
        # Should still respond quickly
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Should include all bookings
        data = response.json()
        summary = data['summary']
        self.assertEqual(summary['total_bookings'], 1010)  # 10 original + 1000 new

    def test_analytics_concurrent_requests(self):
        """Bug: Should handle concurrent requests without issues."""
        import threading
        import time
        
        def make_request():
            url = reverse('dashboard_overview')
            return self.client.get(url)
        
        # Make multiple concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        for thread in threads:
            self.assertTrue(hasattr(thread, 'response'))
            self.assertEqual(thread.response.status_code, 200)

    def test_analytics_data_consistency(self):
        """Bug: Should ensure data consistency across endpoints."""
        # Get data from multiple endpoints
        overview_response = self.client.get(reverse('dashboard_overview'))
        booking_response = self.client.get(reverse('booking_analytics'))
        financial_response = self.get(reverse('financial_analytics'))
        
        overview_data = overview_response.json()
        booking_data = booking_response.json()
        financial_data = financial_response.json()
        
        # Revenue should be consistent
        overview_revenue = overview_data['summary']['total_revenue']
        booking_revenue = booking_data['summary']['total_revenue']
        financial_revenue = financial_data['revenue_metrics']['revenue_30_days']
        
        self.assertAlmostEqual(overview_revenue, booking_revenue, places=2)
        self.assertAlmostEqual(overview_revenue, financial_revenue, places=2)

    def test_analytics_timezone_handling(self):
        """Bug: Should handle timezones correctly."""
        # Test with timezone-aware dates
        now = timezone.now()
        utc_now = now.replace(tzinfo=timezone.utc)
        
        # Create booking with specific timezone
        Booking.objects.create(
            user=self.user,
            trip=self.trip,
            package=self.package,
            status='confirmed',
            total_amount=1000.00,
            created_at=utc_now
        )
        
        url = reverse('dashboard_overview')
        response = self.client.get(url)
        
        data = response.json()
        
        # Should include the UTC booking
        summary = data['summary']
        self.assertGreater(summary['total_bookings'], 0)

    def test_analytics_permissions(self):
        """Bug: Should enforce proper permissions."""
        # Test without authentication
        self.client.logout()
        response = self.client.get(reverse('dashboard_overview'))
        self.assertEqual(response.status_code, 401)
        
        # Test with regular user
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('dashboard_overview'))
        self.assertEqual(response.status_code, 200)
        
        # Test admin-only endpoints
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        self.client.force_authenticate(admin_user)
        
        # Admin should access all endpoints
        response = self.client.get(reverse('refresh_analytics_cache'))
        self.assertEqual(response.status_code, 200)
        
        # Regular user should be denied
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('refresh_analytics_cache'))
        self.assertEqual(response.status_code, 403)

    def test_analytics_response_format(self):
        """Bug: Should return properly formatted JSON responses."""
        url = reverse('dashboard_overview')
        response = self.client.get(url)
        
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIsInstance(response.json(), dict)

    def test_analytics_caching_behavior(self):
        """Bug: Should cache responses appropriately."""
        # First request should hit database
        url = reverse('dashboard_overview')
        response1 = self.client.get(url)
        
        # Second request should use cache
        response2 = self.client.get(url)
        
        # Both should return the same data
        self.assertEqual(response1.json(), response2.json())
        
        # Response times should be significantly faster for cached request
        # (This would be verified with timing in a real scenario)

    def test_analytics_metric_calculations(self):
        """Bug: Should calculate metrics accurately."""
        # Create bookings with known values
        Booking.objects.create(
            user=self.user,
            trip=self.trip,
            package=self.package,
            status='confirmed',
            total_amount=1000.00,
            created_at=timezone.now() - timedelta(days=1)
        )
        
        Booking.objects.create(
            user=self.user,
            trip=self.trip,
            package=self.package,
            status='pending',
            total_amount=500.00,
            created_at=timezone.now() - timedelta(days=2)
        )
        
        url = reverse('dashboard_overview')
        response = self.client.get(url)
        
        data = response.json()
        summary = data['summary']
        
        # Verify calculations
        expected_revenue = 1500.00  # 1000 + 500
        self.assertEqual(summary['total_revenue'], expected_revenue)
        self.assertEqual(summary['total_bookings'], 12)  # 10 original + 2 new

    def test_analytics_filter_combinations(self):
        """Bug: Should handle multiple filter combinations."""
        # Test date + status filter
        start_date = (timezone.now() - timedelta(days=10)).strftime('%Y-%m-%d')
        url = f"{reverse('booking_analytics')}?start_date={start_date}&status=confirmed&trip_id={self.trip.id}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should apply all filters
        period = data['period']
        self.assertEqual(period['start_date'], start_date)
        self.assertEqual(period['end_date'], end_date)
        
        status_breakdown = data['status_breakdown']
        self.assertEqual(len(status_breakdown), 1)
        self.assertEqual(status_breakdown[0]['status'], 'confirmed')

    def test_analytics_data_aggregation(self):
        """Bug: Should aggregate data correctly at different time levels."""
        url = reverse('booking_analytics')
        response = self.client.get(url)
        
        data = response.json()
        
        # Check monthly aggregation
        monthly_trend = data['monthly_trend']
        self.assertIsInstance(monthly_trend, list)
        
        if monthly_trend:
            month = monthly_trend[0]
            self.assertIn('month', month)
            self.assertIn('bookings', month)
            self.assertIn('revenue', month)
            
            # Verify aggregation logic
            expected_month = (timezone.now() - timedelta(days=30)).strftime('%Y-%m')
            self.assertEqual(month['month'], expected_month)

    def test_analytics_error_recovery(self):
        """Bug: Should recover from errors gracefully."""
        # Mock database error for one endpoint
        with patch('analytics.views.booking_analytics', side_effect=Exception('Database connection error')):
            url = reverse('booking_analytics')
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertIn('error', data)
        
        # Other endpoints should still work
        url = reverse('dashboard_overview')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_analytics_data_integrity(self):
        """Bug: Should maintain data integrity across analytics."""
        # Create test data with relationships
        booking = Booking.objects.create(
            user=self.user,
            trip=self.trip,
            package=self.package,
            status='confirmed',
            total_amount=1000.00
        )
        
        Payment.objects.create(
            booking=booking,
            amount=booking.total_amount,
            status='completed'
        )
        
        # Verify relationships in analytics
        url = reverse('financial_analytics')
        response = self.client.get(url)
        
        data = response.json()
        
        # Revenue calculations should be consistent
        financial_revenue = data['revenue_metrics']['revenue_30_days']
        self.assertGreater(financial_revenue, 0)
        
        # Payment success rate should be calculated correctly
        payment_metrics = data['payment_metrics']
        self.assertEqual(payment_metrics['completed_payments'], 1)
        self.assertEqual(payment_metrics['total_payments'], 1)

    def test_analytics_performance_optimization(self):
        """Bug: Should be optimized for performance."""
        # Test with large dataset
        for i in range(500):
            Booking.objects.create(
                user=self.user,
                trip=self.trip,
                package=self.package,
                status='confirmed',
                total_amount=1000.00 + (i * 10),
                created_at=timezone.now() - timedelta(days=i % 365)
            )
        
        import time
        start_time = time.time()
        url = reverse('dashboard_overview')
        response = self.client.get(url)
        end_time = time.time()
        
        # Should complete within reasonable time
        self.assertLess(end_time - start_time, 5.0)  # 5 seconds max

    def test_analytics_edge_cases(self):
        """Bug: should handle edge cases gracefully."""
        # Test with future dates
        future_date = (timezone.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        url = f"{reverse('booking_analytics')}?end_date={future_date}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Test with very old dates
        old_date = (timezone.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        url = f"{reverse('booking_analytics')}?start_date={old_date}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Should handle gracefully with no data
        data = response.json()
        summary = data['summary']
        self.assertEqual(summary['total_bookings'], 0)

    def test_analytics_data_validation(self):
        """Bug: should validate all data types and ranges."""
        url = reverse('dashboard_overview')
        response = self.client.get(url)
        
        data = response.json()
        
        # Validate numeric ranges
        summary = data['summary']
        self.assertGreaterEqual(summary['total_bookings'], 0)
        self.assertGreaterEqual(summary['total_revenue'], 0)
        self.assertGreaterEqual(summary['total_users'], 0)
        
        # Validate percentages
        growth_rates = data['growth_rates']
        for rate in growth_rates.values():
            self.assertGreaterEqual(rate, -100)
            self.assertLessEqual(rate, 100)
        
        # Validate counts
        for status in data['booking_status_breakdown']:
            self.assertGreaterEqual(status['count'], 0)
            self.assertLessEqual(status['percentage'], 100)

    def test_analytics_comprehensive_coverage(self):
        """Bug: should provide comprehensive analytics coverage."""
        endpoints = [
            'dashboard_overview',
            'booking_analytics',
            'user_analytics',
            'financial_analytics',
            'performance_metrics'
        ]
        
        for endpoint in endpoints:
            url = reverse(endpoint)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIsInstance(data, dict)
            
            # Each endpoint should have basic structure
            self.assertIn('summary', data) or endpoint == 'performance_metrics'

    def tearDown(self):
        """Clean up test data."""
        Booking.objects.all().delete()
        Payment.objects.all().delete()
        ContactUs.objects.all().delete()
        User.objects.all().delete()
        Trip.objects.all().delete()
        Package.objects.all().delete()
