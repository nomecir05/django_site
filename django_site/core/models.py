import secrets

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Service(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=220)
    description = models.TextField()
    icon = models.CharField(
        max_length=12,
        default="01",
        help_text="Short number or symbol displayed on the service card.",
    )
    image_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "title"]

    def __str__(self):
        return self.title


class Project(models.Model):
    class Category(models.TextChoices):
        RESIDENTIAL = "residential", "Residential"
        COMMERCIAL = "commercial", "Commercial"
        RENOVATION = "renovation", "Renovation"
        INDUSTRIAL = "industrial", "Industrial"

    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=24, choices=Category.choices)
    location = models.CharField(max_length=160)
    summary = models.CharField(max_length=260)
    description = models.TextField()
    client_name = models.CharField(max_length=120, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    duration_months = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1)]
    )
    area_sqm = models.PositiveIntegerField(null=True, blank=True)
    image_url = models.URLField()
    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completion_date", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:project_detail", kwargs={"slug": self.slug})


class Testimonial(models.Model):
    client_name = models.CharField(max_length=120)
    client_role = models.CharField(max_length=160, blank=True)
    quote = models.TextField(max_length=600)
    rating = models.PositiveSmallIntegerField(default=5)
    featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.client_name} — {self.rating}/5"


class QuoteRequest(models.Model):
    class ProjectType(models.TextChoices):
        NEW_HOME = "new_home", "New home construction"
        COMMERCIAL = "commercial", "Commercial construction"
        RENOVATION = "renovation", "Renovation / fit-out"
        EXTENSION = "extension", "House extension"
        INDUSTRIAL = "industrial", "Industrial project"
        OTHER = "other", "Other"

    class Budget(models.TextChoices):
        UNDER_1M = "under_1m", "Below ₱1 million"
        ONE_TO_THREE = "1m_3m", "₱1–3 million"
        THREE_TO_FIVE = "3m_5m", "₱3–5 million"
        FIVE_TO_TEN = "5m_10m", "₱5–10 million"
        ABOVE_TEN = "above_10m", "Above ₱10 million"
        DISCUSS = "discuss", "To be discussed"

    class Timeline(models.TextChoices):
        ASAP = "asap", "As soon as possible"
        ONE_TO_THREE = "1_3_months", "Within 1–3 months"
        THREE_TO_SIX = "3_6_months", "Within 3–6 months"
        SIX_PLUS = "6_plus_months", "After 6 months"
        FLEXIBLE = "flexible", "Flexible"

    class Status(models.TextChoices):
        NEW = "new", "New request"
        REVIEWING = "reviewing", "Under review"
        CONSULTATION = "consultation", "Consultation scheduled"
        PROPOSAL_SENT = "proposal_sent", "Proposal sent"
        APPROVED = "approved", "Approved"
        IN_PROGRESS = "in_progress", "Project in progress"
        COMPLETED = "completed", "Completed"
        CLOSED = "closed", "Closed"

    reference = models.CharField(max_length=20, unique=True, editable=False)
    full_name = models.CharField(max_length=140)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    company_name = models.CharField(max_length=160, blank=True)
    project_type = models.CharField(max_length=30, choices=ProjectType.choices)
    location = models.CharField(max_length=220)
    budget = models.CharField(max_length=30, choices=Budget.choices)
    timeline = models.CharField(max_length=30, choices=Timeline.choices)
    details = models.TextField()
    preferred_contact = models.CharField(
        max_length=16,
        choices=[("email", "Email"), ("phone", "Phone call"), ("sms", "SMS")],
        default="email",
    )
    status = models.CharField(
        max_length=24, choices=Status.choices, default=Status.NEW
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_quotes",
    )
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} — {self.full_name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            prefix = timezone.localdate().strftime("BC-%Y%m")
            for _ in range(12):
                candidate = f"{prefix}-{secrets.token_hex(2).upper()}"
                if not QuoteRequest.objects.filter(reference=candidate).exists():
                    self.reference = candidate
                    break
            else:
                self.reference = f"{prefix}-{secrets.token_hex(4).upper()}"
        super().save(*args, **kwargs)

    @property
    def status_progress(self):
        progress = {
            self.Status.NEW: 12,
            self.Status.REVIEWING: 26,
            self.Status.CONSULTATION: 42,
            self.Status.PROPOSAL_SENT: 58,
            self.Status.APPROVED: 72,
            self.Status.IN_PROGRESS: 86,
            self.Status.COMPLETED: 100,
            self.Status.CLOSED: 100,
        }
        return progress.get(self.status, 0)


class QuoteStatusUpdate(models.Model):
    quote = models.ForeignKey(
        QuoteRequest, on_delete=models.CASCADE, related_name="updates"
    )
    status = models.CharField(max_length=24, choices=QuoteRequest.Status.choices)
    note = models.CharField(max_length=400, blank=True)
    client_visible = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="quote_updates",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.quote.reference}: {self.get_status_display()}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=140)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=180)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} — {self.name}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email
