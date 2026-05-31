from django.urls import path, include
from django.conf import settings
from accounts import views
from .views import website

app_name = 'website'
urlpatterns = [
    path('', website, name = 'website'),
]
