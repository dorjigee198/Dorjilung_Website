from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseGenericSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.snippets.models import register_snippet


@register_snippet
class BoardMember(models.Model):
    """
    A Board of Directors member, shown in a permanent photo grid right
    under "Organizational Hierarchy" — unlike Department/TeamMember
    below, this isn't tucked behind a click-to-expand accordion, since
    the board is meant to be visible at a glance. Order controls both
    display order and row placement (the homepage shows the first 3 in
    one row, the rest in the next), so keep the chairman first.
    """

    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("designation"),
        FieldPanel("photo"),
        FieldPanel("order"),
    ]

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Board Member"
        verbose_name_plural = "Board Members"

    def __str__(self):
        return f"{self.name} — {self.designation}"


@register_snippet
class Department(models.Model):
    """
    A group in the organogram (e.g. "Board of Directors", "Top
    Leadership", "Statutory Committees"). Admins can add new
    departments freely from Snippets — the homepage just renders
    whatever exists here, in order.
    """

    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("order"),
    ]

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


@register_snippet
class TeamMember(models.Model):
    """
    A single person listed under a Department, shown when that
    department's dropdown is expanded on the homepage.
    """

    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="members"
    )
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel("department"),
        FieldPanel("name"),
        FieldPanel("role"),
        FieldPanel("email"),
        FieldPanel("photo"),
        FieldPanel("order"),
    ]

    class Meta:
        ordering = ["department__order", "order", "name"]

    def __str__(self):
        return f"{self.name} — {self.role}"


@register_setting
class OrganogramSettings(BaseGenericSetting):
    """
    Single editable slot for the organizational hierarchy chart image.
    Admins replace the image here whenever the structure changes —
    no need to create a new record each time.
    """

    chart_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("chart_image"),
    ]

    class Meta:
        verbose_name = "Organogram Chart"
