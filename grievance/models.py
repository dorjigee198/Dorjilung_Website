from django.core.validators import FileExtensionValidator
from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class GrievanceCategory(models.Model):
    """
    An admin-defined grievance category (e.g. "Land Acquisition &
    Compensation", "Environmental Impact"). Shown in the category
    dropdown on the public grievance form — add, rename, or remove
    categories here at any time.
    """

    name = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("order"),
    ]

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Grievance Category"
        verbose_name_plural = "Grievance Categories"

    def __str__(self):
        return self.name


def grievance_audio_path(instance, filename):
    return f"grievances/audio/{filename}"


def grievance_video_path(instance, filename):
    return f"grievances/video/{filename}"


@register_snippet
class Grievance(models.Model):
    """
    A single grievance submitted through the public form at
    /grievance/. Contains personal details and, by default, only
    superusers can see this list in the Wagtail admin — no group has
    been granted access to it.
    """

    reference_no = models.CharField(max_length=20, unique=True, blank=True)
    is_anonymous = models.BooleanField(default=False)

    full_name = models.CharField(max_length=255, blank=True)
    cid_number = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    village_gewog = models.CharField(max_length=255, blank=True)

    category = models.ForeignKey(
        GrievanceCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="grievances",
    )
    description = models.TextField(blank=True)

    audio_file = models.FileField(
        upload_to=grievance_audio_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["mp3", "wav", "m4a", "ogg", "webm"])],
    )
    video_file = models.FileField(
        upload_to=grievance_video_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["mp4", "mov", "avi"])],
    )

    declaration_accepted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    panels = [
        FieldPanel("reference_no"),
        FieldPanel("is_anonymous"),
        FieldPanel("full_name"),
        FieldPanel("cid_number"),
        FieldPanel("email"),
        FieldPanel("phone"),
        FieldPanel("village_gewog"),
        FieldPanel("category"),
        FieldPanel("description"),
        FieldPanel("audio_file"),
        FieldPanel("video_file"),
    ]

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Grievance"
        verbose_name_plural = "Grievances"

    def __str__(self):
        return self.reference_no or f"Grievance #{self.pk}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new and not self.reference_no:
            year = self.submitted_at.year
            self.reference_no = f"GR-{year}-{self.pk:04d}"
            super().save(update_fields=["reference_no"])
