from django.shortcuts import render

from rest_framework import viewsets
from .models import Empresa
from .serializers import EmpresaSerializer

# views.py
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Usuario, Empresa
from .serializers import EmpresaCadastroSerializer, EmpresaSerializer

class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer

class EmpresaCadastroView(generics.CreateAPIView):
    """
    View para cadastro de empresas
    POST /api/empresas/cadastro/
    """
    serializer_class = EmpresaCadastroSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            empresa = serializer.save()
            
            # Criar token de autenticação
            token, created = Token.objects.get_or_create(user=empresa.usuario)
            
            response_data = {
                'message': 'Empresa cadastrada com sucesso!',
                'empresa': EmpresaSerializer(empresa).data,
                'token': token.key
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmpresaPerfilView(generics.RetrieveUpdateAPIView):
    """
    View para visualizar e editar perfil da empresa
    GET/PUT /api/empresas/perfil/
    """
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        try:
            return self.request.user.perfil_empresa
        except Empresa.DoesNotExist:
            return Response(
                {'error': 'Usuário não é uma empresa'}, 
                status=status.HTTP_403_FORBIDDEN
            )

@api_view(['POST'])
@permission_classes([AllowAny])
def empresa_login(request):
    """
    Endpoint para login de empresas
    POST /api/empresas/login/
    """
    email = request.data.get('email')
    senha = request.data.get('senha')
    
    if not email or not senha:
        return Response(
            {'error': 'Email e senha são obrigatórios'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=email, password=senha)
    
    if user and user.tipo_usuario == 'empresa':
        token, created = Token.objects.get_or_create(user=user)
        empresa = user.perfil_empresa
        
        return Response({
            'message': 'Login realizado com sucesso',
            'token': token.key,
            'empresa': EmpresaSerializer(empresa).data
        })
    
    return Response(
        {'error': 'Credenciais inválidas ou usuário não é uma empresa'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def empresa_logout(request):
    """
    Endpoint para logout de empresas
    POST /api/empresas/logout/
    """
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logout realizado com sucesso'})
    except:
        return Response({'error': 'Erro ao realizar logout'}, 
                       status=status.HTTP_400_BAD_REQUEST)

class EmpresaListView(generics.ListAPIView):
    """
    View para listar empresas (apenas para administradores)
    GET /api/empresas/
    """
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.tipo_usuario == 'administrador':
            return Empresa.objects.all()
        return Empresa.objects.none()