from django.urls import path
from .views import RegisterView
# for login api creation added this import
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# profile API added this import
from .views import RegisterView, UserProfileView, BranchListView, SemesterListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/',TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('branches/', BranchListView.as_view(), name='branch_list'),
    path('semesters/', SemesterListView.as_view(), name='semester_list')

]