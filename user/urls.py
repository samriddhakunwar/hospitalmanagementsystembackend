from rest_framework.routers import SimpleRouter
from .views import UserViewSet, UserApprovalViewSet

router = SimpleRouter()

# Register the UserViewSet for user registration
router.register("users", UserViewSet, basename='user')

# Register the UserApprovalViewSet for user approval actions
router.register("users/approval", UserApprovalViewSet, basename='user-approval')

urlpatterns = router.urls
