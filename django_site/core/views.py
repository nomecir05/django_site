from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import ContactForm, NewsletterForm, QuoteRequestForm, QuoteTrackingForm
from .models import NewsletterSubscriber, Project, QuoteRequest, Service, Testimonial
from .workflows import register_quote_request, send_contact_notification


def home(request):
    context = {
        "services": Service.objects.filter(featured=True)[:6],
        "projects": Project.objects.filter(published=True, featured=True)[:3],
        "testimonials": Testimonial.objects.filter(featured=True)[:3],
        "page_title": "Trusted construction, built to last",
    }
    return render(request, "core/home.html", context)


def about(request):
    return render(request, "core/about.html", {"page_title": "About BuildCore"})


def services(request):
    return render(
        request,
        "core/services.html",
        {"services": Service.objects.all(), "page_title": "Construction services"},
    )


def projects(request):
    selected_category = request.GET.get("category", "").strip()
    queryset = Project.objects.filter(published=True)
    valid_categories = {key for key, _ in Project.Category.choices}
    if selected_category in valid_categories:
        queryset = queryset.filter(category=selected_category)
    else:
        selected_category = ""
    context = {
        "projects": queryset,
        "categories": Project.Category.choices,
        "selected_category": selected_category,
        "page_title": "Selected projects",
    }
    return render(request, "core/projects.html", context)


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, published=True)
    related = Project.objects.filter(
        published=True, category=project.category
    ).exclude(pk=project.pk)[:3]
    return render(
        request,
        "core/project_detail.html",
        {"project": project, "related_projects": related, "page_title": project.title},
    )


def quote_request(request):
    if request.method == "POST":
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            quote = form.save()
            register_quote_request(quote)
            request.session["last_quote_reference"] = quote.reference
            return redirect("core:quote_success", reference=quote.reference)
    else:
        requested_service = request.GET.get("service", "")
        service_to_project_type = {
            "residential-construction": QuoteRequest.ProjectType.NEW_HOME,
            "commercial-construction": QuoteRequest.ProjectType.COMMERCIAL,
            "renovation-fit-out": QuoteRequest.ProjectType.RENOVATION,
            "repairs-maintenance": QuoteRequest.ProjectType.RENOVATION,
        }
        initial = {}
        if requested_service in service_to_project_type:
            initial["project_type"] = service_to_project_type[requested_service]
        form = QuoteRequestForm(initial=initial)
    return render(
        request,
        "core/quote_request.html",
        {"form": form, "page_title": "Request a free quotation"},
    )


def quote_success(request, reference):
    if request.session.get("last_quote_reference") != reference:
        return redirect("core:track_quote")
    quote = get_object_or_404(QuoteRequest, reference=reference)
    return render(
        request,
        "core/quote_success.html",
        {"quote": quote, "page_title": "Request received"},
    )


def track_quote(request):
    quote = None
    searched = False
    if request.method == "POST":
        form = QuoteTrackingForm(request.POST)
        searched = True
        if form.is_valid():
            quote = (
                QuoteRequest.objects.prefetch_related("updates")
                .filter(
                    reference__iexact=form.cleaned_data["reference"],
                    email__iexact=form.cleaned_data["email"],
                )
                .first()
            )
    else:
        form = QuoteTrackingForm()
    return render(
        request,
        "core/track_quote.html",
        {
            "form": form,
            "quote": quote,
            "searched": searched,
            "page_title": "Track your quotation",
        },
    )


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            transaction.on_commit(lambda: send_contact_notification(contact_message.pk))
            messages.success(
                request, "Thanks! Your message was sent. We'll reply within one business day."
            )
            return redirect("core:contact")
    else:
        form = ContactForm()
    return render(
        request,
        "core/contact.html",
        {"form": form, "page_title": "Contact our team"},
    )


def newsletter_subscribe(request):
    if request.method != "POST":
        return redirect("core:home")
    form = NewsletterForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data["email"].lower()
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email, defaults={"active": True}
        )
        if not created and not subscriber.active:
            subscriber.active = True
            subscriber.save(update_fields=["active"])
        messages.success(request, "You're subscribed to BuildCore project updates.")
    else:
        messages.error(request, "Please enter a valid email address.")

    next_url = request.POST.get("next", reverse("core:home"))
    if not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        next_url = reverse("core:home")
    return HttpResponseRedirect(next_url)


def privacy(request):
    return render(request, "core/privacy.html", {"page_title": "Privacy policy"})


def custom_404(request, exception):
    return render(request, "core/404.html", status=404)


def custom_500(request):
    return render(request, "core/500.html", status=500)
