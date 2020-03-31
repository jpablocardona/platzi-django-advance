"""Users serializes"""

# Django
from django.conf import settings
from django.db import models
from django.contrib.auth import authenticate, password_validation
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password

# Djangto rest framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# Task
from cride.taskapp.tasks import send_confirmation_email

# User
from cride.users.models import User, Profile

# Serializers
from .profiles import ProfileModelSerializer


class UserModelSerializer(serializers.ModelSerializer):
    """User model serializer"""

    profile = ProfileModelSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'profile'
        )
        # Esto trae la informacion del modelo
        # depth = 1


class UserLoginSerializer(serializers.Serializer):
    """ User login serializers """

    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)

    def validate(self, data):
        """Check credencitals"""
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        if not user.is_verified:
            raise serializers.ValidationError('Account is not activate yet :(')
        self.context['user'] = user
        return data

    def create(self, data):
        """Generate token auth"""
        token, created = Token.objects.get_or_create(user=self.context['user'])
        return self.context['user'], token.key


class UserSingUpSerializer(serializers.Serializer):
    """ User sing up serializers """

    username = serializers.CharField(
        min_length=4,
        max_length=20,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    first_name = serializers.CharField(min_length=2, max_length=30)
    last_name = serializers.CharField(min_length=2, max_length=30)
    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}%',
        message='phone number must be entered in the format: +9999999. Up to 15 digits allowed'
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    password = serializers.CharField(min_length=8, max_length=64)
    password_confirmation = serializers.CharField(min_length=8, max_length=64)

    def validate(self, data):
        """ Handle validate info user"""
        passwd = data['password']
        passwd_conf = data['password_confirmation']
        if passwd != passwd_conf:
            raise serializers.ValidationError('Passwords does not match')
        password_validation.validate_password(passwd)
        data['password'] = make_password(passwd)
        return data

    def create(self, data):
        """ Handle user create"""
        data.pop('password_confirmation')
        user = User.objects.create(**data, is_verified=False)
        Profile.objects.create(user=user)
        send_confirmation_email.delay(user_pk=user.id)
        return user


class UserVerifiedSerializer(serializers.Serializer):
    """Account verification serialized"""
    token = serializers.CharField()

    def validate(self, data):
        """Handle validate account token"""
        try:
            payload = jwt.decode(data['token'], settings.SECRET_KEY, algorithm='HS256')
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Verification token has expired')
        except jwt.PyJWTError:
            raise serializers.ValidationError('Invalid token')
        if (payload.get('type', '') != 'email_confirmation'):
            raise serializers.ValidationError('Incorrect token')

        self.context['payload'] = payload
        return data

    def save(self):
        """Update users verified account"""
        payload = self.context['payload']
        user = User.objects.get(username=payload['user'])
        if (user.is_verified):
            raise serializers.ValidationError('User already verified')
        user.is_verified = True
        user.save()
