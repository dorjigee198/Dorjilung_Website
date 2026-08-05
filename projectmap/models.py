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
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("location_type"),
        FieldPanel("latitude"),
        FieldPanel("longitude"),
        FieldPanel("description"),
        FieldPanel("order"),
    ]

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Project Map Location"
        verbose_name_plural = "Project Map Locations"

    def __str__(self):
        return self.name
