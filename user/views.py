from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from drf_yasg.utils import swagger_auto_schema
from .serializers import UserSerializer, UserLoginSerializer, UserActivationSerializer, UserLogoutSerializer
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @swagger_auto_schema(
        methods=["POST"],
        request_body=UserLoginSerializer
    )
    @action(detail=False, methods=['POST'])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = authenticate(username=email, password=password)
        if user:
            if not user.is_approved:
                return Response(
                    {"detail": "Your account is not approved by the admin."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "mobile": user.mobile,
                    "role": user.role,
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response(
            {"detail": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @swagger_auto_schema(
        methods=['POST'],
        request_body=UserLogoutSerializer,
    )
    @action(detail=False, methods=['POST'])
    def logout(self, request):
        serializer = UserLogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        refresh_token = serializer.validated_data['refresh']
        try:
            RefreshToken.for_user(request.user).blacklist()  # Blacklist the user's token
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Logout failed."}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        methods=['POST'],
        request_body=UserActivationSerializer,
    )
    @action(detail=False, methods=['POST'])
    def activation(self, request):
        serializer = UserActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = User.objects.get(
                email=serializer.validated_data['email'],
                otp=serializer.validated_data['otp'],
            )
            user.is_active = True 
            user.otp = None  # Clear OTP after activation
            user.save()
            
            refresh = RefreshToken.for_user(user)  # Generate tokens after activation
            return Response({
                "details": "Your account has been successfully activated.",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        except User.DoesNotExist:
            return Response(
                {'details': "Email or OTP doesn't match"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from .models import User
from .serializers import UserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.pagination import PageNumberPagination

class NoPagination(PageNumberPagination):
    page_size = 1000000
class UserApprovalViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated] 
    pagination_class=NoPagination # Allow any authenticated user

    @swagger_auto_schema(
        responses={200: UserSerializer(many=True)},
        operation_description="List all users awaiting approval."
    )
    def list(self, request):
        """List all users awaiting approval."""
        users = User.objects.filter(is_approved=False)
        print(users)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    # @swagger_auto_schema(
    #     request_body={'type': 'object', 'properties': {'ids': {'type': 'array', 'items': {'type': 'integer'}}}},
    #     responses={200: 'Users approved.', 400: 'No user IDs provided.', 403: 'Permission denied.'},
    #     operation_description="Approve users by a list of IDs."
    # )
  # Update with your actual User model import

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),
            },
            required=['ids'],
        ),
        responses={
            200: openapi.Response('Users approved.'),
            400: openapi.Response('No user IDs provided.'),
            403: openapi.Response('Permission denied.'),
        },
        operation_description="Approve users by a list of IDs."
    )
    @action(detail=False, methods=['post'])  # Define this as a POST action
    def approve(self, request):
        """Approve users by a list of IDs."""
        ids = request.data.get('ids', [])  # Expecting a list of user IDs
        if not ids:
            return Response({"detail": "No user IDs provided."}, status=status.HTTP_400_BAD_REQUEST)

        approved_users = []
        if request.user.role == 'admin':
            users = User.objects.filter(id__in=ids)
        elif request.user.role == 'receptionist':
            users = User.objects.filter(id__in=ids, role__in=['patient', 'doctor'])
        else:
            raise PermissionDenied("You do not have permission to approve these users.")

        for user in users:
            user.is_approved = True
            user.save()
            approved_users.append(user.email)

        return Response({"detail": f"Users approved: {', '.join(approved_users)}."}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={200: 'User rejected.', 404: 'User not found.', 403: 'Permission denied.'},
        operation_description="Reject a user by ID."
    )
    @action(detail=True, methods=['delete'])  # Define this as a DELETE action
    def reject(self, request, pk=None):
        """Reject a user by ID."""
        user = User.objects.filter(pk=pk).first()
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role in ['admin', 'receptionist']:
            user.delete()  # Alternatively, you could set a rejection field
            return Response({"detail": f"User {user.email} rejected."}, status=status.HTTP_200_OK)

        raise PermissionDenied("You do not have permission to reject this user.")

