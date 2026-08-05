from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class EnvironmentSocialDocument(models.Model):
    """
    A single downloadable document (ESIA, ESMP, SEP, RAP, etc.) shown in
    the homepage "Environment & Social Documents" list. Admins upload
    these from the Wagtail admin (Snippets > Environment & Social
    Documents) — no code changes needed to add a new document.
    """

    CATEGORY_CHOICES = [
        ("environment", "Environment"),
        ("social", "Social"),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    document = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    uploaded_at = models.DateField(auto_now_add=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("category"),
        FieldPanel("document"),
    ]

    class Meta:
        ordering = ["category", "title"]
        verbose_name = "Environment & Social Document"
        verbose_name_plural = "Environment & Social Documents"

    def __str__(self):
        return self.title
