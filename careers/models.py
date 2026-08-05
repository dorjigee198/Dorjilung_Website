import urllib.parse

from django.db import models
from django.utils import timezone

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable
from wagtail.snippets.models import register_snippet

STATUS_OPEN = "open"
STATUS_CLOSED = "closed"
STATUS_CANCELLED = "cancelled"

STATUS_LABELS = {
    STATUS_OPEN: "Open",
    STATUS_CLOSED: "Closed",
    STATUS_CANCELLED: "Cancelled",
}


@register_snippet
class JobOpening(ClusterableModel):
    """
    A single job posting on the Careers page. Admins manage these
    from Snippets — status (Open/Closed) is computed from the closing
    date, not set manually, so it can't go stale.
    """

    EMPLOYMENT_TYPE_CHOICES = [
        ("full_time", "Full-time"),
        ("part_time", "Part-time"),
        ("contract", "Contract"),
        ("internship", "Internship"),
    ]

    title = models.CharField(max_length=255)
    department = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default="full_time")
    closing_date = models.DateField()
    description = RichTextField(blank=True)
    contact_email = models.EmailField()
    cancelled = models.BooleanField(
        default=False,
        help_text="Tick to withdraw this posting, regardless of its closing date.",
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("department"),
        FieldPanel("location"),
        FieldPanel("employment_type"),
        FieldPanel("closing_date"),
        FieldPanel("contact_email"),
        FieldPanel("cancelled"),
        FieldPanel("description"),
        InlinePanel("documents", label="Documents (job description, ToR, etc.)"),
    ]

    class Meta:
        verbose_name = "Job Opening"
        verbose_name_plural = "Job Openings"

    def __str__(self):
        return self.title

    @property
    def computed_status(self):
        if self.cancelled:
            return STATUS_CANCELLED
        if timezone.now().date() <= self.closing_date:
            return STATUS_OPEN
        return STATUS_CLOSED

    @property
    def status_label(self):
        return STATUS_LABELS[self.computed_status]

    @property
    def mailto_link(self):
        subject = f"Application for {self.title}"
        return f"mailto:{self.contact_email}?subject={urllib.parse.quote(subject)}"


class JobOpeningDocument(Orderable):
    """
    A single downloadable file on a job posting — the job description,
    Terms of Reference, or any other PDF applicants should read.
    """

    job = ParentalKey(JobOpening, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=255, help_text='e.g. "Job Description" or "Terms of Reference"')
    document = models.ForeignKey(
        "wagtaildocs.Document",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("document"),
    ]
