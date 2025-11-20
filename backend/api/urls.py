from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'usuarios', views.UsuarioViewSet, basename='usuario')
router.register(r'consumidores', views.UsuarioConsumidorViewSet, basename='consumidor')
router.register(r'empresas', views.UsuarioEmpresaViewSet, basename='empresa')
router.register(r'administradores', views.AdministradorViewSet, basename='administrador')
router.register(r'reclamacoes', views.ReclamacaoViewSet, basename='reclamacao')
router.register(r'respostas_reclamacao', views.RespostaReclamacaoViewSet, basename='resposta_reclamacao')

urlpatterns = [
    path('empresas/cadastro/', views.UsuarioEmpresaCadastroView.as_view(), name='empresa-cadastro'),
    path('empresas/login/', views.usuario_empresa_login, name='empresa-login'),
    path('empresas/logout/', views.usuario_empresa_logout, name='empresa-logout'),
    path('empresas/perfil/', views.UsuarioEmpresaPerfilView.as_view(), name='empresa-perfil'),
    path('empresas/lista/', views.UsuarioEmpresaListView.as_view(), name='empresa-list'),

    path('consumidores/login/', views.usuario_consumidor_login, name='consumidor-login'),
    path('consumidores/logout/', views.usuario_consumidor_logout, name='consumidor-logout'),
    path('consumidores/perfil/', views.UsuarioConsumidorPerfilView.as_view(), name='consumidor-perfil'),

    path('', views.api_root),
    path('', include(router.urls)),
]