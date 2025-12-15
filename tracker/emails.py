"""
Email utilities for leave notifications.
"""

from django.core.mail import send_mail
from django.conf import settings
from database.models import Leave, LeaveStatus
from leavetracker.settings import EMAIL_ADMIN_EMAILS


# Email addresses to notify when a leave is created
ADMIN_EMAILS = [
    email for email in EMAIL_ADMIN_EMAILS
]


def send_leave_created_notification(leave: Leave):
    """
    Send email notification when a new leave request is created.
    Sends to the user who created the leave and to admin emails.
    """
    subject = f"New Leave Request: {leave.leave_type.name}"

    message = f"""
A new leave request has been submitted:

Employee: {leave.user.get_full_name() or leave.user.username} ({leave.user.email})
Leave Type: {leave.leave_type.name}
Start Date: {leave.start_date}
End Date: {leave.end_date}
Days: {leave.days}
Business Year: {leave.business_year.year}
Status: {leave.get_status_display()}
"""

    if leave.description:
        message += f"\nDescription:\n{leave.description}\n"

    # Recipients: the user who created the leave (if they have an email) + admin emails
    recipients = ADMIN_EMAILS.copy()
    if leave.user.email:
        recipients.insert(0, leave.user.email)

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False,
    )


def send_leave_status_change_notification(leave: Leave, old_status: str):
    """
    Send email notification when a leave request status changes.
    Sends to the user who created the leave and to admin emails.
    """
    status_display = leave.get_status_display()
    old_status_display = dict(LeaveStatus.choices).get(old_status, old_status)

    subject = f"Leave Request {status_display}: {leave.leave_type.name}"

    message = f"""
The status of your leave request has been updated:

Employee: {leave.user.get_full_name() or leave.user.username} ({leave.user.email})
Leave Type: {leave.leave_type.name}
Start Date: {leave.start_date}
End Date: {leave.end_date}
Days: {leave.days}
Business Year: {leave.business_year.year}
Previous Status: {old_status_display}
New Status: {status_display}
"""

    if leave.description:
        message += f"\nDescription:\n{leave.description}\n"

    # Recipients: the user who created the leave (if they have an email) + admin emails
    recipients = ADMIN_EMAILS.copy()
    if leave.user.email:
        recipients.insert(0, leave.user.email)

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False,
    )
