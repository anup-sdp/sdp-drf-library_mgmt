# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils import timezone

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'mobile_no', 'membership_date', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active', 'membership_date']
    search_fields = ['username', 'email', 'mobile_no']
    ordering = ['role', 'username']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'mobile_no', 'membership_date')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'mobile_no', 'membership_date')}),
    )
    
