from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import (
    Usuario, UsuarioConsumidor, UsuarioEmpresa, Administrador,
    EstatisticaEmpresa, Reclamacao, Arquivo, RespostaReclamacao, Relatorio
)

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('id', 'nome', 'email', 'date_joined')
        read_only_fields = ('id', 'date_joined')

class UsuarioConsumidorSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='usuario.nome', read_only=True)
    email = serializers.EmailField(source='usuario.email', read_only=True)
    date_joined = serializers.DateTimeField(source='usuario.date_joined', read_only=True)

    class Meta:
        model = UsuarioConsumidor
        fields = ('usuario', 'nome', 'email', 'date_joined')
        read_only_fields = ('usuario', 'nome', 'email', 'date_joined')

class UsuarioEmpresaSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='usuario.nome', read_only=True)
    email = serializers.EmailField(source='usuario.email', read_only=True)
    date_joined = serializers.DateTimeField(source='usuario.date_joined', read_only=True)

    class Meta:
        model = UsuarioEmpresa
        fields = (
            'usuario', 'nome', 'email', 'date_joined',
            'cnpj', 'razao_social', 'nome_social', 'descricao'
        )
        read_only_fields = ('usuario', 'nome', 'email', 'date_joined')

    def create(self, validated_data):
        # Hash da senha antes de salvar o usuário base
        validated_data['senha'] = make_password(validated_data.get('senha'))
        return super().create(validated_data)

class AdministradorSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='usuario.nome', read_only=True)
    email = serializers.EmailField(source='usuario.email', read_only=True)
    date_joined = serializers.DateTimeField(source='usuario.date_joined', read_only=True)

    class Meta:
        model = Administrador
        fields = ('usuario', 'nome', 'email', 'date_joined')
        read_only_fields = ('usuario', 'nome', 'email', 'date_joined')

class EstatisticaEmpresaSerializer(serializers.ModelSerializer):
    usuario_empresa_nome = serializers.CharField(source='usuario_empresa.razao_social', read_only=True)
    class Meta:
        model = EstatisticaEmpresa
        fields = (
            'usuario_empresa', 'usuario_empresa_nome', 'total_reclamacoes', 
            'reclamacoes_resolvidas', 'reclamacoes_pendentes', 'media_tempo_resolucao'
        )
        read_only_fields = ('usuario_empresa',)

class ReclamacaoSerializer(serializers.ModelSerializer):
    usuario_consumidor_nome = serializers.CharField(source='usuario_consumidor.nome', read_only=True)
    empresa_razao_social = serializers.CharField(source='empresa.razao_social', read_only=True)
    class Meta:
        model = Reclamacao
        fields = (
            'id', 'usuario_consumidor', 'usuario_consumidor_nome', 'empresa', 
            'empresa_razao_social', 'titulo', 'descricao', 'data_criacao', 'status'
        )
        read_only_fields = ('id', 'data_criacao')

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
        read_only_fields = ('id', 'data_criacao')

class RelatorioSerializer(serializers.ModelSerializer):
    administrador_nome = serializers.CharField(source='administrador.nome', read_only=True)
    class Meta:
        model = Relatorio
        fields = ('id', 'administrador', 'administrador_nome', 'titulo', 'data_geracao', 'conteudo')
        read_only_fields = ('id', 'data_geracao')
