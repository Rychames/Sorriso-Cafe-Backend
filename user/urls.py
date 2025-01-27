from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user import views

# Criando o roteador e registrando os ViewSets
router = DefaultRouter()

router.register(r'register', views.UserRegisterViewSet, basename='register')
router.register(r'login', views.UserLoginViewSet, basename='login')

app_name = "user"  

urlpatterns = [
    path('', include(router.urls)), 
    path('profile/', views.UserAPI.as_view(), name="profile"),
    #path('profile/image/', views.ProfileImageView.as_view(), name="profile-image"),
]
