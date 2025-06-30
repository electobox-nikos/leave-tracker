from django.contrib import admin
from database.models import User, BusinessYear, LeaveType, Leave, AvailableLeave
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from tracker.actions import reset_password
from database.models import UserRole
from database.models import LeaveStatus

class LimitUserChoicesMixin:
    """
    Mixin for ModelAdmin: employees can only pick themselves in user-related
    dropdowns; admins keep the full list.
    """
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        print(db_field.remote_field.model)
        if db_field.remote_field.model is User:
            print(request.user.role)
            if request.user.role == UserRole.EMPLOYEE and not request.user.is_superuser:
                kwargs["queryset"] = User.objects.filter(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Same for ManyToManyFields, if you need it:
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.remote_field.model is User:
            if request.user.role == UserRole.EMPLOYEE and not request.user.is_superuser:
                kwargs["queryset"] = User.objects.filter(pk=request.user.pk)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

class UserAdmin(BaseUserAdmin):
    list_display = BaseUserAdmin.list_display + ("role",)
    list_filter = BaseUserAdmin.list_filter + ("role",)
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Custom Fields",
            {
                "fields": ("role",),
            },
        ),
    )
    actions = [reset_password]

    # ↓ Only show the logged-in employee’s own row; admins see everyone
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == UserRole.EMPLOYEE and not request.user.is_superuser:
            return qs.filter(pk=request.user.pk)
        return qs

class BusinessYearAdmin(admin.ModelAdmin):
    list_display = ("year",)

class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)

class AvailableLeaveAdmin(LimitUserChoicesMixin, admin.ModelAdmin):
    list_display = ("user", "business_year", "days", "used_days")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == UserRole.EMPLOYEE and not request.user.is_superuser:
            return qs.filter(user=request.user)
        return qs


class LeaveAdmin(LimitUserChoicesMixin, admin.ModelAdmin):
    list_display = ["user", "leave_type", "start_date", "end_date", "status", "days"]
    list_filter = ["user", "status", "leave_type"]
    search_fields = ["user__first_name", "user__last_name", "user__email"]

    def get_readonly_fields(self, request, obj=None):
        if request.user.role == UserRole.EMPLOYEE:
            return ("status",)
        return ()
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == UserRole.EMPLOYEE and not request.user.is_superuser:
            return qs.filter(user=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        if obj.status == LeaveStatus.APPROVED:
            available_leave = AvailableLeave.objects.get(user=obj.user, business_year=obj.business_year)
            available_leave.used_days += obj.days
            available_leave.save()
        elif obj.status == LeaveStatus.CANCELLED:
            available_leave = AvailableLeave.objects.get(user=obj.user, business_year=obj.business_year)
            available_leave.used_days -= obj.days
            available_leave.save()
        super().save_model(request, obj, form, change)


admin.site.register(User, UserAdmin)
admin.site.register(BusinessYear, BusinessYearAdmin)
admin.site.register(LeaveType, LeaveTypeAdmin)
admin.site.register(Leave, LeaveAdmin)
admin.site.register(AvailableLeave, AvailableLeaveAdmin)

