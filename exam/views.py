import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Exam, UserExam, UserAnswer
from .forms import ExamAnswerForm
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages



def custom_404_view(request, exception):
    """Custom 404 error handler"""
    # You can add any custom logic here
    # For example: log the error, suggest similar pages, etc.
    context = {
        'requested_path': request.path,
        'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
    }
    return render(request, '404.html', context, status=404)

@login_required(login_url='/accounts/login/')
def exam_view(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    pdf_url = exam.pdf_file.url
    has_user_exam = UserExam.objects.filter(
            exam=exam,
            profile=request.user.profile
        ).exists()
    if not has_user_exam:
            messages.error(request, 'شما دسترسی به این صفحه را ندارید. این آزمون به شما اختصاص داده نشده است.')
            return redirect('/dashboard')
    
    # تشخیص نوع درخواست
    is_auto_save = request.POST.get('auto_save') == 'true'
    is_final_submit = request.POST.get('final_submit') == 'true'
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Get or create UserExam with proper error handling
    try:
        user_exam = UserExam.objects.get(
            exam=exam,
            profile=request.user.profile,
            is_completed=False,
        )

        if not user_exam.started_date:
            user_exam.started_date = timezone.now()
            user_exam.save()

    except UserExam.DoesNotExist:
        # If no existing exam, create one (optional: check if user is allowed to take it)
        user_exam = UserExam.objects.create(
            exam=exam,
            profile=request.user.profile,
        )
    
    # Check if exam is expired before processing
    if user_exam.is_expired():
        user_exam.is_completed = True
        user_exam.save()
        if is_ajax:
            return JsonResponse({'error': 'Time expired!', 'redirect': 'expired'}, status=400)
        return render(request, "exam/exam-expired.html", {"exam": exam})
    
    questions = exam.questions.all().order_by("id")
    remaining_seconds = user_exam.get_remaining_seconds()

    # پردازش درخواست POST
    if request.method == "POST":
        # Double-check time hasn't expired before processing submission
        if user_exam.is_expired():
            user_exam.is_completed = True
            user_exam.save()
            if is_ajax:
                return JsonResponse({'error': 'Time expired! Cannot submit.'}, status=400)
            return render(request, "exam/exam-expired.html", {"exam": exam})
        
        # برای ذخیره خودکار یا ثبت نهایی
        if is_auto_save or (is_ajax and not is_final_submit):
            # ذخیره موقت پاسخ‌ها در session (بدون اعتبارسنجی کامل)
            temp_answers = {}
            for key, value in request.POST.items():
                if key.startswith('q'):
                    temp_answers[key] = value
            
            # ذخیره در session با timestamp
            session_key = f'exam_{exam_id}_temp_answers'
            request.session[session_key] = {
                'answers': temp_answers,
                'timestamp': timezone.now().isoformat(),
                'question_count': len(questions)
            }
            request.session.modified = True
            
            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'message': 'پاسخ‌ها موقتاً ذخیره شد',
                    'saved_at': timezone.now().strftime('%H:%M:%S'),
                    'answers_count': len(temp_answers)
                })
            # اگر درخواست معمولی بود، به همان صفحه برگردان
            return redirect('exam:exam_view', exam_id=exam_id)
        
        # ثبت نهایی
        elif is_final_submit or not is_ajax:
            form = ExamAnswerForm(request.POST, questions=questions)
            print("Form is valid:", form.is_valid())
            
            if form.is_valid():
                def get_default_for_question_type(question_type):
                    """مقدار پیش‌فرض برای هر نوع سوال"""
                    defaults = {
                        "true_false_set": "X",  # مقدار پیش‌فرض برای هر سلول
                    }
                    return defaults.get(question_type, "")

                with transaction.atomic():
                    for question in questions:
                        if question.question_type == "true_false_set":
                            cols = []
                            for col in range(1, 6):
                                value = form.cleaned_data.get(f"q{question.id}_col{col}")
                                if not value:
                                    value = get_default_for_question_type(question.question_type)
                                cols.append(value)
                            answer_value = ",".join(cols)  # e.g. "true,false,true,true,false"
                        else:
                            answer_value = str(form.cleaned_data[f"q{question.id}"])

                        UserAnswer.objects.update_or_create(
                            user_exam=user_exam,
                            question=question,
                            defaults={"answer_value": answer_value},
                        )

                    user_exam.is_completed = True
                    print(UserAnswer.objects.all())
                    user_exam.save()
                    
                    # Calculate initial score
                    user_exam.recalculate_score()
                    
                    # پاک کردن session ذخیره موقت
                    session_key = f'exam_{exam_id}_temp_answers'
                    if session_key in request.session:
                        del request.session[session_key]

                    if is_ajax:
                        return JsonResponse({
                            'status': 'success',
                            'message': 'آزمون با موفقیت ثبت شد',
                            'redirect_url': reverse('dashboard:dashboard')
                        })
                    
                    return redirect('dashboard:dashboard')
            else:
                # Form invalid
                print("Form errors:", form.errors)
                if is_ajax:
                    return JsonResponse({
                        'error': 'Form validation failed',
                        'errors': form.errors
                    }, status=400)
                # اگر فرم نامعتبر بود و درخواست معمولی، دوباره فرم رو نمایش بده
                return render(
                    request,
                    "exam/exam-view.html",
                    {
                        "exam": exam,
                        "form": form,
                        "questions": questions,
                        "pdf_url": pdf_url,
                        "user_exam": user_exam,
                        "remaining_seconds": remaining_seconds,
                    },
                )
    
    # درخواست GET - بازیابی پاسخ‌های موقت از session اگر وجود داشته باشد
    else:
        form = ExamAnswerForm(questions=questions)
        
        # بازیابی پاسخ‌های موقت از session (اگر کاربر قبلاً ذخیره کرده باشد)
        session_key = f'exam_{exam_id}_temp_answers'
        if session_key in request.session:
            temp_data = request.session[session_key]
            temp_answers = temp_data.get('answers', {})
            
            # پر کردن فرم با پاسخ‌های موقت
            for key, value in temp_answers.items():
                if key in form.fields:
                    form.fields[key].initial = value
            
            # نمایش پیام به کاربر
            saved_time = temp_data.get('timestamp', '')
            if saved_time:
                messages.info(request, f'پاسخ‌های ذخیره شده موقت از تاریخ {saved_time} بازیابی شد.')

    return render(
        request,
        "exam/exam-view.html",
        {
            "exam": exam,
            "form": form,
            "questions": questions,
            "pdf_url": pdf_url,
            "user_exam": user_exam,  # Pass user_exam to template
            "remaining_seconds": remaining_seconds,  # Pass initial remaining time
        },
    )


