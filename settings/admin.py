from django.contrib import admin

from settings.models import Settings

class SingletonModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False if self.model.objects.exists() else True

admin.site.register(Settings, SingletonModelAdmin)
