from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile

class RegisterSerializer (serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_lenght=8)
    role = serializers.ChoiceField(choices=UserProfile.ROLECHOICES)

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
        if User.objects.filter(email_iexact=value).exists():
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
