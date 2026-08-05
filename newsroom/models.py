from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class NewsItem(models.Model):
    """
    A single news entry — either third-party Media Coverage or a DHPL
    Press Release — shown in the homepage "News & Media" section.
    Admins manage these from Snippets: add a title, pick a category,
    optionally attach an image, write a short excerpt, set the date,
    and (once known) paste the article link.
    """

    CATEGORY_CHOICES = [
        ("media_coverage", "Media Coverage"),
        ("press_release", "Press Release"),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    excerpt = models.TextField(blank=True)
    published_date = models.DateField()
    link = models.URLField(blank=True, help_text="Link to the full article (external site or PDF).")

    panels = [
        FieldPanel("title"),
        FieldPanel("category"),
        FieldPanel("image"),
        FieldPanel("excerpt"),
        FieldPanel("published_date"),
        FieldPanel("link"),
    ]

    class Meta:
        ordering = ["-published_date"]
        verbose_name = "News Item"
        verbose_name_plural = "News Items"

    def __str__(self):
        return self.title


@register_snippet
class GalleryCategory(models.Model):
    """
    An admin-defined gallery category (e.g. "Project", "Social",
    "Environmental", "Safety"). Admins add whatever categories they
    need — this isn't a fixed list — and the Media page builds its
    filter tabs from whatever exists here.
    """

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, help_text="Used in the URL/filter — letters, numbers, hyphens only.")
    order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("order"),
    ]

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Gallery Category"
        verbose_name_plural = "Gallery Categories"

    def __str__(self):
        return self.name


@register_snippet
class GalleryImage(models.Model):
    """
    A single photo in the Media page gallery, tagged to one category.
    For adding many at once, use Snippets > Gallery Images > Bulk
    Upload Images instead of adding these one at a time.
    """

    title = models.CharField(max_length=255, blank=True, help_text="Optional caption.")
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        related_name="+",
    )
    category = models.ForeignKey(
        GalleryCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="images",
    )
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("image"),
        FieldPanel("category"),
        FieldPanel("order"),
    ]

    class Meta:
        ordering = ["-uploaded_at", "order"]
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"

    def __str__(self):
        return self.title or f"Gallery image #{self.pk}"
