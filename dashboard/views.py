from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from exam.models import UserExam, Exam
from django.utils import timezone


# Create your views here.
@login_required
def dashboard(request):
    user_exams = request.user.profile.assigned_exams.all()
    context = {'user_exams':user_exams}
    return render(request,'dashboard/dashboard-exams.html', context)

@login_required
def exam_detail(request, pid):
    user_exam = UserExam.objects.get(id = pid)
    is_complete = user_exam.is_completed
    exam = Exam.objects.get(id = user_exam.exam_id)
    now = timezone.now()
    if exam.start_date <= now <= exam.end_date:
        is_active = True
    else:
        is_active = False

    context = {
        'user_exam_id' : user_exam.id , 
        'exam_id':exam.id ,
        'is_active':is_active,
        'is_complete':is_complete,
        'title':exam.title,
        'type':exam.exam_type,
        'question_count':exam.question_count,
        'start_date':exam.start_date,
        'end_date':exam.end_date,
        'duration_lenght':exam.duration_lenght,
        'status':exam.status,

    }
    print(context)
    return render(request,'dashboard/dashboard-exam-detali.html', context)


