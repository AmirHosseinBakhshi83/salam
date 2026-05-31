from django.db import models
from exam.models import UserAnswer
# Create your models here.

class UserQuestionReport(models.Model):
    score = models.IntegerField()
    user_answer = models.ForeignKey(UserAnswer, on_delete=models.CASCADE) 
