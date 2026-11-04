from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile
from .models import Subject, Module, Material
from django.conf import settings
from django.core.mail import send_mail

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

        UserProfile.objects.create(
            user=user,
            role=role
        )

        send_mail(
            subject='New registration - SKSV Study Material Portal',
            message=(
                f'A new user has registered.\n\n'
                f'Username: {user.username}\n'
                f'Email: {user.email}\n'
                f'Role: {role}\n'
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.REGISTRATION_NOTIFICATION_EMAIL],
            fail_silently=False,
        )

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
        category = attrs.get(
            "category",
            getattr(self.instance, "category", None)
        )
        uploaded_file = attrs.get("file")
        video_url = attrs.get(
            "video_url",
            getattr(self.instance, "video_url", "")
        )

        if category in ["pdf", "ppt"] and not uploaded_file:
            raise serializers.ValidationError({
                "file": "Upload a file for PDF or PPT materials."
            })

        if category in ["video", "link"] and not video_url:
            raise serializers.ValidationError({
                "video_url": "Enter a link for this material."
            })

        if category == "pdf" and uploaded_file:
            if not uploaded_file.name.lower().endswith(".pdf"):
                raise serializers.ValidationError({
                    "file": "Please upload a PDF file."
                })

        if category == "ppt" and uploaded_file:
            if not uploaded_file.name.lower().endswith((".ppt", ".pptx")):
                raise serializers.ValidationError({
                    "file": "Please upload a PPT or PPTX file."
                })

        return attrs