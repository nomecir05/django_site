from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import (
    ContactMessage,
    NewsletterSubscriber,
    Project,
    QuoteRequest,
    QuoteStatusUpdate,
    Service,
)
from .workflows import transition_quote


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PublicWebsiteTests(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            title="Residential Construction",
            slug="residential-construction",
            short_description="Well-built homes.",
            description="Complete residential construction service.",
            featured=True,
            display_order=1,
        )
        self.project = Project.objects.create(
            title="Test Residence",
            slug="test-residence",
            category=Project.Category.RESIDENTIAL,
            location="Calamba, Laguna",
            summary="A test residential project.",
            description="Built for automated website testing.",
            image_url="https://example.com/project.jpg",
            featured=True,
            published=True,
        )

    def quote_payload(self, **overrides):
        payload = {
            "full_name": "Juan Dela Cruz",
            "email": "juan@example.com",
            "phone": "+63 917 123 4567",
            "company_name": "",
            "project_type": QuoteRequest.ProjectType.NEW_HOME,
            "location": "Calamba City, Laguna",
            "budget": QuoteRequest.Budget.THREE_TO_FIVE,
            "timeline": QuoteRequest.Timeline.THREE_TO_SIX,
            "preferred_contact": "email",
            "details": "We plan to build a two-storey, three-bedroom family home.",
            "consent": "on",
        }
        payload.update(overrides)
        return payload

    def test_home_and_project_pages_render(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Residential Construction")
        detail = self.client.get(self.project.get_absolute_url())
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "Test Residence")

    def test_quote_submission_starts_workflow_and_sends_emails(self):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("core:quote_request"), self.quote_payload()
            )
        quote = QuoteRequest.objects.get(email="juan@example.com")
        self.assertRedirects(
            response, reverse("core:quote_success", args=[quote.reference])
        )
        self.assertTrue(quote.reference.startswith("BC-"))
        self.assertEqual(quote.updates.count(), 1)
        self.assertEqual(len(mail.outbox), 2)

    def test_quote_rejects_too_short_project_description(self):
        response = self.client.post(
            reverse("core:quote_request"), self.quote_payload(details="Small house")
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please add a little more detail")
        self.assertFalse(QuoteRequest.objects.exists())

    def test_tracking_requires_reference_and_matching_email(self):
        quote = QuoteRequest.objects.create(
            full_name="Maria Santos",
            email="maria@example.com",
            phone="09171234567",
            project_type=QuoteRequest.ProjectType.RENOVATION,
            location="Santa Rosa, Laguna",
            budget=QuoteRequest.Budget.ONE_TO_THREE,
            timeline=QuoteRequest.Timeline.FLEXIBLE,
            details="A complete renovation of an existing family residence.",
        )
        QuoteStatusUpdate.objects.create(
            quote=quote, status=quote.status, note="Request received."
        )
        good = self.client.post(
            reverse("core:track_quote"),
            {"reference": quote.reference.lower(), "email": "MARIA@example.com"},
        )
        self.assertContains(good, quote.reference)
        self.assertContains(good, "Request received.")
        bad = self.client.post(
            reverse("core:track_quote"),
            {"reference": quote.reference, "email": "wrong@example.com"},
        )
        self.assertContains(bad, "could not find that request")

    def test_status_transition_creates_timeline_event(self):
        quote = QuoteRequest.objects.create(
            full_name="Pedro Reyes",
            email="pedro@example.com",
            phone="09170000000",
            project_type=QuoteRequest.ProjectType.COMMERCIAL,
            location="Makati City",
            budget=QuoteRequest.Budget.ABOVE_TEN,
            timeline=QuoteRequest.Timeline.ONE_TO_THREE,
            details="Commercial office construction with coordinated MEP scope.",
        )
        transition_quote(
            quote,
            QuoteRequest.Status.REVIEWING,
            "Estimator assigned and drawings under review.",
        )
        quote.refresh_from_db()
        self.assertEqual(quote.status, QuoteRequest.Status.REVIEWING)
        self.assertEqual(quote.updates.count(), 1)

    def test_newsletter_subscription_is_idempotent(self):
        url = reverse("core:newsletter_subscribe")
        self.client.post(url, {"email": "updates@example.com", "next": "/"})
        self.client.post(url, {"email": "updates@example.com", "next": "/"})
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)

    def test_contact_form_saves_message(self):
        response = self.client.post(
            reverse("core:contact"),
            {
                "name": "Ana Cruz",
                "email": "ana@example.com",
                "phone": "09181234567",
                "subject": "Site visit",
                "message": "Can your team arrange a site visit next week?",
            },
        )
        self.assertRedirects(response, reverse("core:contact"))
        self.assertEqual(ContactMessage.objects.count(), 1)
