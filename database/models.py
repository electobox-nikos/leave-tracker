from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    last_updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Last updated at")
    )

    class Meta:
        abstract = True

class UserRole(models.TextChoices):
    ADMIN = "admin", _("Admin")
    EMPLOYEE = "employee", _("Employee")
    NONE = "none", _("None")

class User(BaseModel, AbstractUser):
    """
    Represents a user of the system.
    """

    role = models.CharField(
        max_length=8,
        choices=UserRole.choices,
        verbose_name=_("Role"),
        default=UserRole.NONE,
    )

class BusinessYear(BaseModel):
    """
    Represents a business year of the system.
    """
    year = models.IntegerField(verbose_name=_("Year"))

    def __str__(self):
        return f"{self.year}"


class AvailableLeave(BaseModel):
    """
    Represents a available leave of the system.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    business_year = models.ForeignKey(BusinessYear, on_delete=models.CASCADE, verbose_name=_("Business year"))
    days = models.IntegerField(verbose_name=_("Days"))
    used_days = models.IntegerField(verbose_name=_("Used days"), default=0)

    def __str__(self):
        return f"{self.user.username} - {self.business_year.year} - {self.days}"


class LeaveType(BaseModel):
    """
    Represents a leave type of the system.
    """
    name = models.CharField(max_length=255, verbose_name=_("Name"))

    def __str__(self):
        return f"{self.name}"

class LeaveStatus(models.TextChoices):
    """
    Represents a status of a leave.
    """
    PENDING = "pending", _("Pending")
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")
    CANCELLED = "cancelled", _("Cancelled")
    
class Leave(BaseModel):
    """
    Represents a leave of the system.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, verbose_name=_("Leave type"))
    start_date = models.DateField(verbose_name=_("Start date"))
    end_date = models.DateField(verbose_name=_("End date"))
    days = models.IntegerField(verbose_name=_("Days"))
    business_year = models.ForeignKey(BusinessYear, on_delete=models.CASCADE, verbose_name=_("Business year"))
    status = models.CharField(
        max_length=9,
        choices=LeaveStatus.choices,
        verbose_name=_("Status"),
        default=LeaveStatus.PENDING,
    )

    def __str__(self):
        return f"{self.user.username} - {self.leave_type.name} - {self.start_date} - {self.end_date} - {self.status}"