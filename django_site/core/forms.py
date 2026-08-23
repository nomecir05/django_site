import re

from django import forms

from .models import ContactMessage, NewsletterSubscriber, QuoteRequest


class StyledFormMixin:
    """Applies consistent front-end classes without repeating every widget."""

    def apply_styles(self):
        for field_name, field in self.fields.items():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"form-control {existing}".strip()
            field.widget.attrs.setdefault("id", f"id_{field_name}")
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 5)


class QuoteRequestForm(StyledFormMixin, forms.ModelForm):
    consent = forms.BooleanField(
        label="I agree that BuildCore may contact me about this project.",
        required=True,
    )

    class Meta:
        model = QuoteRequest
        fields = [
            "full_name",
            "email",
            "phone",
            "company_name",
            "project_type",
            "location",
            "budget",
            "timeline",
            "preferred_contact",
            "details",
        ]
        labels = {
            "full_name": "Full name",
            "company_name": "Company name (optional)",
            "project_type": "What are you planning?",
            "location": "Project location",
            "budget": "Estimated budget",
            "timeline": "Preferred start date",
            "preferred_contact": "Preferred contact method",
            "details": "Tell us about the project",
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Juan Dela Cruz"}),
            "email": forms.EmailInput(attrs={"placeholder": "juan@example.com"}),
            "phone": forms.TextInput(attrs={"placeholder": "+63 917 123 4567"}),
            "company_name": forms.TextInput(attrs={"placeholder": "Optional"}),
            "location": forms.TextInput(attrs={"placeholder": "City, Province"}),
            "details": forms.Textarea(
                attrs={
                    "placeholder": "Scope, approximate floor area, design preferences, and other requirements…",
                    "rows": 6,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = re.sub(r"\D", "", phone)
        if len(digits) < 10 or len(digits) > 15:
            raise forms.ValidationError("Enter a valid phone number with 10–15 digits.")
        return phone

    def clean_details(self):
        details = self.cleaned_data["details"].strip()
        if len(details) < 25:
            raise forms.ValidationError(
                "Please add a little more detail so our estimator can prepare properly."
            )
        return details


class QuoteTrackingForm(StyledFormMixin, forms.Form):
    reference = forms.CharField(
        max_length=20,
        label="Quotation reference",
        widget=forms.TextInput(attrs={"placeholder": "BC-202608-AB12"}),
    )
    email = forms.EmailField(
        label="Email used in the request",
        widget=forms.EmailInput(attrs={"placeholder": "juan@example.com"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()

    def clean_reference(self):
        return self.cleaned_data["reference"].strip().upper()


class ContactForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "phone": forms.TextInput(attrs={"placeholder": "+63 (optional)"}),
            "subject": forms.TextInput(attrs={"placeholder": "How can we help?"}),
            "message": forms.Textarea(attrs={"placeholder": "Write your message…"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "newsletter-input",
                    "placeholder": "Email address",
                    "aria-label": "Email address",
                }
            )
        }
