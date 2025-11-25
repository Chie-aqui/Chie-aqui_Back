from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.db import transaction
from .models import (
    Usuario, UsuarioConsumidor, UsuarioEmpresa, Administrador,
    EstatisticaEmpresa, Reclamacao, Arquivo, RespostaReclamacao, Relatorio
)

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        # Added 'phone' field to be readable
        fields = ('id', 'nome', 'email', 'date_joined', 'phone')
        read_only_fields = ('id', 'date_joined', 'phone')
        extra_kwargs = {
            'phone': {'allow_null': True}
        }

class UsuarioConsumidorSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True)
    senha = serializers.CharField(write_only=True, required=True, min_length=8)

    display_id = serializers.IntegerField(source='usuario.id', read_only=True)
    display_nome = serializers.CharField(source='usuario.nome', read_only=True)
    display_email = serializers.EmailField(source='usuario.email', read_only=True)
    date_joined = serializers.DateTimeField(source='usuario.date_joined', read_only=True)
    # Sourcing phone from the related Usuario object
    phone = serializers.CharField(source='usuario.phone', read_only=True, allow_null=True)

    # SerializerMethodFields for complaint statistics
    totalComplaints = serializers.SerializerMethodField()
    resolved = serializers.SerializerMethodField()
    helpfulVotes = serializers.SerializerMethodField()
    profileViews = serializers.SerializerMethodField()

    class Meta:
        model = UsuarioConsumidor
        fields = (
            'display_id', 'nome', 'email', 'senha',
            'display_nome', 'display_email', 'date_joined',
            'phone', # Added phone
            'totalComplaints', 'resolved', 'helpfulVotes', 'profileViews' # Added stats fields
        )
        read_only_fields = (
            'display_id', 'date_joined', 'display_nome', 'display_email',
            'phone', # Added phone to read_only_fields
            'totalComplaints', 'resolved', 'helpfulVotes', 'profileViews' # Added stats fields to read_only_fields
        )
        extra_kwargs = {
            'usuario': {'read_only': True},
            # Ensure sourced fields also respect nullability if defined on the source model
            'phone': {'allow_null': True}
        }

    def get_totalComplaints(self, obj):
        # Count complaints associated with this consumer
        return Reclamacao.objects.filter(usuario_consumidor=obj).count()

    def get_resolved(self, obj):
        # Count resolved complaints for this consumer
        return Reclamacao.objects.filter(usuario_consumidor=obj, status='Resolvida').count()

    def get_helpfulVotes(self, obj):
        # This would require logic to sum up votes, assuming a Vote model exists or votes are stored elsewhere.
        # For now, returning 0 as a placeholder.
        return 0 # Placeholder: implement vote counting logic if available

    def get_profileViews(self, obj):
        # This would require a mechanism to track profile views (e.g., a separate model or counter).
        # For now, returning 0 as a placeholder.
        return 0 # Placeholder: implement profile view tracking logic if available

    @transaction.atomic
    def create(self, validated_data):
        nome = validated_data.pop('nome')
        email = validated_data.pop('email')
        senha = validated_data.pop('senha')
        # Ensure phone is passed to create_user if it exists in validated_data
        # For now, assuming it is handled by Usuario.objects.create_user if provided during signup
        usuario = Usuario.objects.create_user(email=email, password=senha, nome=nome)
        usuario_consumidor = UsuarioConsumidor.objects.create(usuario=usuario, **validated_data)
        return usuario_consumidor

class UsuarioEmpresaSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True)
    senha = serializers.CharField(write_only=True, required=True, min_length=8)

    display_id = serializers.IntegerField(source='usuario.id', read_only=True)
    display_nome = serializers.CharField(source='usuario.nome', read_only=True)
    display_email = serializers.EmailField(source='usuario.email', read_only=True)
    date_joined = serializers.DateTimeField(source='usuario.date_joined', read_only=True)

    class Meta:
        model = UsuarioEmpresa
        fields = (
            'display_id', 'nome', 'email', 'senha',
            'cnpj', 'razao_social', 'nome_social', 'descricao',
            'display_nome', 'display_email', 'date_joined'
        )
        read_only_fields = ('display_id', 'date_joined', 'display_nome', 'display_email')
        extra_kwargs = {
            'usuario': {'read_only': True}
        }

    @transaction.atomic
    def create(self, validated_data):
        nome = validated_data.pop('nome')
        email = validated_data.pop('email')
        senha = validated_data.pop('senha')
        usuario = Usuario.objects.create_user(email=email, password=senha, nome=nome)
        usuario_empresa = UsuarioEmpresa.objects.create(usuario=usuario, **validated_data)
        # Create statistics for the new company
        EstatisticaEmpresa.objects.create(usuario_empresa=usuario_empresa)
        return usuario_empresa

class EstatisticaEmpresaSerializer(serializers.ModelSerializer):
    usuario_empresa_nome = serializers.CharField(source='usuario_empresa.razao_social', read_only=True)
    class Meta:
        model = EstatisticaEmpresa
        fields = (
            'usuario_empresa', 'usuario_empresa_nome', 'total_reclamacoes', 
            'reclamacoes_resolvidas', 'reclamacoes_pendentes', 'media_tempo_resolucao'
        )
        read_only_fields = ('usuario_empresa',)

class UsuarioEmpresaProfileSerializer(UsuarioEmpresaSerializer):
    estatisticas = serializers.SerializerMethodField()

    class Meta(UsuarioEmpresaSerializer.Meta):
        fields = [field for field in UsuarioEmpresaSerializer.Meta.fields if field != 'senha'] + ['estatisticas']
        read_only_fields = [field for field in UsuarioEmpresaSerializer.Meta.read_only_fields]

    def get_estatisticas(self, obj):
        stats, created = EstatisticaEmpresa.objects.get_or_create(usuario_empresa=obj)
        serializer = EstatisticaEmpresaSerializer(stats)
        return serializer.data

class AdministradorSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='usuario.nome', read_only=True)
    email = serializers.EmailField(source='usuario.email', read_only=True)
    date_joined = serializers.DateTimeField(source='usuario.date_joined', read_only=True)

    class Meta:
        model = Administrador
        fields = ('usuario', 'nome', 'email', 'date_joined')
        read_only_fields = ('usuario', 'nome', 'email', 'date_joined')

class ReclamacaoSerializer(serializers.ModelSerializer):
    usuario_consumidor_nome = serializers.CharField(source='usuario_consumidor.nome', read_only=True)
    empresa_razao_social = serializers.CharField(source='empresa.razao_social', read_only=True)
    empresa = serializers.PrimaryKeyRelatedField(queryset=UsuarioEmpresa.objects.all())

    class Meta:
        model = Reclamacao
        fields = (
            'id', 'usuario_consumidor', 'usuario_consumidor_nome', 'empresa', 
            'empresa_razao_social', 'titulo', 'descricao', 'data_criacao', 'status'
        )
        read_only_fields = ('id', 'data_criacao', 'usuario_consumidor', 'status')

class ArquivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arquivo
        fields = ('id', 'reclamacao', 'arquivo', 'nome_arquivo', 'tipo_arquivo', 'data_upload')
        read_only_fields = ('id', 'data_upload')

class RespostaReclamacaoSerializer(serializers.ModelSerializer):
    reclamacao_titulo = serializers.CharField(source='reclamacao.titulo', read_only=True)
    empresa_razao_social = serializers.CharField(source='empresa.razao_social', read_only=True)
    class Meta:
        model = RespostaReclamacao
        fields = (
            'id', 'reclamacao', 'reclamacao_titulo', 'empresa', 'empresa_razao_social', 
            'descricao', 'data_criacao', 'status_resolucao'
        )
        read_only_fields = ('id', 'data_criacao', 'reclamacao', 'empresa')

class RelatorioSerializer(serializers.ModelSerializer):
    administrador_nome = serializers.CharField(source='administrador.nome', read_only=True)
    class Meta:
        model = Relatorio
        fields = ('id', 'administrador', 'administrador_nome', 'titulo', 'data_geracao', 'conteudo')
        read_only_fields = ('id', 'data_geracao')