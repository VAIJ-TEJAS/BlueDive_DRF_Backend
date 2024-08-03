from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from package import views as package_views
from trip import views as trip_views  
from booking import views as booking_views 
from user import views as user_views 

router = DefaultRouter()
router.register(r'options', package_views.OptionViewSet)
router.register(r'events', package_views.EventViewSet)
router.register(r'days', package_views.DayViewSet)
router.register(r'event_records', package_views.EventRecordViewSet)
router.register(r'day_records', package_views.DayRecordViewSet)
router.register(r'packages', package_views.PackageViewSet)
router.register(r'trips', trip_views.TripViewSet)
router.register(r'bookings', booking_views.BookingViewSet)  

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include(router.urls)),
    path('send-otp/', user_views.SendOtpView.as_view(),name='send_otp'),
    path('verify-otp/', user_views.VerifyOtpView.as_view(), name='verify_otp')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
