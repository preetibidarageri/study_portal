from django.shortcuts import render
# to create registeration api add the following imports
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
# to create profile api add folloiwng imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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

 