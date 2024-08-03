from django.contrib import admin
from .models import Option, Event, Day, EventRecord, DayRecord, Package, PaxOptions

class OptionInline(admin.TabularInline):
    model = Option
    extra = 1

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'standard_option', 'description')
    search_fields = ('name', 'description')
    inlines = [OptionInline]

class OptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'event')
    list_filter = ('event',)
    search_fields = ('name', 'event__name')

class DayRecordInline(admin.TabularInline):
    model = DayRecord
    extra = 1

class EventRecordInline(admin.TabularInline):
    model = EventRecord
    extra = 1

class PaxOptionsInline(admin.StackedInline):  
    model = PaxOptions
    extra = 1

class DayAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    inlines = [EventRecordInline]  

class EventRecordAdmin(admin.ModelAdmin):
    list_display = ('event', 'day')
    list_filter = ('event', 'day')
    search_fields = ('event__name', 'day__name')

class DayRecordAdmin(admin.ModelAdmin):
    list_display = ('day', 'package')
    list_filter = ('day', 'package')
    search_fields = ('day__name', 'package__name')

class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'description')
    inlines = [DayRecordInline, PaxOptionsInline]
    search_fields = ('name', 'description')

admin.site.register(Event, EventAdmin)
# admin.site.register(Option, OptionAdmin)
admin.site.register(Day, DayAdmin)
# admin.site.register(EventRecord, EventRecordAdmin)
# admin.site.register(DayRecord, DayRecordAdmin)
admin.site.register(Package, PackageAdmin)
