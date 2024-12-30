from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from random import randint
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'mobile', 'role', 'is_approved')
        read_only_fields = ('is_approved',)
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': True},
            'email': {'required': True}  # Ensure email is required
        }

    def create(self, validated_data):
        email = validated_data.get('email')
        if not email:
            raise serializers.ValidationError({"email": "Email must be provided."})

        username = self.generate_unique_username(email)

        # Check the role and set is_staff accordingly
        role = validated_data.get('role')
        is_staff = role == 'admin'  # Only admins should have staff access

        user = User.objects.create_user(
            email=email,
            password=validated_data['password'],
            username=username,
            mobile=validated_data.get('mobile'),
            role=role,
            is_staff=is_staff,  # Set is_staff based on the role
            is_approved=False  # New users are not approved by default
        )
        
        user.otp = randint(10000, 99999)
        user.otp_created_at = timezone.now()  # Add a timestamp for OTP
        user.save()

        self.send_activation_email(user)

        return user

    def generate_unique_username(self, email):
        base_username = email.split('@')[0]
        username = base_username + str(randint(1, 9999))
        while User.objects.filter(username=username).exists():
            username = base_username + str(randint(1, 9999))
        return username

    def send_activation_email(self, user):
        subject = 'Activate Your Account'
        message = f'''
        Hi {user.username}, thank you for registering in the Hospital Management System.
        Your OTP for activating your account is {user.otp}. It is valid for 10 minutes.
        '''
        email_from = 'hims@gmail.com'
        recipient_list = [user.email]
        try:
            send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            raise serializers.ValidationError({"email": f"Error sending email: {str(e)}"})

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = User.objects.filter(email=email).first()

        if user is None:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_approved:
            raise serializers.ValidationError("Your account is not approved by the admin.")

        # Check if password is correct
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        return attrs

class UserActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')
        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError("User not found.")

        if user.otp != otp:
            raise serializers.ValidationError("Invalid OTP.")

        # Check if OTP is expired
        # if user.otp_created_at is None or timezone.now() > user.otp_created_at + timedelta(minutes=10):
        #     raise serializers.ValidationError("OTP has expired.")

        return attrs

    def activate_user(self, validated_data):
        email = validated_data['email']
        user = User.objects.get(email=email)
        user.is_active = True  # Ensure the user is activated
        user.is_approved = True  # Approve the user
        user.save()

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)



from rest_framework import serializers
from .models import User

class UserApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'is_approved')  # Include other fields if necessary

    def validate(self, attrs):
        # Add any additional validation logic here if needed
        return attrs



    
