# urls.py (do app)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'empresas'

# Configuração do ViewSet (CRUD)
router = DefaultRouter()
router.register(r'empresas', views.EmpresaViewSet, basename='empresa')

urlpatterns = [
    # Cadastro de empresa (endpoint personalizado)
    path('cadastro/', views.EmpresaCadastroView.as_view(), name='empresa-cadastro'),
    
    # Login/Logout (endpoints personalizados)
    path('login/', views.empresa_login, name='empresa-login'),
    path('logout/', views.empresa_logout, name='empresa-logout'),
    
    # Perfil da empresa (endpoints personalizados)
    path('perfil/', views.EmpresaPerfilView.as_view(), name='empresa-perfil'),
    
    # Inclui as URLs do ViewSet (listar empresas, etc.)
    path('', include(router.urls)),
]
