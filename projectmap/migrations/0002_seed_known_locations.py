from django.db import migrations

LOCATIONS = [
    dict(
        name="Dam Site",
        location_type="dam_site",
        latitude=27.7287,
        longitude=91.1364,
        description=(
            "Located on the Kurichhu River, approximately 7 km downstream "
            "of Autsho and 1 km upstream of Rewan village."
        ),
        order=1,
    ),
    dict(
        name="Powerhouse",
        location_type="powerhouse",
        latitude=27.2625,
        longitude=91.1730,
        description=(
            "An underground facility located 16 km downstream from the dam "
            "site, near Lingmethang township in Mongar Dzongkhag."
        ),
        order=2,
    ),
]


def seed_locations(apps, schema_editor):
    ProjectLocation = apps.get_model("projectmap", "ProjectLocation")
    for location in LOCATIONS:
        ProjectLocation.objects.get_or_create(
            name=location["name"], defaults=location
        )


def remove_locations(apps, schema_editor):
    ProjectLocation = apps.get_model("projectmap", "ProjectLocation")
    ProjectLocation.objects.filter(
        name__in=[loc["name"] for loc in LOCATIONS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("projectmap", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_locations, remove_locations),
    ]
