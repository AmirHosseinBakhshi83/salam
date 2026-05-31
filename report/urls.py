from django.urls import path
from .views import single_report,total_report,generate_answer_sheet_pdf

app_name = 'report'
urlpatterns = [
    path("single/<int:pid>",single_report , name ='single'),
    path("total/",total_report , name ='total'),
    path("answersheet/<int:exam_id>/<int:user_exam_id>",generate_answer_sheet_pdf , name ='answer_sheet'),
]