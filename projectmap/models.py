from django import forms
from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class ProjectLocation(models.Model):
    """
    A pin on the homepage project map (dam site, powerhouse, main
    office, etc). Admins manage these from Snippets — add, move, or
    edit a pin without touching code.
    """

    LOCATION_TYPE_CHOICES = [
        ("dam_site", "Dam Site"),
        ("powerhouse", "Powerhouse"),
        ("main_office", "Main Office"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=255)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPE_CHOICES)
    latitude = models.FloatField(
        help_text="Decimal degrees only, e.g. 27.7287 — not the whole \"27.7287, 91.1364\" pair from Google Maps.",
    )
    longitude = models.FloatField(
        help_text="Decimal degrees only, e.g. 91.1364 — no ° symbol or N/E/S/W letters.",
    )
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("location_type"),
        # A plain text input, not the browser's native number input — the
        # latter silently empties itself (no validation error at all) if
        # it receives anything other than digits/a single decimal point,
        # which is exactly what happens when someone pastes a coordinate
        # copied straight from Google Maps (comma-separated pair, or a
        # value with a ° symbol). A text input lets Django's own
        # validation give a clear "Enter a number" message instead.
        FieldPanel("latitude", widget=forms.TextInput),
        FieldPanel("longitude", widget=forms.TextInput),
        FieldPanel("description"),
        FieldPanel("order"),
    ]

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Project Map Location"
        verbose_name_plural = "Project Map Locations"

    def __str__(self):
        return self.name