# API endpoint to get remaining time
@login_required(login_url='/accounts/login/')
@require_http_methods(["GET"])
def get_remaining_time(request, user_exam_id):
    """API endpoint to get remaining time for an exam"""
    try:
        user_exam = UserExam.objects.get(id=user_exam_id, profile__user=request.user)
        
        if user_exam.is_completed:
            return JsonResponse({'remaining': 0, 'completed': True})
        
        remaining_seconds = user_exam.get_remaining_seconds()
        
        if remaining_seconds <= 0:
            # Auto-mark as completed if time expired
            user_exam.is_completed = True
            user_exam.save()
            return JsonResponse({'remaining': 0, 'completed': True, 'expired': True})
        
        return JsonResponse({
            'remaining': remaining_seconds,
            'completed': False,
            'started_date': user_exam.started_date.isoformat()
        })
    
    except UserExam.DoesNotExist:
        return JsonResponse({'error': 'Exam not found'}, status=404)


# API endpoint to submit exam via AJAX
@login_required(login_url='/accounts/login/')
@require_http_methods(["POST"])
@csrf_exempt
def submit_exam_ajax(request, user_exam_id):
    """AJAX endpoint to submit exam with time validation"""
    try:
        user_exam = UserExam.objects.get(id=user_exam_id, profile__user=request.user)
        
        # Check if already completed
        if user_exam.is_completed:
            return JsonResponse({'error': 'Exam already submitted'}, status=400)
        
        # Check if time expired
        if user_exam.is_expired():
            user_exam.is_completed = True
            user_exam.save()
            return JsonResponse({'error': 'Time expired! Exam auto-submitted.'}, status=400)
        
        # Get exam and questions
        exam = user_exam.exam
        questions = exam.questions.all().order_by("id")
        
        # Process the answers from POST data
        form = ExamAnswerForm(request.POST, questions=questions)
        
        if form.is_valid():
            with transaction.atomic():
                for question in questions:
                    if question.question_type == "true_false_set":
                        cols = [
                            form.cleaned_data[f"q{question.id}_col{col}"]
                            for col in range(1, 6)
                        ]
                        answer_value = ",".join(cols)
                    else:
                        answer_value = str(form.cleaned_data[f"q{question.id}"])

                    UserAnswer.objects.update_or_create(
                        user_exam=user_exam,
                        question=question,
                        defaults={"answer_value": answer_value},
                    )

                user_exam.is_completed = True
                user_exam.save()
                
                return JsonResponse({'success': True, 'message': 'Exam submitted successfully!'})
        else:
            return JsonResponse({'error': 'Form validation failed', 'errors': form.errors}, status=400)
            
    except UserExam.DoesNotExist:
        return JsonResponse({'error': 'Exam not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    


@login_required(login_url='/accounts/login/')
def public_scoreboard(request, exam_id):
    """Public view to display scoreboard with limitations"""
    exam = get_object_or_404(Exam, id=exam_id)
    has_user_exam = UserExam.objects.filter(
            exam=exam,
            profile=request.user.profile
        ).exists()
    if not has_user_exam:
            messages.error(request, 'شما دسترسی به این صفحه را ندارید.')
            return redirect('/dashboard')
    
    # Get all completed exams
    user_exams = UserExam.objects.filter(
        exam=exam,
        is_completed=True,
        score__isnull=False
    ).select_related('profile__user').order_by('-percentage_score', '-score', 'completed_at')
    
    # Calculate ranks
    scoreboard_data = []
    current_rank = 1
    previous_score = None
    
    for idx, ue in enumerate(user_exams, 1):
        if previous_score != ue.percentage_score:
            current_rank = idx
        
        # Calculate duration
        duration = ""
        if ue.started_date and ue.completed_at:
            delta = ue.completed_at - ue.started_date
            duration = f"{delta.total_seconds() / 60:.0f}"
        
        scoreboard_data.append({
            'rank': current_rank,
            'username': ue.profile.user.username,
            'name': ue.profile.user_name or '',
            'score': float(ue.score),
            'percentage': float(ue.percentage_score),
            'completed_at': ue.completed_at,
            'duration': duration,
        })
        
        previous_score = ue.percentage_score
    
    # Apply limitations based on request parameters
    limit = request.GET.get('limit', 50)  # Default limit 50
    show_top = request.GET.get('top', None)  # Show only top N
    search = request.GET.get('search', None)  # Search by username
    
    # Apply search filter
    if search:
        scoreboard_data = [item for item in scoreboard_data if 
                          search.lower() in item['username'].lower() or 
                          search.lower() in item['name'].lower()]
    
    # Apply top N limitation
    if show_top and show_top.isdigit():
        scoreboard_data = scoreboard_data[:int(show_top)]
    
    # Apply pagination
    paginator = Paginator(scoreboard_data, int(limit))
    page = request.GET.get('page', 1)
    
    try:
        scoreboard_page = paginator.page(page)
    except PageNotAnInteger:
        scoreboard_page = paginator.page(1)
    except EmptyPage:
        scoreboard_page = paginator.page(paginator.num_pages)
    
    # Calculate statistics
    total_participants = len(scoreboard_data)
    stats = {}
    if total_participants > 0:
        avg_score = sum(item['percentage'] for item in scoreboard_data) / total_participants
        stats = {
            'total': total_participants,
            'average': round(avg_score, 2),
            'highest': scoreboard_data[0]['percentage'] if scoreboard_data else 0,
            'lowest': scoreboard_data[-1]['percentage'] if scoreboard_data else 0,
        }
    
    # Get current user's rank if authenticated
    user_rank = None
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        for item in scoreboard_data:
            if item['username'] == request.user.username:
                user_rank = item['rank']
                break
    
    context = {
        'exam': exam,
        'scoreboard': scoreboard_page,
        'stats': stats,
        'user_rank': user_rank,
        'limit': limit,
        'show_top': show_top,
        'search': search,
    }
    
    return render(request, 'exam/public_scoreboard.html', context)




@login_required(login_url='/accounts/login/')
def pdf_view(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    has_user_exam = UserExam.objects.filter(
            exam=exam,
            profile=request.user.profile
        ).exists()
    if not has_user_exam:
            messages.error(request, 'شما دسترسی به این صفحه را ندارید.')
            return redirect('/dashboard')
    
    pdf_url = exam.pdf_file.url

    context = {
        'pdf_url': pdf_url,
    }

    return render(request, 'exam/pdf-view.html', context)

@login_required(login_url='/accounts/login/')
def answer_view(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    has_user_exam = UserExam.objects.filter(
            exam=exam,
            profile=request.user.profile
        ).exists()
    if not has_user_exam:
            messages.error(request, 'شما دسترسی به این صفحه را ندارید.')
            return redirect('/dashboard')
    
    pdf_url = exam.answer_pdf_file.url

    context = {
        'pdf_url': pdf_url,
    }

    return render(request, 'exam/answer-pdf-view.html', context)

