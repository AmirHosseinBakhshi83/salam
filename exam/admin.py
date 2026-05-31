from django.contrib import admin
from .models import Exam,UserExam,Question, UserAnswer
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse,path
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.db.models import Count, Q, Avg
from personal.models import Profile
import csv
import io
from datetime import datetime

class QuestionInline(admin.TabularInline):  # or admin.StackedInline for vertical layout
    model = Question
    extra = 1  # Number of empty forms to display
    fields = ['order', 'question_type', 'correct_answer']
    ordering = ['order']
    show_change_link = True  # Link to edit question separately if needed
    
    # Optional: Add custom styling
    classes = ['collapse']  # Collapsible section
    # classes = ['wide']  # Wider form
    
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'tag', 'exam_type', 'start_date', 'end_date', 
                   'participants_count', 'completed_count', 'scoreboard_buttons']
    list_filter = ['tag', 'exam_type', 'start_date']
    search_fields = ['title']
    inlines = [QuestionInline]  # This shows questions inside exam edit page
    fieldsets = (
        ('Exam Information', {
            'fields': ('title', 'pdf_file', 'tag', 'exam_type', 'question_count', 'start_date', 'end_date', 'duration_lenght')
        }),
    )
        
    # Optional: Add actions
    actions = ['duplicate_exam','export_selected_scoreboards']
    
    def duplicate_exam(self, request, queryset):
        for exam in queryset:
            exam.pk = None
            exam.title = f"Copy of {exam.title}"
            exam.save()
        self.message_user(request, "Exams duplicated successfully!")
    duplicate_exam.short_description = "Duplicate selected exams"



    def recalculate_button(self, obj):
        """Add a button to recalculate scores for this exam"""
        return format_html(
            '<a class="button" href="{}" style="background-color: #ba2121; color: white; padding: 4px 8px; text-decoration: none; border-radius: 4px;">Recalculate Scores</a>',
            reverse('admin:recalculate_exam_scores', args=[obj.id])
        )
    recalculate_button.short_description = 'Recalculate Scores'
    recalculate_button.allow_tags = True


    def recalculate_exam_scores(self, request, exam_id):
        """Recalculate all scores for an exam"""
        try:
            exam = Exam.objects.get(id=exam_id)
            user_exams = UserExam.objects.filter(exam=exam, is_completed=True)
            
            if not user_exams.exists():
                self.message_user(request, f"No completed exams found for '{exam.title}'", messages.WARNING)
                return redirect(request.META.get('HTTP_REFERER', '../'))
            
            updated_count = 0
            for user_exam in user_exams:
                if hasattr(user_exam, 'recalculate_score'):
                    user_exam.recalculate_score()
                    updated_count += 1
            
            self.message_user(
                request, 
                f"Successfully recalculated {updated_count} exam(s) for '{exam.title}'",
                messages.SUCCESS
            )
            
        except Exam.DoesNotExist:
            self.message_user(request, "Exam not found", messages.ERROR)
        
        return redirect(request.META.get('HTTP_REFERER', '../'))
    
    
    
    
    
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            participants_count=Count('participants', filter=Q(participants__is_completed=True)),
            completed_count=Count('participants', filter=Q(participants__is_completed=True, participants__score__isnull=False))
        )
        return queryset
    
    def participants_count(self, obj):
        return obj.participants_count
    participants_count.short_description = "Total Participants"
    
    def completed_count(self, obj):
        return obj.completed_count
    completed_count.short_description = "Completed"
    
    def scoreboard_buttons(self, obj):
        """Display buttons for scoreboard actions directly in admin list"""
        return format_html(
            '<div style="white-space: nowrap;">'
            '<a class="button" href="{}" style="background-color: #2196F3; color: white; padding: 4px 8px; text-decoration: none; border-radius: 4px; margin-right: 5px; font-size: 12px;">📊 CSV</a>'
            '<a class="button" href="{}" style="background-color: #4CAF50; color: white; padding: 4px 8px; text-decoration: none; border-radius: 4px; margin-right: 5px; font-size: 12px;">📈 Excel</a>'
            '<a class="button" href="{}" style="background-color: #f44336; color: white; padding: 4px 8px; text-decoration: none; border-radius: 4px; font-size: 12px;">🔄 Recalc</a>',
            '<a class="button" href="{}" style="background-color: #FF9800; color: white; padding: 4px 8px; text-decoration: none; border-radius: 4px; font-size: 12px;">🔄 View</a>',
            '</div>',
            reverse('admin:export_csv_scoreboard', args=[obj.id]),
            reverse('admin:export_excel_scoreboard', args=[obj.id]),
            reverse('admin:recalculate_exam_scores', args=[obj.id]),
            reverse('admin:view_scoreboard_html', args=[obj.id]),
        )
    scoreboard_buttons.short_description = 'Scoreboard'
    scoreboard_buttons.allow_tags = True
    
    def export_selected_scoreboards(self, request, queryset):
        """Export scoreboards for selected exams as CSV"""
        import zipfile
        import tempfile
        import os
        
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, 'scoreboards.zip')
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for exam in queryset:
                # Generate CSV in memory
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write headers
                writer.writerow(['Rank', 'Username', 'Name', 'Email', 'Score', 'Percentage', 'Completed At'])
                
                # Get data
                user_exams = UserExam.objects.filter(
                    exam=exam,
                    is_completed=True,
                    score__isnull=False
                ).select_related('profile__user').order_by('-percentage_score', '-score', 'completed_at')
                
                current_rank = 1
                previous_score = None
                
                for idx, ue in enumerate(user_exams, 1):
                    if previous_score != ue.percentage_score:
                        current_rank = idx
                    
                    writer.writerow([
                        current_rank,
                        ue.profile.user.username,
                        ue.profile.user_name or '',
                        ue.profile.user.email,
                        float(ue.score),
                        f"{float(ue.percentage_score)}%",
                        ue.completed_at.strftime('%Y-%m-%d %H:%M:%S') if ue.completed_at else ''
                    ])
                    previous_score = ue.percentage_score
                
                # Add to zip
                zipf.writestr(f"{exam.title}_{exam.id}.csv", output.getvalue())
        
        with open(zip_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="scoreboards.zip"'
            return response
    
    export_selected_scoreboards.short_description = "Export selected scoreboards as CSV (ZIP)"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-csv/<int:exam_id>/', 
                 self.admin_site.admin_view(self.export_csv_scoreboard),
                 name='export_csv_scoreboard'),
            path('export-excel/<int:exam_id>/', 
                 self.admin_site.admin_view(self.export_excel_scoreboard),
                 name='export_excel_scoreboard'),
            path('view-scoreboard/<int:exam_id>/', 
                 self.admin_site.admin_view(self.view_scoreboard_html),
                 name='view_scoreboard_html'),
            path('recalculate/<int:exam_id>/', 
                 self.admin_site.admin_view(self.recalculate_exam_scores),
                 name='recalculate_exam_scores'),
        ]
        return custom_urls + urls
    
    def export_csv_scoreboard(self, request, exam_id):
        """Export scoreboard as CSV file"""
        try:
            exam = Exam.objects.get(id=exam_id)
            
            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="scoreboard_{exam.title}_{exam.id}.csv"'
            
            writer = csv.writer(response)
            
            # Write headers
            writer.writerow(['Rank', 'Username', 'Name', 'Email', 'Score', 'Percentage Score', 'Completed At', 'Duration (minutes)'])
            
            # Get data
            user_exams = UserExam.objects.filter(
                exam=exam,
                is_completed=True,
                score__isnull=False
            ).select_related('profile__user').order_by('-percentage_score', '-score', 'completed_at')
            
            current_rank = 1
            previous_score = None
            
            for idx, ue in enumerate(user_exams, 1):
                if previous_score != ue.percentage_score:
                    current_rank = idx
                
                # Calculate duration
                duration = ""
                if ue.started_date and ue.completed_at:
                    delta = ue.completed_at - ue.started_date
                    duration = f"{delta.total_seconds() / 60:.1f}"
                
                writer.writerow([
                    current_rank,
                    ue.profile.user.username,
                    ue.profile.user_name or '',
                    ue.profile.user.email,
                    float(ue.score),
                    f"{float(ue.percentage_score)}%",
                    ue.completed_at.strftime('%Y-%m-%d %H:%M:%S') if ue.completed_at else '',
                    duration
                ])
                previous_score = ue.percentage_score
            
            return response
            
        except Exam.DoesNotExist:
            self.message_user(request, "Exam not found", messages.ERROR)
            return redirect('../')
    
    def export_excel_scoreboard(self, request, exam_id):
        """Export scoreboard as Excel file using simple HTML table (works without pandas)"""
        try:
            exam = Exam.objects.get(id=exam_id)
            
            # Create HTML response that Excel can open
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'attachment; filename="scoreboard_{exam.title}_{exam.id}.xls"'
            
            # Get data
            user_exams = UserExam.objects.filter(
                exam=exam,
                is_completed=True,
                score__isnull=False
            ).select_related('profile__user').order_by('-percentage_score', '-score', 'completed_at')
            
            # Build HTML table
            html = ['<html><head><meta charset="UTF-8"><title>Scoreboard</title></head><body>']
            html.append(f'<h2>Scoreboard: {exam.title}</h2>')
            html.append('<table border="1" cellpadding="5" cellspacing="0">')
            
            # Headers
            html.append('<tr style="background-color: #4CAF50; color: white;">')
            for header in ['Rank', 'Username', 'Name', 'Email', 'Score', 'Percentage', 'Completed At', 'Duration (min)']:
                html.append(f'<th>{header}</th>')
            html.append('</tr>')
            
            # Data rows
            current_rank = 1
            previous_score = None
            
            for idx, ue in enumerate(user_exams, 1):
                if previous_score != ue.percentage_score:
                    current_rank = idx
                
                # Calculate duration
                duration = ""
                if ue.started_date and ue.completed_at:
                    delta = ue.completed_at - ue.started_date
                    duration = f"{delta.total_seconds() / 60:.1f}"
                
                # Row color based on percentage
                bgcolor = ''
                if ue.percentage_score and float(ue.percentage_score) >= 80:
                    bgcolor = ' style="background-color: #C6EFCE;"'
                elif ue.percentage_score and float(ue.percentage_score) >= 60:
                    bgcolor = ' style="background-color: #FFEB9C;"'
                elif ue.percentage_score and float(ue.percentage_score) < 60:
                    bgcolor = ' style="background-color: #FFC7CE;"'
                
                html.append(f'<tr{bgcolor}>')
                html.append(f'<td>{current_rank}</td>')
                html.append(f'<td>{ue.profile.user.username}</td>')
                html.append(f'<td>{ue.profile.user_name or ""}</td>')
                html.append(f'<td>{ue.profile.user.email}</td>')
                html.append(f'<td>{float(ue.score)}</td>')
                html.append(f'<td><strong>{float(ue.percentage_score)}%</strong></td>')
                html.append(f'<td>{ue.completed_at.strftime("%Y-%m-%d %H:%M:%S") if ue.completed_at else ""}</td>')
                html.append(f'<td>{duration}</td>')
                html.append('</tr>')
                
                previous_score = ue.percentage_score
            
            html.append('</table>')
            
            # Add statistics
            if user_exams:
                avg_score = user_exams.aggregate(Avg('percentage_score'))['percentage_score__avg']
                html.append(f'<p><strong>Total Participants:</strong> {user_exams.count()}</p>')
                html.append(f'<p><strong>Average Score:</strong> {avg_score:.2f}%</p>')
            
            html.append('</body></html>')
            
            response.write('\n'.join(html))
            return response
            
        except Exam.DoesNotExist:
            self.message_user(request, "Exam not found", messages.ERROR)
            return redirect('../')
    
    def view_scoreboard_html(self, request, exam_id):
        """Display scoreboard as HTML in admin panel"""
        try:
            exam = Exam.objects.get(id=exam_id)
            
            # Get data
            user_exams = UserExam.objects.filter(
                exam=exam,
                is_completed=True,
                score__isnull=False
            ).select_related('profile__user').order_by('-percentage_score', '-score', 'completed_at')
            
            # Build HTML directly in response
            html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Scoreboard - {exam.title}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }}
                    .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
                    .stats {{ background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    .stats p {{ margin: 5px 0; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    th {{ background: #4CAF50; color: white; padding: 12px; text-align: left; }}
                    td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
                    tr:hover {{ background: #f5f5f5; }}
                    .rank-1 {{ background: #FFD700; font-weight: bold; }}
                    .rank-2 {{ background: #C0C0C0; font-weight: bold; }}
                    .rank-3 {{ background: #CD7F32; font-weight: bold; }}
                    .button {{
                        display: inline-block;
                        padding: 8px 16px;
                        margin: 10px 5px;
                        background: #4CAF50;
                        color: white;
                        text-decoration: none;
                        border-radius: 4px;
                    }}
                    .button:hover {{ background: #45a049; }}
                    .nav {{ margin-bottom: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="nav">
                        <a href="/admin/exam/exam/" class="button">← Back to Exams</a>
                        <a href="/admin/exam/exam/export-csv/{exam.id}/" class="button" style="background: #2196F3;">📥 Download CSV</a>
                        <a href="/admin/exam/exam/export-excel/{exam.id}/" class="button" style="background: #FF9800;">📊 Download Excel</a>
                    </div>
                    
                    <h1>Scoreboard: {exam.title}</h1>
                    
                    <div class="stats">
            '''
            
            # Add statistics
            total_participants = user_exams.count()
            if total_participants > 0:
                avg_score = user_exams.aggregate(Avg('percentage_score'))['percentage_score__avg']
                top_score = user_exams.first()
                html += f'''
                        <p><strong>📊 Total Participants:</strong> {total_participants}</p>
                        <p><strong>⭐ Average Score:</strong> {avg_score:.2f}%</p>
                        <p><strong>🏆 Top Score:</strong> {float(top_score.percentage_score)}% ({top_score.profile.user.username})</p>
                '''
            else:
                html += '<p>No participants yet.</p>'
            
            html += '''
                    </div>
                    
                    <table>
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Username</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Score</th>
                                <th>Percentage</th>
                                <th>Completed At</th>
                                <th>Duration (min)</th>
                            </tr>
                        </thead>
                        <tbody>
            '''
            
            # Add data rows
            current_rank = 1
            previous_score = None
            
            for idx, ue in enumerate(user_exams, 1):
                if previous_score != ue.percentage_score:
                    current_rank = idx
                
                # Calculate duration
                duration = ""
                if ue.started_date and ue.completed_at:
                    delta = ue.completed_at - ue.started_date
                    duration = f"{delta.total_seconds() / 60:.1f}"
                
                # Row class for top 3
                row_class = ''
                if current_rank == 1:
                    row_class = 'rank-1'
                elif current_rank == 2:
                    row_class = 'rank-2'
                elif current_rank == 3:
                    row_class = 'rank-3'
                
                # Color code percentage
                percent_color = ''
                if ue.percentage_score and float(ue.percentage_score) >= 80:
                    percent_color = 'color: #4CAF50; font-weight: bold;'
                elif ue.percentage_score and float(ue.percentage_score) >= 60:
                    percent_color = 'color: #FF9800; font-weight: bold;'
                elif ue.percentage_score and float(ue.percentage_score) < 60:
                    percent_color = 'color: #f44336; font-weight: bold;'
                
                html += f'''
                    <tr class="{row_class}">
                        <td><strong>{current_rank}</strong></td>
                        <td>{ue.profile.user.username}</td>
                        <td>{ue.profile.user_name or '-'}</td>
                        <td>{ue.profile.user.email}</td>
                        <td>{float(ue.score)}</td>
                        <td style="{percent_color}">{float(ue.percentage_score)}%</td>
                        <td>{ue.completed_at.strftime('%Y-%m-%d %H:%M:%S') if ue.completed_at else '-'}</td>
                        <td>{duration}</td>
                    </tr>
                '''
                previous_score = ue.percentage_score
            
            html += '''
                        </tbody>
                    </table>
                </div>
            </body>
            </html>
            '''
            
            return HttpResponse(html)
            
        except Exam.DoesNotExist:
            return HttpResponse('<h1>Exam not found</h1>', status=404)


# Customize Question admin separately if needed
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'exam', 'order', 'question_type', 'correct_answer']
    list_filter = ['exam', 'question_type']
    search_fields = ['exam__title', 'correct_answer']
    list_editable = ['order', 'correct_answer']  # Inline editing in list view
    ordering = ['exam', 'order']
    
    # Add bulk actions
    actions = ['bulk_change_type']
    
    def bulk_change_type(self, request, queryset):
        # Example bulk action
        for question in queryset:
            question.question_type = 'multi_choice'
            question.save()
        self.message_user(request, f"Updated {queryset.count()} questions")
    bulk_change_type.short_description = "Change type to Multi-choice"

@admin.register(UserExam)
class UserExamAdmin(admin.ModelAdmin):
    list_display = ['exam', 'profile', 'is_completed', 'score', 'total_possible_score', 'percentage_score']
    list_filter = ['exam', 'is_completed']
    actions = ['recalculate_selected_scores']
    
    def recalculate_selected_scores(self, request, queryset):
        """Recalculate scores for selected user exams"""
        updated_count = 0
        total_score_sum = 0
        
        for user_exam in queryset.filter(is_completed=True):
            old_score = user_exam.score or 0
            result = user_exam.recalculate_score()
            updated_count += 1
            total_score_sum += result['score']
            
        average = total_score_sum / updated_count if updated_count > 0 else 0
        
        self.message_user(
            request,
            f"Recalculated {updated_count} exam(s). Average score: {average:.2f}",
            messages.SUCCESS
        )
    
    recalculate_selected_scores.short_description = "Recalculate scores for selected exams"

# Register your models here.
admin.site.register(Exam, ExamAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(UserAnswer)