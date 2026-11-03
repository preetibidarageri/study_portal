from django.shortcuts import render

# to create registeration api add the following imports
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer,SubjectSerializer, ModuleSerializer, MaterialSerializer

# to create profile api add folloiwng imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

# added this import to create Branch Apiand Semester Api
from .models import Branch, Scheme, Semester,Subject, Module, UserProfile, Material

# validate user role for subject creation
from rest_framework.exceptions import ValidationError
from .permissions import IsTeacherOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser


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
    permission_classes = [IsTeacherOrReadOnly]
    def get(self, request):
        branches = Branch.objects.all().values('id', 'name')
        return Response({
            'branches': list(branches)
        })

class SchemeListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        branch_id = request.query_params.get("branch_id")
        if not branch_id:
            return Response({"error": "Please provide branch_id"},status=400)

        schemes = Scheme.objects.filter(branch_id=branch_id).values("id", "name", "code")
        return Response({
            "schemes": list(schemes)
        })

class  SemesterListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        scheme_id = request.query_params.get('scheme_id')
        if not scheme_id:
            return Response({
                'error': "Please Provide Scheme Id"
            }, status=400)

        semesters = Semester.objects.filter(scheme_id=scheme_id).values('id', 'number', 'name')
        return Response({
            'semesters': list(semesters)
        })

class SubjectListCreateView(generics.ListCreateAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [IsTeacherOrReadOnly]

    def get_queryset(self):
        queryset = Subject.objects.select_related('branch', 'semester')
        branch_id  = self.request.query_params.get('branch_id')
        semester_id = self.request.query_params.get('semester_id')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        if semester_id:
            queryset = queryset.filter(semester_id=semester_id)
        return queryset

    def perform_create(self, serializer):
        branch = serializer.validated_data["branch"]
        semester = serializer.validated_data["semester"]
        if semester.scheme.branch != branch:
            raise ValidationError({"semester": "Semester does not belong to the selected branch."})

        serializer.save()

class ModuleListCreateView(APIView):
    serializer_class = ModuleSerializer
    permission_classes = [IsTeacherOrReadOnly]

    def get(self, request):
        subject_id = request.query_params.get('subject_id')
        if not subject_id:
            return Response({
                'error': "Please Provide Subject Id"
            }, status=status.HTTP_400_BAD_REQUEST)

        modules = Module.objects.filter(subject_id=subject_id).order_by('number')
        serializer = ModuleSerializer(modules, many=True)
        return Response({"modules": serializer.data})

    def post(self, request):
        profile = UserProfile.objects.filter(user=request.user).first()
        if not profile or profile.role != "teacher":
            return Response({"error": "You do not have permission to create a module."}, status=status.HTTP_403_FORBIDDEN)
        serializer = ModuleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MaterialListCreateView(generics.ListCreateAPIView):
    serializer_class = MaterialSerializer
    permission_classes = [IsTeacherOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        queryset = Material.objects.all()        
        module_id = self.request.query_params.get("module_id")
        if module_id:
            queryset = queryset.filter(module_id=module_id)

        return queryset

    def perform_create(self, serializer):
        # Only teachers should be allowed to upload.
        profile = getattr(self.request.user, "profile", None)

        if not profile or profile.role != "teacher":
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only teachers can upload materials.")

        serializer.save(uploaded_by=self.request.user)
