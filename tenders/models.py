import urllib.parse

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import Truncator

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index
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
class DocumentCategory(models.Model):
    """
    A heading that tender documents can be grouped under on the tender page
    (e.g. "Annexures", "Addendum / Clarification", "BOQ / Price Schedule").
    Managed by admins under Snippets - a starter set is seeded by migration,
    and new categories can be added at any time.
    """

    name = models.CharField(max_length=100, unique=True)
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first on the tender page.",
    )
    collapsed_by_default = models.BooleanField(
        default=False,
        help_text="Start this group collapsed on the tender page. Useful for "
        "long lists such as annexures.",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("sort_order"),
        FieldPanel("collapsed_by_default"),
    ]

    class Meta:
        verbose_name = "Document category"
        verbose_name_plural = "Document categories"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


@register_snippet
class TenderGroup(models.Model):
    """
    An optional grouping for related tenders (e.g. every package and
    addendum belonging to "DCP-I"). On the /tenders/ list the group's
    tenders are shown together in one collapsible panel. A tender with no
    group is listed on its own. Groups and lone tenders are ordered
    against each other by how recently they were published, so a group
    jumps to the top whenever a new tender is added to it.
    """

    name = models.CharField(max_length=150, unique=True)
    description = models.CharField(
        max_length=300,
        blank=True,
        help_text="Optional one-line note shown under the group heading.",
    )
    collapsed_by_default = models.BooleanField(
        default=False,
        help_text="Start this panel collapsed on the tender list.",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("collapsed_by_default"),
    ]

    class Meta:
        verbose_name = "Tender group"
        verbose_name_plural = "Tender groups"
        ordering = ["name"]

    def __str__(self):
        return self.name


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
            .select_related("group")
            .prefetch_related("sub_tenders", "documents", "extensions", "notices")
        )
        if query:
            tenders_qs = tenders_qs.filter(
                Q(title__icontains=query) | Q(reference_no__icontains=query)
            )
        tenders = list(tenders_qs)

        # "Publish Date" is an editable field, so admins reorder a tender by
        # adjusting it; pk is the tiebreaker so newer entries with an
        # identical publish date still sort above older ones.
        def newest_first(t):
            return (t.publish_date, t.pk)

        open_tenders = sorted(
            (t for t in tenders if t.computed_status == STATUS_OPEN),
            key=newest_first,
            reverse=True,
        )
        other_tenders = sorted(
            (t for t in tenders if t.computed_status != STATUS_OPEN),
            key=newest_first,
            reverse=True,
        )

        def as_blocks(section_tenders):
            """Turn a newest-first tender list into a list of render blocks:
            one per lone (ungrouped) tender, one per tender group present.
            Groups and lone tenders are interleaved by recency — a group
            takes the publish date of its newest tender — so whatever was
            published most recently is on top, group or not."""
            grouped = {}
            blocks = []
            for tender in section_tenders:
                if tender.group_id:
                    grouped.setdefault(tender.group, []).append(tender)
                else:
                    blocks.append(
                        {"is_group": False, "sort_key": newest_first(tender), "tender": tender}
                    )
            for group, members in grouped.items():
                blocks.append(
                    {
                        "is_group": True,
                        "sort_key": newest_first(members[0]),  # members already newest-first
                        "group": group,
                        "tenders": members,
                        "collapsed": group.collapsed_by_default,
                    }
                )
            blocks.sort(key=lambda b: b["sort_key"], reverse=True)
            return blocks

        context["open_tenders"] = open_tenders
        context["other_tenders"] = other_tenders
        context["open_blocks"] = as_blocks(open_tenders)
        context["other_blocks"] = as_blocks(other_tenders)
        context["query"] = query
        return context


