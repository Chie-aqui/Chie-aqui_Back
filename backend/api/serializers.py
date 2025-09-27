# serializers.py
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Usuario, Empresa

class EmpresaCadastroSerializer(serializers.ModelSerializer):
    """
    Serializer para cadastro de empresas
    Inclui dados do usuário e dados específicos da empresa
    """
    # Campos do usuário
    nome = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    senha = serializers.CharField(write_only=True, min_length=8)
    telefone = serializers.CharField(max_length=15, required=False)
    
    # Campos específicos da empresa
    cnpj = serializers.CharField(max_length=18)
    nome_fantasia = serializers.CharField(max_length=150)
    razao_social = serializers.CharField(max_length=150)
    descricao = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Empresa
        fields = ['nome', 'email', 'senha', 'telefone', 'cnpj', 
                 'nome_fantasia', 'razao_social', 'descricao']
    
    def validate_email(self, value):
        """Valida se o email já não está sendo usado"""
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        return value
    
    def validate_cnpj(self, value):
        """Valida formato do CNPJ"""
        import re
        if not re.match(r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$', value):
            raise serializers.ValidationError("CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX")
        
        if Empresa.objects.filter(cnpj=value).exists():
            raise serializers.ValidationError("Este CNPJ já está cadastrado.")
        return value
    
    def create(self, validated_data):
        """Cria usuário e perfil de empresa"""
        # Extrair dados do usuário
        dados_usuario = {
            'username': validated_data['email'],
            'nome': validated_data['nome'],
            'email': validated_data['email'],
            'password': make_password(validated_data['senha']),
            'telefone': validated_data.get('telefone', ''),
            'tipo_usuario': 'empresa',
        }
        
        # Criar usuário
        usuario = Usuario.objects.create(**dados_usuario)
        
        # Extrair dados da empresa
        dados_empresa = {
            'usuario': usuario,
            'cnpj': validated_data['cnpj'],
            'nome_fantasia': validated_data['nome_fantasia'],
            'razao_social': validated_data['razao_social'],
            'descricao': validated_data.get('descricao', ''),
        }
        
        # Criar empresa
        empresa = Empresa.objects.create(**dados_empresa)
        
        return empresa

class EmpresaSerializer(serializers.ModelSerializer):
    """Serializer para visualização de dados da empresa"""
    nome = serializers.CharField(source='usuario.nome', read_only=True)
    email = serializers.EmailField(source='usuario.email', read_only=True)
    telefone = serializers.CharField(source='usuario.telefone', read_only=True)
    data_cadastro = serializers.DateTimeField(source='usuario.date_joined', read_only=True)
    
    class Meta:
        model = Empresa
        fields = ['id', 'nome', 'email', 'telefone', 'data_cadastro',
                 'cnpj', 'nome_fantasia', 'razao_social', 'descricao']
        read_only_fields = ['id', 'data_cadastro']