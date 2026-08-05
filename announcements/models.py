from django.db import models
from django.utils import timezone

from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


class AnnouncementQuerySet(models.QuerySet):
    def visible(self):
        today = timezone.localdate()
        return self.filter(is_active=True).filter(
            models.Q(expires_on__isnull=True) | models.Q(expires_on__gte=today)
        )


@register_snippet
class Announcement(models.Model):
    """
    A single message in the homepage announcement ticker (the scrolling
    strip between the hero and "Discover DHPP"). Add as many as you
    like — they all scroll together. Untick "Is active" or set an
    expiry date to stop one showing without deleting it.
    """

    text = models.CharField(max_length=300)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional small thumbnail shown next to this announcement in the ticker.",
    )
    link = models.CharField(
        max_length=500,
        blank=True,
        help_text="Optional. Where clicking this announcement should go — e.g. /tenders/ or a full https:// URL.",
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    expires_on = models.DateField(
        null=True,
        blank=True,
        help_text="Optional — the announcement stops showing after this date.",
    )

    objects = AnnouncementQuerySet.as_manager()

    panels = [
        FieldPanel("text"),
        FieldPanel("image"),
        FieldPanel("link"),
        FieldPanel("order"),
        FieldPanel("is_active"),
        FieldPanel("expires_on"),
    ]

    class Meta:
        ordering = ["order", "-id"]
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"

    def __str__(self):
        return self.text
