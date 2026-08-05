from django import forms
from django.core.exceptions import ValidationError

from .models import Grievance, GrievanceCategory

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50MB


class GrievanceForm(forms.ModelForm):
    declaration_accepted = forms.BooleanField(
        required=True,
        error_messages={"required": "Please confirm the declaration before submitting."},
        widget=forms.CheckboxInput(attrs={"class": "dhpl-checkbox-input"}),
    )

    class Meta:
        model = Grievance
        fields = [
            "is_anonymous",
            "full_name",
            "cid_number",
            "email",
            "phone",
            "village_gewog",
            "category",
            "description",
            "audio_file",
            "video_file",
            "declaration_accepted",
        ]
        widgets = {
            "is_anonymous": forms.CheckboxInput(attrs={"class": "dhpl-switch-input"}),
            "full_name": forms.TextInput(attrs={"class": "dhpl-input", "placeholder": "Enter your full name"}),
            "cid_number": forms.TextInput(attrs={"class": "dhpl-input", "placeholder": "Enter your CID number"}),
            "email": forms.EmailInput(attrs={"class": "dhpl-input", "placeholder": "Enter your email address"}),
            "phone": forms.TextInput(attrs={"class": "dhpl-input", "placeholder": "Enter your phone number"}),
            "village_gewog": forms.TextInput(
                attrs={"class": "dhpl-input", "placeholder": "Enter your village or gewog"}
            ),
            "category": forms.Select(attrs={"class": "dhpl-select"}),
            "description": forms.Textarea(
                attrs={"class": "dhpl-textarea", "rows": 6, "placeholder": "Describe your grievance in detail..."}
            ),
            "audio_file": forms.ClearableFileInput(attrs={"class": "dhpl-file-input", "accept": "audio/*"}),
            "video_file": forms.ClearableFileInput(attrs={"class": "dhpl-file-input", "accept": "video/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = GrievanceCategory.objects.all()
        self.fields["category"].empty_label = "Select category"
        self.fields["category"].required = True

    def clean(self):
        cleaned = super().clean()
        is_anonymous = cleaned.get("is_anonymous")

        if not is_anonymous:
            for field in ("full_name", "cid_number", "phone"):
                if not cleaned.get(field):
                    self.add_error(field, "This field is required unless you submit anonymously.")

        if not cleaned.get("description") and not cleaned.get("audio_file") and not cleaned.get("video_file"):
            raise ValidationError(
                "Please describe your grievance in writing, or attach a voice recording or video."
            )

        return cleaned

    def _clean_upload(self, field_name):
        f = self.cleaned_data.get(field_name)
        if f and f.size > MAX_UPLOAD_BYTES:
            raise ValidationError("This file is too large — the limit is 50MB.")
        return f

    def clean_audio_file(self):
        return self._clean_upload("audio_file")

    def clean_video_file(self):
        return self._clean_upload("video_file")
