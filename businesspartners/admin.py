from django.contrib import admin
from .models import BusinessPartnerProfile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'status')
    search_fields = ('first_name', 'last_name', 'email', 'status')

admin.site.register(BusinessPartnerProfile, ProfileAdmin)
