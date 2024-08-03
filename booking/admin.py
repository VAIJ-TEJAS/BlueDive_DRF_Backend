import nested_admin
from django.contrib import admin
from .models import Booking, PaxRecord, CustomerDetail, Payment

class CustomerDetailInline(nested_admin.NestedStackedInline):
    model = CustomerDetail
    extra = 1  

class PaymentInline(nested_admin.NestedStackedInline):
    model = Payment
    extra = 1  

class PaxRecordInline(nested_admin.NestedStackedInline):
    model = PaxRecord
    extra = 1  
    inlines = [CustomerDetailInline] 

class BookingAdmin(nested_admin.NestedModelAdmin):
    list_display = ('user', 'trip', 'booking_date', 'status', 'scuba_included')
    search_fields = ('user__username', 'trip__package__name')
    list_filter = ('status', 'booking_date')
    inlines = [PaxRecordInline, PaymentInline]

admin.site.register(Booking, BookingAdmin)
