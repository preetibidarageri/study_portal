from django.shortcuts import render

# to create registeration api add the following imports
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer

# to create profile api add folloiwng imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# added this import to create Branch Api
from .models import Branch,Semester


class RegisterView(generics.CreateAPIView):
    serializer_class  = RegisterSerializer
    permission_classes = [AllowAny]

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile

        return Response({
            'username':request.user.username,
            'email':request.user.email,
            'first_name':request.user.first_name,
            'last_name':request.user.last_name,
            'role':profile.role,
        })

class BranchListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        branches = Branch.objects.all().values('id', 'name')
        return Response({
            'branches': list(branches)
        })

class  SemesterListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        branch_id = request.query_params.get('branch_id')
        if not branch_id:
            return Response({
                'error': "Please Provide Branch Id"
            }, status=400)

        semesters = Semester.objects.filter(branch_id=branch_id).values('id', 'number', 'name')
        return Response({
            'semesters': list(semesters)
        })

