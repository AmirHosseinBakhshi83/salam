from django.urls import path
from .views import dashboard,exam_detail

app_name = 'dashboard'
urlpatterns = [
    path("",dashboard , name ='dashboard'),
    path("exam-detail/<int:pid>/", exam_detail , name ='exam-detail'),
]