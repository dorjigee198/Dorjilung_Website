from django.db import migrations

CATEGORIES = [
    dict(name="Land Acquisition & Compensation", order=1),
    dict(name="Resettlement", order=2),
    dict(name="Environmental Impact", order=3),
    dict(name="Employment & Labour", order=4),
    dict(name="Community Health & Safety", order=5),
    dict(name="Cultural Heritage", order=6),
    dict(name="Corruption / Ethics", order=7),
    dict(name="Other", order=8),
]


def seed_categories(apps, schema_editor):
    GrievanceCategory = apps.get_model("grievance", "GrievanceCategory")
    for category in CATEGORIES:
        GrievanceCategory.objects.get_or_create(
            name=category["name"], defaults=category
        )


def remove_categories(apps, schema_editor):
    GrievanceCategory = apps.get_model("grievance", "GrievanceCategory")
    GrievanceCategory.objects.filter(
        name__in=[c["name"] for c in CATEGORIES]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("grievance", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_categories, remove_categories),
    ]
