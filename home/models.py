from django.db import models

from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.snippets.models import register_snippet


class StatCardBlock(blocks.StructBlock):
    value = blocks.CharBlock(max_length=50, help_text='e.g. "1,125 MW"')
    label = blocks.CharBlock(max_length=100, help_text='e.g. "Installed Capacity"')

    class Meta:
        icon = "pick"


class StatCardsBlock(blocks.StructBlock):
    """A row of highlighted stat cards, e.g. capacity / commissioning year / cost."""

    cards = blocks.ListBlock(StatCardBlock())

    class Meta:
        icon = "pick"
        label = "Stat Highlight Cards"
        template = "home/blocks/stat_cards_block.html"


class SectionTextBlock(blocks.StructBlock):
    """A heading plus a paragraph or two of narrative text."""

    heading = blocks.CharBlock(max_length=255)
    text = blocks.RichTextBlock(features=["bold", "italic", "link", "ol", "ul"])

    class Meta:
        icon = "doc-full"
        label = "Text Section"
        template = "home/blocks/section_text_block.html"


class SpecRowBlock(blocks.StructBlock):
    label = blocks.CharBlock(max_length=100)
    value = blocks.CharBlock(max_length=100)


class SpecTableBlock(blocks.StructBlock):
    """A labelled table of technical spec rows, e.g. Hydrology, Reservoir, Dam & Spillway."""

    heading = blocks.CharBlock(max_length=255)
    rows = blocks.ListBlock(SpecRowBlock())

    class Meta:
        icon = "table"
        label = "Spec Table"
        template = "home/blocks/spec_table_block.html"


class BulletListBlock(blocks.StructBlock):
    """A labelled bullet list, e.g. Partnership & Financing, Socio-Economic."""

    heading = blocks.CharBlock(max_length=255, required=False)
    items = blocks.ListBlock(blocks.CharBlock(max_length=500))

    class Meta:
        icon = "list-ul"
        label = "Bullet List"
        template = "home/blocks/bullet_list_block.html"


class HomePage(Page):
    pass


class ProjectPage(Page):
    """
    The full project details page, at /project/. Linked from "Explore
    Project" (hero), "Learn More" (Project Introduction), and "View
    More" (Project Overview) on the homepage. Built from a StreamField
    so admins can add, reorder, or remove sections without a developer.
    """

    body = StreamField(
        [
            ("stat_cards", StatCardsBlock()),
            ("text_section", SectionTextBlock()),
            ("spec_table", SpecTableBlock()),
            ("bullet_list", BulletListBlock()),
        ],
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    parent_page_types = ["home.HomePage"]
    max_count = 1


@register_snippet
class Milestone(models.Model):
    """
    A single entry on the homepage's "Key Milestones" timeline. Admins
    manage these from Snippets — the homepage shows the 6 most recent
    (by sort_date), with the full list available via "View More".
    """

    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("in_progress", "In Progress"),
        ("upcoming", "Upcoming"),
    ]

    year_label = models.CharField(
        max_length=50,
        help_text='Displayed year or range, e.g. "2004" or "2022 – 2025".',
    )
    sort_date = models.DateField(
        help_text="Used only to order milestones chronologically — pick the start of the period shown above.",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="completed")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    panels = [
        FieldPanel("year_label"),
        FieldPanel("sort_date"),
        FieldPanel("status"),
        FieldPanel("title"),
        FieldPanel("description"),
    ]

    class Meta:
        ordering = ["sort_date"]
        verbose_name = "Key Milestone"
        verbose_name_plural = "Key Milestones"

    def __str__(self):
        return self.title


@register_snippet
class Achievement(models.Model):
    """
    A single entry on the homepage's "Key Achievements" cards. Admins
    manage these from Snippets — the homepage shows the 4 most recent
    (by date), with the full list available via "View More".
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField(help_text='Used for ordering, and displayed as e.g. "Jul 2026".')

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("date"),
    ]

    class Meta:
        ordering = ["-date"]
        verbose_name = "Key Achievement"
        verbose_name_plural = "Key Achievements"

    def __str__(self):
        return self.title
