from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile
from .models import Subject, Module, Material

class RegisterSerializer (serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'role'
        ]
    
    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value
    
    def create(self, validated_data):
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        UserProfile.objects.create(user=user, role=role)
        return user

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "branch", "semester", "name", "code"]
        read_only_fields = ["id"]

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["id", "subject","number", "name", "description"]
        read_only_fields = ["id"]

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = [
            "id",
            "module",
            "category",
            "heading",
            "description",
            "file",
            "video_url",
            "uploaded_by",
            "uploaded_at",
        ]
        read_only_fields = ["id", "uploaded_by", "uploaded_at"]

    def validate(self, attrs):
        category = attrs.get("category")
        file = attrs.get("file")
        video_url = attrs.get("video_url", "")

        if category in ["pdf", "ppt"] and not file:
            raise serializers.ValidationError({
                "file": "Upload a file for PDF or PPT materials."
            })

        if category == "video" and not video_url:
            raise serializers.ValidationError({
                "video_url": "Enter a video link."
            })

        if category == "pdf" and file and not file.name.lower().endswith(".pdf"):
            raise serializers.ValidationError({
                "file": "Please upload a PDF file."
            })

        if category == "ppt" and file and not file.name.lower().endswith((".ppt", ".pptx")):
            raise serializers.ValidationError({
                "file": "Please upload a PPT or PPTX file."
            })

        return attrs
