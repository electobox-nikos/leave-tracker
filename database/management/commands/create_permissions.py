from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from database.models import AvailableLeave

class Command(BaseCommand):
    """
    Creates (or updates) the default permission groups for the leave-tracking
    app.

    • Business Admin → all permissions on Leave
    • Employee      → “add” + “view” permissions only
    """

    help = "Create or update default permission groups for leave tracking"

    # --------------------------------------------------------------------- #
    #  Setup
    # --------------------------------------------------------------------- #
    leave_model_label = "database.Leave"       # ↩️  CHANGE to your app’s label

    groups = {
        "Business Admin": "all",              # full CRUD + approve/reject
        "Employee": ["add_leave", "view_leave", "view_availableleave"],
    }

    # --------------------------------------------------------------------- #
    #  Implementation
    # --------------------------------------------------------------------- #
    def handle(self, *args, **options):
        self.stdout.write("Creating / updating permission groups…")

        Leave = apps.get_model(*self.leave_model_label.split("."))
        leave_ct: ContentType = ContentType.objects.get_for_model(Leave)
        available_leave_ct: ContentType = ContentType.objects.get_for_model(AvailableLeave)
        all_permss = Permission.objects.filter(content_type__in=[leave_ct, available_leave_ct])

        # All permissions that belong to Leave (built-ins + custom)
        leave_perms = Permission.objects.filter(content_type=leave_ct)
        available_leave_perms = Permission.objects.filter(content_type=available_leave_ct)
        perms_by_code = {p.codename: p for p in all_permss}

        for group_name, wanted in self.groups.items():
            group, _ = Group.objects.get_or_create(name=group_name)

            if wanted == "all":
                perm_set = list(leave_perms)
                perm_set.extend(available_leave_perms)
            else:
                # Ensure every codename exists, fail loudly if not
                missing = [code for code in wanted if code not in perms_by_code]
                if missing:
                    raise RuntimeError(
                        f"Permissions not found on {Leave._meta.model_name}: {missing}"
                    )
                perm_set = [perms_by_code[code] for code in wanted]

            group.permissions.set(perm_set)
            group.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓ {group_name}: {len(perm_set)} permission(s) assigned."
                )
            )

        self.stdout.write(self.style.SUCCESS("Done."))
