from django.db import migrations

PERMISSION_CODENAMES = ("add_page", "change_page", "publish_page")


def create_procurement_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")
    GroupPagePermission = apps.get_model("wagtailcore", "GroupPagePermission")
    TenderIndexPage = apps.get_model("tenders", "TenderIndexPage")

    group, _ = Group.objects.get_or_create(name="Procurement")

    # Scope the group to the tenders subtree only: granting permissions on
    # TenderIndexPage covers it and everything created under it (i.e. every
    # TenderPage, since TenderPage can only be created there). The group
    # gets no other page or admin permissions.
    tender_index = TenderIndexPage.objects.order_by("pk").first()
    if not tender_index:
        return

    page_content_type = ContentType.objects.get(app_label="wagtailcore", model="page")
    for codename in PERMISSION_CODENAMES:
        permission = Permission.objects.get(content_type=page_content_type, codename=codename)
        GroupPagePermission.objects.get_or_create(
            group=group,
            page_id=tender_index.pk,
            permission=permission,
        )


def remove_procurement_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name="Procurement").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("tenders", "0002_tender_restructure"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("wagtailcore", "0097_baselogentry_uuid_action_timestamp_indexes"),
    ]

    operations = [
        migrations.RunPython(create_procurement_group, remove_procurement_group),
    ]
