from django.db import models
from django.utils import timezone
from decimal import Decimal

# Create your models here.

class Exam(models.Model):
    TYPE_CHOICES = (
        ('M1', 'Marhale 1'),
        ('M2', 'Marhale 2'),
    )
    title = models.CharField(max_length=200)
    tag = models.CharField(max_length=200, default='')
    exam_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    question_count = models.PositiveIntegerField(default=25, null=False)
    pdf_file = models.FileField(upload_to='media/exams/pdfs/q/' )
    answer_pdf_file = models.FileField(upload_to='media/exams/pdfs/a/', default='')
    created_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(default= timezone.now)
    end_date = models.DateTimeField(default= timezone.now)
    duration_lenght = models.IntegerField(default=120, null=False)
    status = models.BooleanField(default=False)
    def __str__(self):
        return self.title
    

class Question(models.Model):
    TYPE_CHOICES = (
        ('multi_choice', '5-Choice Question'),
        ('true_false_set', '5-Boolean Statements'),
        ('numeric', 'Numeric Answer'),
    )
    
    exam = models.ForeignKey('Exam', on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES)  
    correct_answer = models.CharField(max_length=50 , null=True) 
    order = models.PositiveIntegerField(default=0, help_text="Question order in exam")
    
    class Meta:
        ordering = ['order', 'id']
        
    def __str__(self):
        return f"{self.exam.title} - Q{self.id} ({self.question_type})"
  


class UserExam(models.Model):
    profile = models.ForeignKey('personal.Profile', on_delete=models.CASCADE, related_name='assigned_exams')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='participants')
    is_completed = models.BooleanField(default=False)
    started_date = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_possible_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    percentage_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('profile', 'exam')

    def get_remaining_seconds(self):
        if self.is_completed:
            return 0
        
        elapsed = timezone.now() - self.started_date
        total_seconds = self.exam.duration_lenght * 60  # Convert minutes to seconds
        remaining = total_seconds - elapsed.total_seconds()
        
        return max(0, int(remaining))
    
    def is_expired(self):
        return self.get_remaining_seconds() <= 0
    
    def recalculate_score(self):
        """Recalculate score for this exam based on current answers and question correct answers"""
        user_answers = self.answers.select_related('question').all()
        
        total_score = Decimal('0')
        total_possible = Decimal('0')
        
        for user_answer in user_answers:
            question = user_answer.question
            
            # Get question points based on type
            if question.question_type == "true_false_set":
                points = Decimal('5')  # 5 points total for true_false_set
                total_possible += points
                
                question_score = self._calculate_true_false_set_score(
                    user_answer.answer_value, 
                    question.correct_answer,
                    points
                )
                total_score += question_score
                
            elif question.question_type == "multi_choice":
                # Check if answer is number or character
                try:
                    # Try to convert to int to see if it's numeric
                    int(question.correct_answer)
                    points = Decimal('6')  # Numeric answers: 6 points
                except (ValueError, TypeError):
                    points = Decimal('5')  # Character answers: 5 points
                
                total_possible += points
                
                if self._calculate_multi_choice_score(user_answer.answer_value, question.correct_answer):
                    total_score += points
                # else: 0 points for incorrect
                
            elif question.question_type == "numeric":
                points = Decimal('6')  # Numeric answers: 6 points
                total_possible += points
                
                if self._calculate_numeric_score(user_answer.answer_value, question.correct_answer):
                    total_score += points
                # else: 0 points for incorrect
        
        # Calculate percentage
        percentage = (total_score / total_possible) * 100

        # Store results
        self.score = total_score
        self.total_possible_score = total_possible
        self.percentage_score = percentage
        self.save()
        
        return {
            'score': float(total_score),
            'total_possible': float(total_possible),
            'percentage': float(percentage)
        }
    
    def _calculate_true_false_set_score(self, user_answer, correct_answer, total_points):
        """
        Calculate score for true_false_set questions
        user_answer and correct_answer are strings like "TFTTF" or "BBBBB"
        B means both T and F are correct
        """
        if not user_answer or user_answer == "unanswered" or not correct_answer:
            return Decimal('0')
        
        # Split into individual answers
        user_parts = user_answer.split(',')
        correct_parts = list(correct_answer)
        print( user_parts + correct_parts)
        
        # Ensure both have the same length
        min_length = min(len(user_parts), len(correct_parts))
        if min_length == 0:
            return Decimal('0')
        
        # Count correct answers
        correct_count = 0
        incorrect_count = 0
        
        for i in range(min_length):
            user_val = user_parts[i].upper()
            correct_val = correct_parts[i].upper()
            
            # B means both T and F are correct
            if correct_val == 'B':
                # Always correct regardless of user answer
                correct_count += 1
            elif user_val == correct_val:
                correct_count += 1
            elif user_val != correct_val and user_val!='X':
                incorrect_count += 1
        
        # Calculate score based on correct count (5, 4, 3, 2, 1, 0)
        if correct_count == 5:
            positive_score = Decimal('5')  # 100%
        elif correct_count == 4:
            positive_score = Decimal('3')  # 60% of total (3/5)
        elif correct_count == 3:
            positive_score = Decimal('2')  # 40% of total (2/5)
        elif correct_count == 2:
            positive_score = Decimal('1')  # 20% of total (1/5)
        else:  # 1 or 0 correct
            positive_score = Decimal('0')
        
        # Subtract 0.1 of total_points for each incorrect answer
        negative_penalty = Decimal(str(incorrect_count* 0.5)) 
        
        
        # Final score cannot be negative
        final_score = positive_score - negative_penalty
        
        return final_score
    
    def _calculate_multi_choice_score(self, user_answer, correct_answer):
        """Calculate score for multi_choice questions (character or number)"""
        if not user_answer or user_answer == "unanswered":
            return False
        
        # Compare as strings, case-insensitive, stripped
        return user_answer.strip().upper() == str(correct_answer).strip().upper()
    
    def _calculate_numeric_score(self, user_answer, correct_answer):
        """Calculate score for numeric questions with tolerance"""
        if not user_answer or user_answer == "unanswered":
            return False
        
        try:
            user_num = float(user_answer)
            correct_num = float(correct_answer)
            # Tolerance of 0.001 for floating point comparisons
            return abs(user_num - correct_num) < 0.001
        except (ValueError, TypeError):
            return False
    def __str__(self):
        return self.exam.title



class UserAnswer(models.Model):
    user_exam = models.ForeignKey('UserExam', on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_value = models.CharField(max_length=10,
        blank=True,           # Allows empty form submission
        null=False,           # Don't allow NULL in database
        default="-",)

    class Meta:
        unique_together = ('user_exam', 'question') # هر سوال در هر آزمون فقط یک پاسخ دارد




class ScoreBoard(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='scoreboards')
    profile = models.ForeignKey('personal.Profile', on_delete=models.CASCADE, related_name='scoreboard_entries')
    rank = models.PositiveIntegerField(null=True, blank=True)
    percentage_score = models.DecimalField(max_digits=5, decimal_places=2)
    completed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['exam', 'rank']
        unique_together = ['exam', 'profile']  # Each profile can have only one scoreboard entry per exam
    
    def __str__(self):
        return f"{self.exam.title} - {self.profile.user.username} - Rank {self.rank}"