from rest_framework import serializers

from .models import Project, Service, Testimonial


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "title", "slug", "short_description", "description", "icon", "image_url"]


class ProjectSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Project
        fields = [
            "id", "title", "slug", "category", "category_display", "location",
            "summary", "description", "client_name", "completion_date",
            "duration_months", "area_sqm", "image_url", "featured",
        ]


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ["id", "client_name", "client_role", "quote", "rating"]