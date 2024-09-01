from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from package import views as package_views
from trip import views as trip_views  
from booking import views as booking_views 
from payment import views as payment_views
from user import views as user_views 

router = DefaultRouter()
router.register(r'packages-overview', package_views.PackageOverviewViewSet, basename='packages-overview')
router.register(r'packages-trips', package_views.PackageTripsViewSet, basename='packages-trips')
router.register(r'packages', package_views.PackageViewSet,  basename='packages')
router.register(r'trips', trip_views.TripViewSet,  basename='trips')
router.register(r'bookings', booking_views.BookingViewSet,  basename='bookings')  
router.register(r'payments', payment_views.BookingPaymentViewset, basename='payments')
router.register(r'user', user_views.UserViewSet, basename='user')


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include(router.urls)),
    path('send-otp/', user_views.SendOtpView.as_view(),name='send_otp'),
    path('verify-otp/', user_views.VerifyOtpView.as_view(), name='verify_otp')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
