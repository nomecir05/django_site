from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from .models import ContactMessage, QuoteRequest, QuoteStatusUpdate


@transaction.atomic
def register_quote_request(quote: QuoteRequest):
    """Create the first timeline event and queue both notification emails."""
    QuoteStatusUpdate.objects.create(
        quote=quote,
        status=quote.status,
        note="Your request was received. Our estimating team will review the details.",
        client_visible=True,
    )
    transaction.on_commit(lambda: send_quote_notifications(quote.pk))
    return quote


def send_quote_notifications(quote_id: int):
    quote = QuoteRequest.objects.get(pk=quote_id)
    send_mail(
        subject=f"We received your request — {quote.reference}",
        message=(
            f"Hi {quote.full_name},\n\n"
            "Thank you for considering BuildCore Construction. "
            f"Your quotation reference is {quote.reference}.\n\n"
            "Our team will review your requirements and contact you within one business day. "
            "You may track the status on our website using your reference and email.\n\n"
            "BuildCore Construction"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[quote.email],
        fail_silently=True,
    )
    send_mail(
        subject=f"New quotation request: {quote.reference}",
        message=(
            f"Name: {quote.full_name}\n"
            f"Email: {quote.email}\n"
            f"Phone: {quote.phone}\n"
            f"Project: {quote.get_project_type_display()}\n"
            f"Location: {quote.location}\n"
            f"Budget: {quote.get_budget_display()}\n\n"
            f"Details:\n{quote.details}"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.COMPANY_EMAIL],
        fail_silently=True,
    )


def send_contact_notification(message_id: int):
    message = ContactMessage.objects.get(pk=message_id)
    send_mail(
        subject=f"Website message: {message.subject}",
        message=(
            f"Name: {message.name}\n"
            f"Email: {message.email}\n"
            f"Phone: {message.phone or 'Not provided'}\n\n"
            f"{message.message}"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.COMPANY_EMAIL],
        fail_silently=True,
    )


@transaction.atomic
def transition_quote(
    quote: QuoteRequest,
    new_status: str,
    note: str = "",
    user=None,
    client_visible: bool = True,
):
    """Change status and keep an auditable timeline entry."""
    valid_statuses = {choice for choice, _ in QuoteRequest.Status.choices}
    if new_status not in valid_statuses:
        raise ValueError(f"Unknown quote status: {new_status}")
    if quote.status == new_status and not note:
        return quote

    quote.status = new_status
    quote.save(update_fields=["status", "updated_at"])
    QuoteStatusUpdate.objects.create(
        quote=quote,
        status=new_status,
        note=note,
        created_by=user if getattr(user, "is_authenticated", False) else None,
        client_visible=client_visible,
    )
    return quote
