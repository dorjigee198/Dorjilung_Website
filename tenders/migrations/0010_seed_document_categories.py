from django.db import migrations

# (name, sort_order, collapsed_by_default) — a starter set. Admins can add,
# rename, reorder or delete these under Snippets → Document categories.
SEED_CATEGORIES = [
    ("Tender Notice", 10, False),
    ("Bidding Document", 20, False),
    ("BOQ / Price Schedule", 30, False),
    ("Drawings", 40, False),
    ("Annexures", 50, True),
    ("Addendum / Clarification", 60, False),
]


def seed(apps, schema_editor):
    DocumentCategory = apps.get_model("tenders", "DocumentCategory")
    for name, sort_order, collapsed in SEED_CATEGORIES:
        DocumentCategory.objects.get_or_create(
            name=name,
            defaults={"sort_order": sort_order, "collapsed_by_default": collapsed},
        )


def unseed(apps, schema_editor):
    DocumentCategory = apps.get_model("tenders", "DocumentCategory")
    DocumentCategory.objects.filter(
        name__in=[name for name, _, _ in SEED_CATEGORIES]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("tenders", "0009_documentcategory_and_more"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
