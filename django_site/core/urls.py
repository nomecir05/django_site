from django.urls import path

from . import views


app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("projects/", views.projects, name="projects"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    path("request-a-quote/", views.quote_request, name="quote_request"),
    path("request-a-quote/success/<str:reference>/", views.quote_success, name="quote_success"),
    path("track/", views.track_quote, name="track_quote"),
    path("contact/", views.contact, name="contact"),
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
    path("privacy/", views.privacy, name="privacy"),
]
