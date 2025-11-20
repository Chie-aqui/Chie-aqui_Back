from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from .models import (
    Usuario, UsuarioConsumidor, UsuarioEmpresa, Administrador,
    Reclamacao, RespostaReclamacao
)
from .serializers import (
    UsuarioSerializer, UsuarioConsumidorSerializer, UsuarioEmpresaSerializer,
    AdministradorSerializer, ReclamacaoSerializer, RespostaReclamacaoSerializer
)

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'usuarios': reverse('api:usuario-list', request=request, format=format),
        'consumidores': reverse('api:consumidor-list', request=request, format=format),
        'consumidor_login': reverse('api:consumidor-login', request=request, format=format),
        'consumidor_logout': reverse('api:consumidor-logout', request=request, format=format),
        'consumidor_perfil': reverse('api:consumidor-perfil', request=request, format=format),
        'empresas': reverse('api:empresa-list', request=request, format=format),
        'empresa_cadastro': reverse('api:empresa-cadastro', request=request, format=format),
        'empresa_login': reverse('api:empresa-login', request=request, format=format),
        'empresa_logout': reverse('api:empresa-logout', request=request, format=format),
        'empresa_perfil': reverse('api:empresa-perfil', request=request, format=format),
        'empresa_lista': reverse('api:empresa-list', request=request, format=format),
        'administradores': reverse('api:administrador-list', request=request, format=format),
        'reclamacoes': reverse('api:reclamacao-list', request=request, format=format),
        'respostas_reclamacao': reverse('api:resposta_reclamacao-list', request=request, format=format),
    })

# Views para Usuario
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

# Views para UsuarioConsumidor
class UsuarioConsumidorViewSet(viewsets.ModelViewSet):
    serializer_class = UsuarioConsumidorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = UsuarioConsumidor.objects.all()
        user = self.request.user

        # Apenas administradores podem buscar
        if hasattr(user, 'administrador') or user.is_superuser:
            email = self.request.query_params.get('email', None)
            if email is not None:
                queryset = queryset.filter(usuario__email__icontains=email)
        return queryset

class UsuarioConsumidorPerfilView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UsuarioConsumidorSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        try:
            return UsuarioConsumidor.objects.get(pk=self.request.user.pk)
        except UsuarioConsumidor.DoesNotExist:
            return Response(
                {'error': 'Usuário não é um consumidor'}, 
                status=status.HTTP_403_FORBIDDEN
            )
    
    def perform_destroy(self, instance):
        # O usuário associado também será excluído devido ao on_delete=models.CASCADE
        instance.usuario.delete()

# Views para UsuarioEmpresa
class UsuarioEmpresaViewSet(viewsets.ModelViewSet):
    serializer_class = UsuarioEmpresaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = UsuarioEmpresa.objects.all()
        user = self.request.user

        if hasattr(user, 'administrador') or user.is_superuser:
            cnpj = self.request.query_params.get('cnpj', None)
            if cnpj is not None:
                queryset = queryset.filter(cnpj__icontains=cnpj)
        return queryset

class UsuarioEmpresaCadastroView(generics.CreateAPIView):
    serializer_class = UsuarioEmpresaSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            usuario_empresa = serializer.save()
            
            token, created = Token.objects.get_or_create(user=usuario_empresa)
            
            response_data = {
                'message': 'Empresa cadastrada com sucesso!',
                'usuario_empresa': UsuarioEmpresaSerializer(usuario_empresa).data,
                'token': token.key
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UsuarioEmpresaPerfilView(generics.RetrieveUpdateAPIView):
    serializer_class = UsuarioEmpresaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        try:
            return UsuarioEmpresa.objects.get(pk=self.request.user.pk)
        except UsuarioEmpresa.DoesNotExist:
            return Response(
                {'error': 'Usuário não é uma empresa'}, 
                status=status.HTTP_403_FORBIDDEN
            )

@api_view(['POST'])
@permission_classes([AllowAny])
def usuario_empresa_login(request):
    email = request.data.get('email')
    senha = request.data.get('senha')
    
    if not email or not senha:
        return Response(
            {'error': 'Email e senha são obrigatórios'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=email, password=senha)
    
    if user is not None:
        if hasattr(user, 'usuarioempresa'):
            token, created = Token.objects.get_or_create(user=user)
            usuario_empresa = user.usuarioempresa
            
            return Response({
                'message': 'Login realizado com sucesso',
                'token': token.key,
                'usuario_empresa': UsuarioEmpresaSerializer(usuario_empresa).data
            })
        else:
            return Response(
                {'error': 'Usuário não é uma empresa'}, 
                status=status.HTTP_403_FORBIDDEN
            )
    
    return Response(
        {'error': 'Credenciais inválidas'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def usuario_empresa_logout(request):
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logout realizado com sucesso'})
    except:
        return Response({'error': 'Erro ao realizar logout'}, 
                       status=status.HTTP_400_BAD_REQUEST)

class UsuarioEmpresaListView(generics.ListAPIView):
    serializer_class = UsuarioEmpresaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'administrador'):
            return UsuarioEmpresa.objects.all()
        return UsuarioEmpresa.objects.none()

# Views para Administrador
class AdministradorViewSet(viewsets.ModelViewSet):
    queryset = Administrador.objects.all()
    serializer_class = AdministradorSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def usuario_consumidor_login(request):
    email = request.data.get('email')
    senha = request.data.get('senha')
    
    if not email or not senha:
        return Response(
            {'error': 'Email e senha são obrigatórios'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=email, password=senha)
    
    if user is not None:
        if hasattr(user, 'usuarioconsumidor'):
            token, created = Token.objects.get_or_create(user=user)
            usuario_consumidor = user.usuarioconsumidor
            
            return Response({
                'message': 'Login realizado com sucesso',
                'token': token.key,
                'usuario_consumidor': UsuarioConsumidorSerializer(usuario_consumidor).data
            })
        else:
            return Response(
                {'error': 'Usuário não é um consumidor'}, 
                status=status.HTTP_403_FORBIDDEN
            )
    
    return Response(
        {'error': 'Credenciais inválidas'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def usuario_consumidor_logout(request):
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logout realizado com sucesso'})
    except:
        return Response({'error': 'Erro ao realizar logout'}, 
                       status=status.HTTP_400_BAD_REQUEST)

# Views para Reclamacao
class ReclamacaoViewSet(viewsets.ModelViewSet):
    serializer_class = ReclamacaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Reclamacao.objects.all()

        if hasattr(user, 'usuarioconsumidor'):
            queryset = queryset.filter(usuario_consumidor=user.usuarioconsumidor)
        elif hasattr(user, 'usuarioempresa'):
            queryset = queryset.filter(empresa=user.usuarioempresa)
        elif not (hasattr(user, 'administrador') or user.is_superuser):
             return Reclamacao.objects.none()

        # Filtros para todos os usuários autorizados
        status_filtro = self.request.query_params.get('status', None)
        if status_filtro is not None:
            queryset = queryset.filter(status=status_filtro)
        
        empresa_id = self.request.query_params.get('empresa_id', None)
        if empresa_id is not None:
            queryset = queryset.filter(empresa__usuario_id=empresa_id)
            
        return queryset

# Views para RespostaReclamacao
class RespostaReclamacaoViewSet(viewsets.ModelViewSet):
    queryset = RespostaReclamacao.objects.all()
    serializer_class = RespostaReclamacaoSerializer
