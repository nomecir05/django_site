from django.contrib import admin, messages

from .models import (
    ContactMessage,
    NewsletterSubscriber,
    Project,
    QuoteRequest,
    QuoteStatusUpdate,
    Service,
    Testimonial,
)
from .workflows import transition_quote


admin.site.site_header = "BuildCore Operations"
admin.site.site_title = "BuildCore Admin"
admin.site.index_title = "Website and quotation workflow"


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "featured", "display_order")
    list_editable = ("featured", "display_order")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "description")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "location", "completion_date", "featured", "published")
    list_filter = ("category", "featured", "published")
    list_editable = ("featured", "published")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "location", "client_name")
    date_hierarchy = "completion_date"


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("client_name", "client_role", "rating", "featured")
    list_filter = ("rating", "featured")
    search_fields = ("client_name", "quote")


class QuoteStatusUpdateInline(admin.TabularInline):
    model = QuoteStatusUpdate
    extra = 0
    readonly_fields = ("created_at", "created_by")


@admin.action(description="Move selected requests to Under review")
def mark_reviewing(modeladmin, request, queryset):
    for quote in queryset:
        transition_quote(
            quote,
            QuoteRequest.Status.REVIEWING,
            "Our estimating team is reviewing the project requirements.",
            user=request.user,
        )
    messages.success(request, f"Updated {queryset.count()} quotation request(s).")


@admin.action(description="Mark selected requests as Proposal sent")
def mark_proposal_sent(modeladmin, request, queryset):
    for quote in queryset:
        transition_quote(
            quote,
            QuoteRequest.Status.PROPOSAL_SENT,
            "The detailed proposal has been prepared and sent for review.",
            user=request.user,
        )
    messages.success(request, f"Updated {queryset.count()} quotation request(s).")


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "full_name",
        "project_type",
        "location",
        "status",
        "assigned_to",
        "created_at",
    )
    list_filter = ("status", "project_type", "budget", "created_at")
    search_fields = ("reference", "full_name", "email", "phone", "location")
    readonly_fields = ("reference", "created_at", "updated_at")
    date_hierarchy = "created_at"
    list_select_related = ("assigned_to",)
    inlines = [QuoteStatusUpdateInline]
    actions = [mark_reviewing, mark_proposal_sent]
    fieldsets = (
        ("Customer", {"fields": ("reference", "full_name", "email", "phone", "company_name")}),
        ("Project", {"fields": ("project_type", "location", "budget", "timeline", "details", "preferred_contact")}),
        ("Workflow", {"fields": ("status", "assigned_to", "internal_notes", "created_at", "updated_at")}),
    )

    def save_model(self, request, obj, form, change):
        old_status = None
        if change:
            old_status = QuoteRequest.objects.only("status").get(pk=obj.pk).status
        super().save_model(request, obj, form, change)
        if old_status and old_status != obj.status:
            QuoteStatusUpdate.objects.create(
                quote=obj,
                status=obj.status,
                note=f"Status updated to {obj.get_status_display()}.",
                created_by=request.user,
                client_visible=True,
            )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    list_editable = ("is_read",)
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at",)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "active", "subscribed_at")
    list_filter = ("active", "subscribed_at")
    list_editable = ("active",)
    search_fields = ("email",)


@admin.register(QuoteStatusUpdate)
class QuoteStatusUpdateAdmin(admin.ModelAdmin):
    list_display = ("quote", "status", "client_visible", "created_by", "created_at")
    list_filter = ("status", "client_visible")
    search_fields = ("quote__reference", "note")
