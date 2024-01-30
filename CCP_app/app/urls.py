from django.urls import include, path
from django.conf import settings
from main_page import views
from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = [
    path("", include("main_page.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
