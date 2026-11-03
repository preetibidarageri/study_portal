from django.contrib import admin
from .models import Branch, Scheme, Semester, UserProfile, Subject, Module, Material

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_field = ('name', 'code')
    ordering = ('name',)

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("scheme", "number", "name")
    list_filter = ("scheme", "number")
    search_fields = ("scheme__name","scheme__code","scheme__branch__name","scheme__branch__code","name",)
    ordering = ("scheme", "number")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user','role')
    list_filter = ['role']
    search_fields = ('user__username', 'user__email')
    ordering = ('user__username',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'branch', 'semester')
    list_filter = ('branch', 'semester')
    search_fields = ('name', 'code', 'branch__name', 'semester__name')
    ordering = ('name',)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('subject', 'number', 'name')       
    list_filter = ('subject',)
    search_fields = ('name', 'subject__name') 
    ordering = ('subject', 'number')

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("heading","module","category","uploaded_by","uploaded_at",)
    list_filter = ("category", "uploaded_at")
    search_fields = ("heading", "description", "module__name")
    ordering = ("-uploaded_at",)

@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "branch")
    list_filter = ("branch",)
    search_fields = ("name", "code", "branch__name", "branch__code")
    ordering = ("branch", "name")

