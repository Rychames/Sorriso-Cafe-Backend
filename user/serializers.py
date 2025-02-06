from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from user.models import CustomUser, EmailVerificationCode

class UserSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'profile_image',
            'email',
            'first_name',
            'last_name',
            'role',
            'is_active',
        ]
        extra_kwargs = {
            'email': {'read_only': True},
        }
    
    def get_is_admin(self, obj):
        return obj.is_staff
    
    def get_is_active(self, obj):
        return obj.is_active
    
    def validate_email(self, value):
        """
        Valida o campo email apenas se ele foi alterado.
        """
        user = self.instance  # Usuário existente
        if user and user.email == value:
            return value  # O email não foi alterado, ignore a validação
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Um usuário com este email já existe.")

    def update(self, instance, validated_data):
        """
            Atualiza os campos do usuário.
        """
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.password = make_password(value)
            else:
                setattr(instance, attr, value)
        return instance

class UserManagerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'profile_image',
            'email',
            'first_name',
            'last_name',
            'role',
            'is_active',
        ]
        extra_kwargs = {
            'profile_image': {'read_only': True},
            'email': {'read_only': True},
            'first_name': {'read_only': True},
            'last_name': {'read_only': True},
        }



class SendCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailVerificationCode
        fields = ['email']

class VerifyCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailVerificationCode
        fields = ['email', 'code', 'is_valid']

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = CustomUser
        fields = ['profile_image', 'email', 'password', 'confirm_password']

    def validate(self, data):

        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("As senhas precisam ser iguais.")

        data.pop('confirm_password', None)
        return data

    def create(self, validated_data):
        password = validated_data.pop('password') 
        user = CustomUser.objects.create(**validated_data)  
        user.set_password(password) 
        user.save()  
        return user
              
class LoginUserSerializer(serializers.ModelSerializer):    
    class Meta:
        model = CustomUser
        fields = ['email', 'password']

