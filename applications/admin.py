from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.contrib import messages

class OwnedAdmin(admin.ModelAdmin):
    """Auto-fills the User ForeignKey with request.user on create, for any model."""
    def get_owner_field(self):
        # first FK pointing at the user model (User, user, owner... whatever it's called)
        for f in self.model._meta.fields:
            if f.is_relation and f.related_model is get_user_model():
                return f.name
        return None

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        owner = self.get_owner_field()
        if owner and owner not in fields:
            fields.append(owner)   # shown but not editable, so the form doesn't demand it
        return fields

    def get_list_display(self, request):
        list = [f.name for f in self.model._meta.fields]
        if 'id' in list:
            list.remove('id')
        return list

    def save_model(self, request, obj, form, change):
        owner = self.get_owner_field()
        if owner and not change:
            setattr(obj, owner, request.user)
        try:
            super().save_model(request, obj, form, change)
        except IntegrityError:
            messages.error(request, "Error: A record with this User exists. Duplicate entries are not allowed.")

    def delete_queryset(self, request, queryset):
        for obj in queryset:       # runs each model's own delete() (e.g. file cleanup)
            obj.delete()

# Register every other model in the app with the shared admin
for model in apps.get_app_config(__package__).get_models():
    if model not in admin.site._registry:
        admin.site.register(model, OwnedAdmin)