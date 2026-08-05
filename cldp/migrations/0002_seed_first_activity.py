from django.db import migrations


def seed_activity(apps, schema_editor):
    CLDPActivity = apps.get_model("cldp", "CLDPActivity")
    CLDPActivity.objects.get_or_create(
        title="Home Electrical Wiring Refresher Course (Rangjung)",
        defaults=dict(
            location="Rangjung",
            status="completed",
            date="2026-07-01",
            target_participants=25,
            actual_participants=22,
            male_participants=22,
            female_participants=0,
        ),
    )


def remove_activity(apps, schema_editor):
    CLDPActivity = apps.get_model("cldp", "CLDPActivity")
    CLDPActivity.objects.filter(
        title="Home Electrical Wiring Refresher Course (Rangjung)"
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("cldp", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_activity, remove_activity),
    ]
