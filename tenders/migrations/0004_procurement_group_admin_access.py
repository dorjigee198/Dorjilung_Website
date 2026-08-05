from django.db import migrations


def add_admin_access(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    try:
        group = Group.objects.get(name="Procurement")
    except Group.DoesNotExist:
        return

    # Page-level permissions alone aren't enough — without this, a
    # Procurement-group member is bounced straight to the login page and
    # can never reach the admin at all, regardless of what they're
    # allowed to do once inside.
    access_admin = Permission.objects.get(
        content_type__app_label="wagtailadmin", codename="access_admin"
    )
    group.permissions.add(access_admin)


def remove_admin_access(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    try:
        group = Group.objects.get(name="Procurement")
    except Group.DoesNotExist:
        return

    access_admin = Permission.objects.get(
        content_type__app_label="wagtailadmin", codename="access_admin"
    )
    group.permissions.remove(access_admin)


class Migration(migrations.Migration):

    dependencies = [
        ("tenders", "0003_procurement_group"),
    ]

    operations = [
        migrations.RunPython(add_admin_access, remove_admin_access),
    ]
