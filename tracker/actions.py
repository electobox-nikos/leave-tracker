from django.contrib import messages
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe

def reset_password(modeladmin, request, queryset):
    """
    Reset the password of selected users to a 10-digit password containing only uppercase characters and numbers.
    """
    count = 0
    generated_passwords = {}
    for user in queryset:
        generated_password = get_random_string(
            length=10, allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        )
        user.set_password(generated_password)
        user.save()
        generated_passwords[user.username] = generated_password
        count += 1
    credentials_message = "".join(
        f"<li style='padding:0; background:none; display:list-item;'><span style='font-weight:bold;'>Username: </span>{username} | <span style='font-weight:bold;'>Password: </span>{password}</li>"
        for username, password in generated_passwords.items()
    )
    modeladmin.message_user(
        request,
        f"Password reset to a 10-digit password containing only uppercase characters and numbers for {count} users.",
        level=messages.SUCCESS,
    )
    modeladmin.message_user(
        request,
        mark_safe(
            f"The generated passwords for the selected users are: <ul>{credentials_message}</ul>"
        ),
        level=messages.SUCCESS,
    )


reset_password.short_description = "Reset Password"