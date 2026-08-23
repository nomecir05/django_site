from .forms import NewsletterForm


def site_context(request):
    return {
        "company": {
            "name": "BuildCore Construction",
            "short_name": "BuildCore",
            "phone": "+63 917 555 0142",
            "email": "hello@buildcore.example",
            "address": "Calamba City, Laguna, Philippines",
            "hours": "Mon–Sat, 8:00 AM–6:00 PM",
        },
        "newsletter_form": NewsletterForm(),
    }
