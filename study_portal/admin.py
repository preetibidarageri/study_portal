from django.contrib import admin
from .models import Branch, Semester, UserProfile

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_field = ('name', 'code')
    ordering = ('name',)

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('branch', 'number', 'name')
    list_filter = ('branch', 'number')
    search_field = ('branch_name', 'branch_code', 'name')
    ordering = ('branch', 'number')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user','role')
    list_filter = ['role']
    search_fields = ('user__username', 'user__email')
    ordering = ('user__username',)