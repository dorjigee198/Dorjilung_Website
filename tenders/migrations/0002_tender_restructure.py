import django.db.models.deletion
import modelcluster.fields
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wagtaildocs", "0014_alter_document_file_size"),
        ("tenders", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="tenderpage", name="category"),
        migrations.RemoveField(model_name="tenderpage", name="status"),
        migrations.RemoveField(model_name="tenderpage", name="published_date"),
        migrations.RemoveField(model_name="tenderpage", name="deadline"),
        migrations.RemoveField(model_name="tenderpage", name="summary"),
        migrations.AlterField(
            model_name="tenderpage",
            name="reference_no",
            field=models.CharField(max_length=255),
        ),
        migrations.AddField(
            model_name="tenderpage",
            name="description",
            field=wagtail.fields.RichTextField(blank=True),
        ),
        migrations.AddField(
            model_name="tenderpage",
            name="opening_date",
            field=models.DateTimeField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="tenderpage",
            name="closing_date",
            field=models.DateTimeField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="tenderpage",
            name="contact_email",
            field=models.EmailField(default="", max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="tenderpage",
            name="cancelled",
            field=models.BooleanField(
                default=False,
                help_text="Tick to mark this tender cancelled, regardless of its closing date.",
            ),
        ),
        migrations.AlterModelOptions(
            name="tenderpage",
            options={"ordering": ["-closing_date"]},
        ),
        migrations.RemoveField(model_name="tenderdocument", name="label"),
        migrations.AddField(
            model_name="tenderdocument",
            name="title",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="tenderdocument",
            name="sub_tender_name",
            field=models.CharField(
                blank=True,
                help_text=(
                    "Optional — if this document belongs to a specific sub-tender, "
                    "enter its title exactly as entered above so it can be grouped "
                    "correctly."
                ),
                max_length=255,
            ),
        ),
        migrations.DeleteModel(name="TenderCategory"),
        migrations.CreateModel(
            name="SubTender",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                ("title", models.CharField(max_length=255)),
                ("reference_no", models.CharField(blank=True, max_length=255)),
                ("description", wagtail.fields.RichTextField(blank=True)),
                ("page", modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name="sub_tenders", to="tenders.tenderpage")),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TenderExtension",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                ("new_closing_date", models.DateTimeField()),
                ("issued_date", models.DateField()),
                ("remarks", models.TextField(blank=True)),
                ("notice", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="wagtaildocs.document")),
                ("page", modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name="extensions", to="tenders.tenderpage")),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]
