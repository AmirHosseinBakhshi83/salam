from django.shortcuts import render,get_object_or_404
from django.contrib.auth.decorators import login_required
from exam.models import UserExam, UserAnswer
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
import os
from django.conf import settings




@login_required
# views.py
def single_report(request, pid):
    user_exam = get_object_or_404(UserExam, id=pid)
    user_answers = UserAnswer.objects.filter(
        user_exam=user_exam
    ).select_related('question').order_by('question_id')
    
    site_answer = {}
    for idx, answer in enumerate(user_answers, start=1):
        # تبدیل پاسخ کاربر به آرایه
        reza ={}
        combined_answers = []
        if answer.question.question_type == 'true_false_set':
            user_answers_list = answer.answer_value.split(',') if answer.answer_value else []
            user_answers_list = [a.strip() for a in user_answers_list if a.strip()]
            question_answer_list = answer.question.correct_answer
            correct_answer_list = [a.strip() for a in question_answer_list if a.strip()]
            is_correct=[]
            is_answered=[]
            letters = {1: 'الف', 2: 'ب', 3: 'ج', 4: 'د', 5: 'ه'}
            letter=[]
            for i in range(0,5):
                letter.append(letters.get(i+1, str(i)))
                if user_answers_list[i] == 'X':
                    is_answered.append(False)
                else:
                    is_answered.append(True)

                if user_answers_list[i] == correct_answer_list[i] or (correct_answer_list[i]==0 and is_answered[i]== True) :
                    is_correct.append(True) 
                    
                elif user_answers_list[i] != correct_answer_list[i] and correct_answer_list[i] != 'B':
                    is_correct.append(False)

            for i in range(5):  # since both have 5 elements
                combined_answers.append({
                'letter': letters.get(i+1, str(i+1)),
                'q_answer': correct_answer_list[i],
                'user_answer': user_answers_list[i],
                'is_correct' : is_correct[i],
                'is_answered': is_answered[i],
            })
            print(idx , combined_answers)  


        else:
            if answer.answer_value == answer.question.correct_answer:
                reza_is_correct=True
            else:
                reza_is_correct=False

            if answer.answer_value == 'None':
                reza_is_answered = False
            else:
                reza_is_answered = True

            reza = {
                'q_answer': answer.question.correct_answer,
                'user_answer': answer.answer_value,
                'is_correct': reza_is_correct,
                'is_answered':reza_is_answered,
            }
            print(idx , reza) 
        
    
        site_answer[idx] = {
            'question_type': answer.question.question_type,
            'combined_answers':combined_answers,
            'reza':reza,
        }
    
    context = {
        'user_exam': user_exam,
        'site_answer': site_answer,
    }
    
    return render(request, 'report/single-report.html', context)

@login_required
def total_report (request):
    user = request.user
    user_exams = UserExam.objects.filter(profile=user.profile)
    context = {'user_exams':user_exams}
    return render (request,'report/total-report.html' , context)


