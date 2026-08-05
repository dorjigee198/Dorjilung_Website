import urllib.parse

from django.db import models
from django.db.models import Q
from django.utils import timezone

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index

STATUS_OPEN = "open"
STATUS_CLOSED = "closed"
STATUS_CANCELLED = "cancelled"

STATUS_LABELS = {
    STATUS_OPEN: "Open",
    STATUS_CLOSED: "Closed",
    STATUS_CANCELLED: "Cancelled",
}


class TenderIndexPage(Page):
    """
    The single public tender listing page, at /tenders/. The nav
    "Tenders" item points here. Admins only edit the intro text on this
    page — the list itself is always computed from published TenderPages.
    """

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["tenders.TenderPage"]
    max_count = 1

    def get_context(self, request):
        context = super().get_context(request)

        query = request.GET.get("q", "").strip()
        tenders_qs = (
            TenderPage.objects.live()
            .descendant_of(self)
            .prefetch_related("sub_tenders", "documents", "extensions")
        )
        if query:
            tenders_qs = tenders_qs.filter(
                Q(title__icontains=query) | Q(reference_no__icontains=query)
            )
        tenders = list(tenders_qs)

        open_tenders = sorted(
            (t for t in tenders if t.computed_status == STATUS_OPEN),
            key=lambda t: t.effective_closing_date,
        )
        other_tenders = sorted(
            (t for t in tenders if t.computed_status != STATUS_OPEN),
            key=lambda t: t.effective_closing_date,
            reverse=True,
        )

        context["open_tenders"] = open_tenders
        context["other_tenders"] = other_tenders
        context["query"] = query
        return context


class TenderPage(Page):
    """
    A single tender notice. Everything a visitor needs to read the
    tender, download its documents, and email procurement is on this
    page — there is no bidder login or online submission.
    """

    reference_no = models.CharField(max_length=255)
    description = RichTextField(blank=True)
    publish_date = models.DateTimeField(
        default=timezone.now,
        help_text="When this tender notice was actually published/announced — can differ from the opening date.",
    )
    opening_date = models.DateTimeField()
    closing_date = models.DateTimeField()
    contact_email = models.EmailField()
    cancelled = models.BooleanField(
        default=False,
        help_text="Tick to mark this tender cancelled, regardless of its closing date.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("reference_no"),
        FieldPanel("publish_date"),
        FieldPanel("opening_date"),
        FieldPanel("closing_date"),
        FieldPanel("contact_email"),
        FieldPanel("cancelled"),
        FieldPanel("description"),
        InlinePanel("sub_tenders", label="Sub-tenders"),
        InlinePanel("documents", label="Documents"),
        InlinePanel("extensions", label="Extensions"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("reference_no"),
        index.SearchField("description"),
        index.FilterField("cancelled"),
    ]

    parent_page_types = ["tenders.TenderIndexPage"]
    subpage_types = []

    class Meta:
        ordering = ["-closing_date"]

    @property
    def latest_extension(self):
        """The most recently issued extension, if any."""
        # extensions is prefetched as a plain list by the index view, so
        # sort in Python there; here (detail view, not prefetched) a
        # fresh query is fine.
        extensions = list(self.extensions.all())
        if not extensions:
            return None
        return max(extensions, key=lambda e: (e.issued_date, e.pk))

    @property
    def is_extended(self):
        return self.latest_extension is not None

    @property
    def effective_closing_date(self):
        extension = self.latest_extension
        return extension.new_closing_date if extension else self.closing_date

    @property
    def computed_status(self):
        if self.cancelled:
            return STATUS_CANCELLED
        if timezone.now() < self.effective_closing_date:
            return STATUS_OPEN
        return STATUS_CLOSED

    @property
    def status_label(self):
        return STATUS_LABELS[self.computed_status]

    @property
    def mailto_link(self):
        subject = f"{self.reference_no} - {self.title}"
        return f"mailto:{self.contact_email}?subject={urllib.parse.quote(subject)}"

    def get_context(self, request):
        context = super().get_context(request)

        context["extensions_newest_first"] = sorted(
            self.extensions.all(), key=lambda e: (e.issued_date, e.pk), reverse=True
        )

        grouped_documents = {}
        ungrouped_documents = []
        for doc in self.documents.all():
            if doc.sub_tender_name:
                grouped_documents.setdefault(doc.sub_tender_name, []).append(doc)
            else:
                ungrouped_documents.append(doc)
        context["grouped_documents"] = grouped_documents
        context["ungrouped_documents"] = ungrouped_documents
        return context


class SubTender(Orderable):
    """
    An optional sub-component of a larger tender (e.g. separate lots or
    packages within one procurement). A tender with none of these still
    renders normally — the section is just skipped.
    """

    page = ParentalKey(TenderPage, on_delete=models.CASCADE, related_name="sub_tenders")
    title = models.CharField(max_length=255)
    reference_no = models.CharField(max_length=255, blank=True)
    description = RichTextField(blank=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("reference_no"),
        FieldPanel("description"),
    ]


class TenderDocument(Orderable):
    """
    A single downloadable file on a tender. Superseded documents are
    never deleted — admins just add the replacement alongside it.
    """

    page = ParentalKey(TenderPage, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=255)
    document = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    sub_tender_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional — if this document belongs to a specific sub-tender, "
        "enter its title exactly as entered above so it can be grouped correctly.",
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("document"),
        FieldPanel("sub_tender_name"),
    ]


class TenderExtension(Orderable):
    """
    A record of a tender's closing date being pushed back. The most
    recently issued extension (by issued_date) determines the tender's
    effective closing date and therefore its computed status.
    """

    page = ParentalKey(TenderPage, on_delete=models.CASCADE, related_name="extensions")
    new_closing_date = models.DateTimeField()
    issued_date = models.DateField()
    remarks = models.TextField(blank=True)
    notice = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("new_closing_date"),
        FieldPanel("issued_date"),
        FieldPanel("remarks"),
        FieldPanel("notice"),
    ]
