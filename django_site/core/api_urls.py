from rest_framework.routers import DefaultRouter

from .api import ProjectViewSet, ServiceViewSet, TestimonialViewSet


router = DefaultRouter()
router.register("services", ServiceViewSet, basename="api-service")
router.register("projects", ProjectViewSet, basename="api-project")
router.register("testimonials", TestimonialViewSet, basename="api-testimonial")

urlpatterns = router.urls