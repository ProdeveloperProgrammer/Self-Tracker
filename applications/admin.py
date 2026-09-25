from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(MovieAndSeries)
admin.site.register(DailyJournel)
admin.site.register(SiteDiscovery)

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('Title', 'Provider', 'Proof','User')
    def save_model(self, request, obj, form, change):
        # If this is a new certificate being created (not an update)
        if not change:
            obj.User = request.user  # Automatically attach the logged-in admin user
            
        super().save_model(request, obj, form, change)
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()