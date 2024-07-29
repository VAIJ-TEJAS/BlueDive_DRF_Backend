from django.contrib import admin
from .models import Option, Event, Day, EventRecord, DayRecord, Package

class OptionInline(admin.TabularInline):
    model = Option
    extra = 1

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'standard_option', 'description', 'compulsory')
    list_filter = ('compulsory',)
    search_fields = ('name', 'description')
    inlines = [OptionInline]

class OptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'event')
    list_filter = ('event',)
    search_fields = ('name', 'event__name')

class DayAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'number')
    ordering = ('number',)

class EventRecordAdmin(admin.ModelAdmin):
    list_display = ('number', 'event', 'day')
    list_filter = ('event', 'day')
    search_fields = ('event__name', 'day__name')

class DayRecordAdmin(admin.ModelAdmin):
    list_display = ('number', 'day', 'package')
    list_filter = ('day', 'package')
    search_fields = ('day__name', 'package__name')

class DayRecordInline(admin.TabularInline):
    model = DayRecord
    extra = 1

class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'description', 'pax_4_price', 'pax_3_price', 'pax_2_price')
    inlines = [DayRecordInline]
    search_fields = ('name', 'description')

admin.site.register(Event, EventAdmin)
admin.site.register(Option, OptionAdmin)
admin.site.register(Day, DayAdmin)
admin.site.register(EventRecord, EventRecordAdmin)
admin.site.register(DayRecord, DayRecordAdmin)
admin.site.register(Package, PackageAdmin)
