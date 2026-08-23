from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]

handler404 = "core.views.custom_404"
handler500 = "core.views.custom_500"
