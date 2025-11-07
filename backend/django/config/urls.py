"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# ViewSet imports
from users.views import AuthViewSet, UserViewSet
from characters.views import CharacterViewSet
from conversations.views import ConversationViewSet, MessageViewSet
from media.views import MediaAssetViewSet, GenerationJobViewSet

# Router 설정
router = DefaultRouter()

# 인증 & 사용자
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='users')

# 캐릭터
router.register(r'characters', CharacterViewSet, basename='character')

# 대화 & 메시지
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# 미디어 & 생성 작업
router.register(r'media', MediaAssetViewSet, basename='media')
router.register(r'generation-jobs', GenerationJobViewSet, basename='generation-job')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
]
