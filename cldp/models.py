from django.db import models

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.contrib.settings.models import BaseGenericSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.models import Orderable
from wagtail.snippets.models import register_snippet


@register_snippet
class CLDPActivity(ClusterableModel):
    """
    A single Community & Local Development Plan activity (a training,
    workshop, or programme run under the CLDP). Admins manage these
    from Snippets — the homepage shows the 4 most recent, and the
    full CLD Dashboard page (/cldp/) lists all of them.
    """

    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("in_progress", "In Progress"),
        ("upcoming", "Upcoming"),
    ]

    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="upcoming")
    date = models.DateField(help_text="Used for ordering and for choosing the 4 shown on the homepage.")
    description = models.TextField(blank=True)

    target_participants = models.PositiveIntegerField(default=0)
    actual_participants = models.PositiveIntegerField(default=0)
    male_participants = models.PositiveIntegerField(default=0)
    female_participants = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel("title"),
        FieldPanel("location"),
        FieldPanel("status"),
        FieldPanel("date"),
        FieldPanel("description"),
        FieldPanel("target_participants"),
        FieldPanel("actual_participants"),
        FieldPanel("male_participants"),
        FieldPanel("female_participants"),
        InlinePanel("images", label="Photos"),
    ]

    class Meta:
        ordering = ["-date"]
        verbose_name = "CLDP Activity"
        verbose_name_plural = "CLDP Activities"

    def __str__(self):
        return self.title

    @property
    def participation_rate(self):
        if not self.target_participants:
            return None
        return round((self.actual_participants / self.target_participants) * 100)


class CLDPActivityImage(Orderable):
    activity = ParentalKey(CLDPActivity, on_delete=models.CASCADE, related_name="images")
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        related_name="+",
    )
    caption = models.CharField(max_length=255, blank=True)

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]


def cldp_dashboard_stats(activities):
    """
    Aggregate stats for the CLD Dashboard, computed from the full set
    of activities passed in (not just whichever subset is displayed),
    so the numbers can't drift out of sync with the activity records.
    """
    activities = list(activities)
    total_target = sum(a.target_participants for a in activities)
    total_actual = sum(a.actual_participants for a in activities)
    return {
        "total": len(activities),
        "completed": sum(1 for a in activities if a.status == "completed"),
        "in_progress": sum(1 for a in activities if a.status == "in_progress"),
        "upcoming": sum(1 for a in activities if a.status == "upcoming"),
        "success_rate": round((total_actual / total_target) * 100) if total_target else None,
    }


@register_setting
class CLDPSettings(BaseGenericSetting):
    """
    Single editable slot for the CLD Dashboard's intro paragraph
    (e.g. announcing new partner MoUs). Update the text here whenever
    it changes — no need to touch a template.
    """

    intro_text = models.TextField(
        blank=True,
        help_text="Intro paragraph shown at the top of the CLD Dashboard, on the homepage and on /cldp/.",
    )

    panels = [
        FieldPanel("intro_text"),
    ]

    class Meta:
        verbose_name = "CLD Dashboard Settings"
