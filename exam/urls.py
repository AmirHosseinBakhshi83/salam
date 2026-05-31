from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import exam_view,public_scoreboard,pdf_view,answer_view

app_name = 'exam'
urlpatterns = [
    path("<int:exam_id>/",exam_view , name ='exam_view'),
    path('exam/<int:exam_id>/auto-save/', exam_view , name='auto_exam_view'),
    path('scoreboard/<int:exam_id>/', public_scoreboard, name='public_scoreboard'),
    path('viewpdf/<int:exam_id>/', pdf_view, name='pdf_view'),
    path('viewanswerpdf/<int:exam_id>/', answer_view, name='answer_view'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
