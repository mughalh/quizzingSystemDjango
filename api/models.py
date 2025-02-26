from django.db import models
from django.contrib.auth.models import User
from django.db import models
import random
import string

class Quiz(models.Model):
    quiz_name = models.CharField(max_length=255, default="Quiz 1")
    date_created = models.DateTimeField(auto_now_add=True)
    join_code = models.CharField(max_length=4, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def generate_join_code(self):
        while True:
            code = ''.join(random.choices(string.digits, k=4))
            if not Quiz.objects.filter(join_code=code).exists():
                self.join_code = code
                self.save()
                return code

    def __str__(self):
        return self.quiz_name

class QuizPlayer(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='players')
    fingerprint_hash = models.CharField(max_length=255)
    nickname = models.CharField(max_length=50)
    joined_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    is_host = models.BooleanField(default=False)

    class Meta:
        unique_together = ['quiz', 'fingerprint_hash']

    def __str__(self):
        return f"{self.nickname} ({self.fingerprint_hash[:8]}...)"

class PlayerAnswer(models.Model):
    quiz_player = models.ForeignKey(QuizPlayer, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    response_time = models.FloatField(help_text="Time taken to answer in seconds")
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['submitted_at']

        

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fingerprint_hash = models.CharField(max_length=255, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Question(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('open_ended', 'Open Ended'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(
        verbose_name="Question Text", 
        help_text="Enter your question here",
        default="New Question"  # Added default value here
    )
    question_type = models.CharField(
        max_length=50, 
        choices=QUESTION_TYPES,
        default='multiple_choice',
        verbose_name="Question Type"
    )
    options = models.JSONField(
        blank=True, 
        null=True,
        help_text="For multiple choice questions, provide options as a JSON array"
    )
    correct_answer = models.TextField(
        blank=True, 
        null=True,
        help_text="The correct answer for the question"
    )
    timer = models.PositiveIntegerField(
        default=30,
        help_text="Time limit in seconds"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order of the question in the quiz"
    )

    class Meta:
        ordering = ['order', 'date_created']
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return f"{self.quiz.quiz_name} - {self.text[:50]}..."

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.question_type == 'multiple_choice' and not self.options:
            raise ValidationError({
                'options': 'Multiple choice questions must have options.'
            })
        if self.question_type == 'true_false':
            if self.correct_answer not in ['True', 'False']:
                raise ValidationError({
                    'correct_answer': 'True/False questions must have either "True" or "False" as the correct answer.'
                })


class Answer(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.fingerprint_hash} - {self.question.text}"

class QuizUser(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.profile.fingerprint_hash} - {self.quiz.quiz_name}"
