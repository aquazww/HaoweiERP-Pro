from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomTokenObtainPairView, CustomTokenRefreshView, UserInfoView, LogoutView, UserViewSet, LogViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'logs', LogViewSet)

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', UserInfoView.as_view(), name='user_info'),
    path('', include(router.urls)),
]
