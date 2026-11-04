from django.db import models
from django.contrib.auth.models import User

class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class Scheme(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE,related_name="schemes",)
    name = models.CharField(max_length=50)  
    code = models.CharField(max_length=20)
    class Meta:
        ordering = ["branch", "name"]
        constraints = [models.UniqueConstraint(fields=["branch", "code"],name="unique_scheme_code_per_branch",)]
    def __str__(self):
        return f"{self.branch.code} - {self.name}"

class Semester(models.Model):
    scheme = models.ForeignKey(Scheme,on_delete=models.CASCADE,related_name="semesters",)    
    number = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=50, blank=True)
    def __str__(self):
        return f"{self.scheme} - Semester {self.number}"
    class Meta:
        ordering = ["scheme", "number"]
        constraints = [models.UniqueConstraint(fields=["scheme", "number"],name="unique_semester_per_scheme",)]

class UserProfile(models.Model):
    ROLE_CHOICES = [('student', 'student'), ('teacher', 'teacher')]
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'profile')
    role = models.CharField(max_length=10, choices = ROLE_CHOICES)
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Subject(models.Model):
    branch = models.ForeignKey(Branch, on_delete = models.CASCADE, related_name = "Subjects")
    semester = models.ForeignKey(Semester, on_delete = models.CASCADE, related_name = "Subjects")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    class Meta:
        ordering = ['name']
        constraints=[models.UniqueConstraint(fields=['semester', 'name'], name='unique_subject_per_semester')]
    def __str__(self):
        return f"{self.name} - {self.semester}"

class Module(models.Model):
    subject = models.ForeignKey(Subject, on_delete = models.CASCADE, related_name = "modules")
    number = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    class Meta:
        ordering = ['number']
        constraints=[models.UniqueConstraint(fields=['subject', 'number'], name='unique_module_number_per_subject')]
    def __str__(self):
        return f"{self.subject}- Module {self.number}: {self.name}"

class Material(models.Model):
    CATEGORY_CHOICES = [
        ("pdf", "PDF"),
        ("ppt", "PowerPoint"),
        ("video", "Video Link"),
        ("link", "External Link"),
    ]    
    module = models.ForeignKey(Module,on_delete=models.CASCADE,related_name="materials",)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    heading = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="materials/%Y/%m/",blank=True,null=True,)
    video_url = models.URLField(blank=True)
    uploaded_by = models.ForeignKey("auth.User",on_delete=models.SET_NULL,null=True,blank=True,related_name="uploaded_materials",)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["category", "uploaded_at"]
    def __str__(self):
        return self.heading or (
            f"{self.get_category_display()} - Module {self.module.number}"
        )