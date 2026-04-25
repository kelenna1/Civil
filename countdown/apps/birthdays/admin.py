from django.contrib import admin
from .models import Birthday, BirthdayImport


@admin.register(Birthday)
class BirthdayAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'date_of_birth', 'organization', 'is_active', 'created_at')
    list_filter = ('is_active', 'organization')
    search_fields = ('full_name',)
    date_hierarchy = 'date_of_birth'


@admin.register(BirthdayImport)
class BirthdayImportAdmin(admin.ModelAdmin):
    list_display = ('organization', 'status', 'records_added', 'records_skipped', 'uploaded_at')
    list_filter = ('status', 'organization')
    readonly_fields = ('uploaded_at', 'status_detail')
