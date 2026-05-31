from django.urls import path
from .views import profile_edit_view
app_name = 'personal'
urlpatterns = [
    path ("", profile_edit_view , name='profile')
]
