from django.db import migrations

# New display order: Chairman alone in the top row, then two rows of
# three — matched by name rather than primary key so this applies
# correctly regardless of the exact IDs in a given database.
NEW_ORDER = [
    "Dasho Karma Tshering",
    "Dasho Leki Wangmo",
    "Dasho Chhewang Rinzin",
    "Dr. Praveer Sinha",
    "Dasho Lungten Jamtsho",
    "Ms. Anjali Pandey",
    "Mr. Kumar Pritam Kumar",
]


def reorder(apps, schema_editor):
    BoardMember = apps.get_model("structure", "BoardMember")
    for index, name in enumerate(NEW_ORDER, start=1):
        BoardMember.objects.filter(name=name).update(order=index)


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0002_boardmember'),
    ]

    operations = [
        migrations.RunPython(reorder, migrations.RunPython.noop),
    ]