class TenderPage(Page):
    """
    A single tender notice. Everything a visitor needs to read the
    tender, download its documents, and email procurement is on this
    page — there is no bidder login or online submission.
    """

    reference_no = models.CharField(max_length=255)
    summary = models.CharField(
        max_length=400,
        blank=True,
        help_text="One or two plain sentences shown under the tender title in "
        "the public tender list. If left blank, the start of the description "
        "below is used instead.",
    )
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
    group = models.ForeignKey(
        "tenders.TenderGroup",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tenders",
        help_text="Optional. Tenders sharing a group are shown together in one "
        "collapsible panel on the tender list. Manage groups under Snippets - "
        "Tender groups. Leave blank to list this tender on its own.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("reference_no"),
        FieldPanel("summary"),
        FieldPanel("group"),
        FieldPanel("publish_date"),
        FieldPanel("opening_date"),
        FieldPanel("closing_date"),
        FieldPanel("contact_email"),
        FieldPanel("cancelled"),
        FieldPanel("description"),
        InlinePanel("sub_tenders", label="Sub-tenders"),
        InlinePanel("documents", label="Documents"),
        InlinePanel("extensions", label="Extensions"),
        InlinePanel("notices", label="Notices"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("reference_no"),
        index.SearchField("summary"),
        index.SearchField("description"),
        index.FilterField("cancelled"),
    ]

    parent_page_types = ["tenders.TenderIndexPage"]
    subpage_types = []

    class Meta:
        # Newest tender first — matches the public listing order and keeps
        # the Wagtail admin explorer consistent with it.
        ordering = ["-publish_date"]

    @property
    def listing_summary(self):
        """Short teaser shown under the title on the /tenders/ list row.
        Uses the Summary field when set, otherwise falls back to the opening
        of the rich-text description with formatting stripped."""
        if self.summary:
            return self.summary
        return Truncator(strip_tags(self.description)).words(28, truncate="…")

    @property
    def latest_notice(self):
        """The most recent notice, if any — shown as a sticky note on the /tenders/ list row."""
        notices = list(self.notices.all())
        if not notices:
            return None
        return max(notices, key=lambda n: (n.date, n.pk))

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
        context["notices_newest_first"] = sorted(
            self.notices.all(), key=lambda n: (n.date, n.pk), reverse=True
        )

        # Documents are split three ways, in this order of precedence:
        #   1. a sub-tender name  -> grouped under that heading (flat list)
        #   2. a category         -> grouped under a collapsible category heading
        #   3. neither            -> shown as a plain flat list, no dropdown
        # Rows that are neither an upload nor a link are dropped so group
        # counts stay honest.
        docs = self.documents.filter(
            Q(document__isnull=False) | ~Q(external_url="")
        ).select_related("document", "category")
        sub_tender_documents = {}
        by_category = {}
        uncategorised_documents = []
        for doc in docs:
            if doc.sub_tender_name:
                sub_tender_documents.setdefault(doc.sub_tender_name, []).append(doc)
            elif doc.category_id:
                by_category.setdefault(doc.category, []).append(doc)
            else:
                uncategorised_documents.append(doc)

        category_document_groups = [
            {
                "name": category.name,
                "documents": group,
                "collapsed": category.collapsed_by_default,
            }
            for category, group in sorted(
                by_category.items(),
                key=lambda item: (item[0].sort_order, item[0].name.lower()),
            )
        ]

        context["uncategorised_documents"] = uncategorised_documents
        context["sub_tender_documents"] = sub_tender_documents
        context["category_document_groups"] = category_document_groups
        context["has_documents"] = bool(
            uncategorised_documents or sub_tender_documents or category_document_groups
        )
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
    A downloadable resource on a tender — either a file uploaded to the
    Wagtail document library, or an external link (e.g. a Google Drive
    folder). Exactly one of `document` / `external_url` is filled in.
    Superseded entries are never deleted — admins just add the
    replacement alongside.
    """

    page = ParentalKey(TenderPage, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(
        max_length=255,
        help_text="The label shown to visitors, e.g. \"Annexure J - Equipment "
        "list\" or \"Drawings (Google Drive)\".",
    )
    document = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Upload here for files hosted on this site. Leave blank if "
        "you are linking out with the field below.",
    )
    external_url = models.URLField(
        "External link",
        blank=True,
        help_text="Use instead of an upload to point at a file or folder hosted "
        "elsewhere (Google Drive, Dropbox, etc.). Opens in a new tab.",
    )
    category = models.ForeignKey(
        "tenders.DocumentCategory",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Groups this document under a collapsible heading on the "
        "tender page. Manage the list under Snippets - Document categories. "
        "Leave blank to list it under \"Other Documents\".",
    )
    sub_tender_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional — if this document belongs to a specific sub-tender, "
        "enter its title exactly as entered above so it can be grouped correctly. "
        "Takes precedence over Category.",
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("document"),
        FieldPanel("external_url"),
        FieldPanel("category"),
        FieldPanel("sub_tender_name"),
    ]

    def clean(self):
        super().clean()
        if self.document_id and self.external_url:
            raise ValidationError(
                {
                    "external_url": "Fill in either an uploaded document or an "
                    "external link, not both."
                }
            )

    @property
    def href(self):
        """Where the row links to — the uploaded file, or the external URL."""
        if self.document_id:
            return self.document.url
        return self.external_url

    @property
    def is_external(self):
        return not self.document_id and bool(self.external_url)


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


class TenderNotice(Orderable):
    """
    A free-form update or announcement for a tender — a rescheduled
    pre-bid meeting, an issued addendum, a clarification, etc. Distinct
    from TenderExtension, which specifically changes the closing date
    and drives computed_status. Shown as a "sticky note": the single
    latest one on the tender's row in the /tenders/ list, and the full
    history (newest first) on the tender's own page.
    """

    page = ParentalKey(TenderPage, on_delete=models.CASCADE, related_name="notices")
    text = models.TextField(help_text='e.g. "Pre-bid meeting rescheduled to 15 March 2027."')
    date = models.DateField(default=timezone.now)
    document = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("text"),
        FieldPanel("date"),
        FieldPanel("document"),
    ]