@login_required
def generate_answer_sheet_pdf(request, exam_id, user_exam_id):
    """
    تولید PDF پاسخ‌نامه کاربر
    """
    # دریافت اطلاعات
    user_exam = get_object_or_404(UserExam, id=user_exam_id)
    user_answers = UserAnswer.objects.filter(
        user_exam=user_exam
    ).select_related('question').order_by('question_id')
    
    # ایجاد پاسخ HTTP با محتوای PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="answer_sheet_{user_exam.profile.user_name}.pdf"'
    
    # تنظیم مسیر فونت فارسی
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'shabnam', 'Shabnam-Medium.ttf')
    
    # اگر فونت موجود نیست از فونت پیش‌فرض استفاده کن
    try:
        pdfmetrics.registerFont(TTFont('shabnam', font_path))
        font_name = 'shabnam'
    except:
        font_name = 'Helvetica'
    
    # ایجاد سند PDF
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=30,
        bottomMargin=20
    )
    
    # استایل‌ها
    styles = getSampleStyleSheet()
    
    # استایل عنوان اصلی
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=20,
    )
    
    # استایل هدر
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=12,
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#2563eb'),
    )
    
    # استایل متن معمولی
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        alignment=TA_RIGHT,
        leading=18,
    )

    
    # استایل پاسخ
    answer_style = ParagraphStyle(
        'AnswerStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#065f46'),
        backColor=colors.HexColor('#d1fae5'),
        leading=16,
    )
    
    # محتوای PDF
    story = []
    
    # عنوان اصلی
    title = Paragraph(f"<b>پاسخ‌نامه آزمون: {user_exam.exam.title}</b>", title_style)
    story.append(title)
    story.append(Spacer(1, 10))
    
    # اطلاعات کاربر
    user_info = Paragraph(
        f"<b>نام کاربر:</b> {user_exam.profile.user_name}<br/>"
        f"<b>تاریخ:</b> {user_exam.started_date}<br/>"
        f"<b>تعداد سوالات:</b> {user_answers.count()}",
        header_style
    )
    story.append(user_info)
    story.append(Spacer(1, 20))
    
    # جدول اصلی سوالات
    for idx, answer in enumerate(user_answers, start=1):
        # نوع سوال
        q_type = answer.question.question_type
        
        # نمایش پاسخ بر اساس نوع سوال
        if q_type == 'numeric':
            # سوال عددی
            user_answer = answer.answer_value if answer.answer_value != '-' else 'پاسخ داده نشده'
            answer_html = f"<b>پاسخ کاربر:</b> {user_answer}"
            if answer.question.correct_answer:
                answer_html += f"<br/><b>پاسخ صحیح:</b> {answer.question.correct_answer}"
            story.append(Paragraph(answer_html, answer_style))
            
        elif q_type == 'multi_choice':
            # سوال تستی
            user_answer = answer.answer_value if answer.answer_value != '-' else 'پاسخ داده نشده'
            answer_html = f"<b>پاسخ کاربر:</b> گزینه {user_answer}"
            if answer.question.correct_answer:
                answer_html += f"<br/><b>پاسخ صحیح:</b> گزینه {answer.question.correct_answer}"
            story.append(Paragraph(answer_html, answer_style))
            
        elif q_type == 'true_false_set':
            # سوال صحیح/غلط ۵ ستونه
            answers_list = answer.answer_value.split(',') if answer.answer_value and answer.answer_value != '-' else []
            correct_list = answer.question.correct_answer.split(',') if answer.question.correct_answer else []
            
            # ساخت جدول برای نمایش ۵ ستون
            tf_data = []
            headers = ['ستون 1', 'ستون 2', 'ستون 3', 'ستون 4', 'ستون 5']
            tf_data.append(headers)
            
            # ردیف پاسخ کاربر
            user_row = []
            for i in range(5):
                if i < len(answers_list):
                    val = answers_list[i]
                    if val == 'T':
                        user_row.append('✓ صحیح')
                    elif val == 'F':
                        user_row.append('✗ غلط')
                    else:
                        user_row.append('-')
                else:
                    user_row.append('-')
            tf_data.append(user_row)
            
            # ردیف پاسخ صحیح
            correct_row = []
            for i in range(5):
                if i < len(correct_list):
                    val = correct_list[i]
                    if val == 'T':
                        correct_row.append('✓ صحیح')
                    elif val == 'F':
                        correct_row.append('✗ غلط')
                    else:
                        correct_row.append('-')
                else:
                    correct_row.append('-')
            tf_data.append(correct_row)
            
            # ساخت جدول
            tf_table = Table(tf_data, colWidths=[60, 60, 60, 60, 60])
            tf_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#d1fae5')),
                ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#fef3c7')),
            ]))
            
            story.append(Spacer(1, 5))
            story.append(Paragraph("<b>پاسخ‌های ثبت شده:</b>", normal_style))
            story.append(tf_table)
        
        # جداکننده بین سوالات
        story.append(Spacer(1, 15))
        story.append(Paragraph("<hr/>", normal_style))
        story.append(Spacer(1, 5))
    
    # ساخت PDF
    doc.build(story)
    return response