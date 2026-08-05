from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from wagtail.images.models import Image

from .models import GalleryCategory, GalleryImage


class BulkUploadForm(forms.Form):
    category = forms.ModelChoiceField(queryset=GalleryCategory.objects.all(), required=True)


class BulkRecategorizeForm(forms.Form):
    category = forms.ModelChoiceField(queryset=GalleryCategory.objects.all(), required=True)


@login_required
def gallery_manager(request):
    """
    A single admin page for the two things one-at-a-time snippet forms
    are bad at: uploading many photos at once under one category, and
    re-tagging a batch of existing photos in one action.
    """
    can_manage = request.user.has_perm("newsroom.add_galleryimage") or request.user.has_perm(
        "newsroom.change_galleryimage"
    )
    if not can_manage:
        raise PermissionDenied

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "upload":
            upload_form = BulkUploadForm(request.POST)
            files = request.FILES.getlist("images")
            if upload_form.is_valid() and files:
                category = upload_form.cleaned_data["category"]
                created = 0
                for f in files:
                    image = Image.objects.create(title=f.name, file=f, file_size=f.size)
                    GalleryImage.objects.create(image=image, category=category)
                    created += 1
                messages.success(request, f"Uploaded {created} image(s) to “{category.name}”.")
            else:
                messages.error(request, "Choose a category and at least one image file.")
            return redirect("newsroom_gallery_manager")

        elif action == "recategorize":
            recategorize_form = BulkRecategorizeForm(request.POST)
            ids = request.POST.getlist("selected")
            if recategorize_form.is_valid() and ids:
                category = recategorize_form.cleaned_data["category"]
                count = GalleryImage.objects.filter(pk__in=ids).update(category=category)
                messages.success(request, f"Re-categorized {count} image(s) to “{category.name}”.")
            else:
                messages.error(request, "Select at least one image and a category.")
            return redirect("newsroom_gallery_manager")

    context = {
        "upload_form": BulkUploadForm(),
        "recategorize_form": BulkRecategorizeForm(),
        "gallery_images": GalleryImage.objects.select_related("category", "image").order_by("-uploaded_at"),
        "categories": GalleryCategory.objects.all(),
    }
    return render(request, "newsroom/gallery_manager.html", context)
