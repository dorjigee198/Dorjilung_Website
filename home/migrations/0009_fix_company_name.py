from django.db import migrations

# StreamField data migrations don't reconstruct block definitions
# reliably through Django's historical model state, so this imports
# the real model directly, same as 0007/0008.
from home.models import ProjectPage

OLD_NAME = "Dorjilung Hydro Power Limited"
NEW_NAME = "Dorjilung Hydroelectric Power Limited"


def fix_company_name(apps, schema_editor):
    """
    The company name appeared three ways across the site ("Dorjilung
    Hydro Power Limited", "Dorjilung Hydroelectric Power Limited", and
    "Dorjilung Hydropower Company Limited") — standardizing on the
    second everywhere. Templates were fixed directly; this catches the
    one occurrence living in the ProjectPage StreamField body, editing
    the raw stream data in place rather than reconstructing the whole
    body (as 0007/0008 do) so this migration stays independent of
    whatever content admins may have already changed since.
    """
    page = ProjectPage.objects.get(slug="project")
    raw = page.body.raw_data
    changed = False
    for block in raw:
        if block["type"] == "bullet_list":
            items = block["value"].get("items", [])
            for i, item in enumerate(items):
                if OLD_NAME in item:
                    items[i] = item.replace(OLD_NAME, NEW_NAME)
                    changed = True
    if changed:
        page.body = raw
        page.save()


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_update_projectpage_specs'),
    ]

    operations = [
        migrations.RunPython(fix_company_name, migrations.RunPython.noop),
    ]
