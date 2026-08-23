from rest_framework import viewsets

from .models import Project, Service, Testimonial
from .serializers import ProjectSerializer, ServiceSerializer, TestimonialSerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.filter(featured=True)
    serializer_class = ServiceSerializer


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.filter(published=True)
    serializer_class = ProjectSerializer
    lookup_field = "slug"


class TestimonialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Testimonial.objects.filter(featured=True)
    serializer_class = TestimonialSerializer