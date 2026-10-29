from django.db import models
from django.contrib.auth.models import User

class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']


class Semester(models.Model):
    branch = models.ForeignKey(Branch,on_delete = models.CASCADE, related_name = 'semester')
    number = models.PositiveSmallIntegerField()
    name = models.CharField(max_length = 50, blank = True)
    def __str__(self):
        return f"{self.branch.code} - Semester {self.number}"
    class Meta:
        ordering = ['branch', 'number']
        constraints = [models.UniqueConstraint(fields=['branch', 'number'], name='unique_semester_per_brnach')]

class UserProfile(models.Model):
    ROLE_CHOICES = [('student', 'student'), ('teacher', 'teacher')]
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'profile')
    role = models.CharField(max_length=10, choices = ROLE_CHOICES)
    def __str__(self):
        return f"{self.user.username} - {self.role}"