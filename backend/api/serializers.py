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
        read_only_fields = ('id', 'date_joined',)
        extra_kwargs = {
            'phone': {'allow_null': True}
        }

class UsuarioConsumidorSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source="usuario.nome", required=False)
    email = serializers.EmailField(source="usuario.email", required=False)
    phone = serializers.CharField(source="usuario.phone", required=False, allow_null=True, allow_blank=True)
    senha = serializers.CharField(write_only=True, required=False, min_length=8)
    
    user_complaints = serializers.SerializerMethodField()

    display_id = serializers.IntegerField(source='usuario.id', read_only=True)
    display_nome = serializers.CharField(source='usuario.nome', read_only=True)
    display_email = serializers.EmailField(source='usuario.email', read_only=True)
    date_joined = serializers.DateTimeField(source='usuario.date_joined', read_only=True)

    totalComplaints = serializers.SerializerMethodField()
    resolved = serializers.SerializerMethodField()
    helpfulVotes = serializers.SerializerMethodField()
    profileViews = serializers.SerializerMethodField()

    class Meta:
        model = UsuarioConsumidor
        fields = (
            'display_id', 'nome', 'email', 'senha', 'phone',
            'display_nome', 'display_email', 'date_joined',
            'totalComplaints', 'resolved', 'helpfulVotes', 'profileViews',
            'user_complaints' # Adicionado o campo de reclamações
        )
        read_only_fields = (
            'display_id', 'date_joined', 'display_nome', 'display_email',
            'totalComplaints', 'resolved', 'helpfulVotes', 'profileViews'
        )
        
    def get_totalComplaints(self, obj):
        return Reclamacao.objects.filter(usuario_consumidor=obj).count()

    def get_resolved(self, obj):
        return Reclamacao.objects.filter(usuario_consumidor=obj, status='ENCERRADA').count()

    def get_helpfulVotes(self, obj):
        return 0

    def get_profileViews(self, obj):
        return 0

    def get_user_complaints(self, obj):
        # Retorna as reclamações do usuário consumidor
        complaints = Reclamacao.objects.filter(usuario_consumidor=obj).order_by('-data_criacao')
        return ReclamacaoSerializer(complaints, many=True).data

    @transaction.atomic
    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario', {})
        senha = validated_data.pop('senha')
        
        nome = usuario_data.get('nome')
        email = usuario_data.get('email')
        phone = usuario_data.get('phone')

        usuario = Usuario.objects.create_user(
            email=email, password=senha, nome=nome, phone=phone
        )
        usuario_consumidor = UsuarioConsumidor.objects.create(usuario=usuario, **validated_data)
        return usuario_consumidor

    @transaction.atomic
    def update(self, instance, validated_data):
        usuario = instance.usuario

        # O DRF já trata campos com 'source' no nível superior de validated_data
        print(f"[DEBUG] UsuarioConsumidorSerializer - validated_data: {validated_data}")
        usuario_data = validated_data.get('usuario', {})
        nome = usuario_data.get("nome")
        email = usuario_data.get("email")
        phone = usuario_data.get("phone")
        print(f"[DEBUG] UsuarioConsumidorSerializer - nome: {nome}, email: {email}, phone: {phone}")

        senha = validated_data.pop("senha", None)
        
        # Atualiza apenas campos enviados
        if nome is not None:
            usuario.nome = nome

        if email is not None:
            usuario.email = email

        if phone is not None:
            usuario.phone = phone

        if senha is not None:
            usuario.set_password(senha)

        usuario.save()

        # Atualiza outros dados do model do consumidor (se houver)
        # return super().update(instance, validated_data)
        # Como não há campos diretos no UsuarioConsumidor sendo atualizados aqui,
        # podemos simplesmente retornar a instância.
        return instance

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

class ArquivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arquivo
        fields = ('id', 'reclamacao', 'arquivo', 'nome_arquivo', 'tipo_arquivo', 'data_upload')
        read_only_fields = ('id', 'data_upload')

class ReclamacaoSerializer(serializers.ModelSerializer):
    usuario_consumidor_nome = serializers.SerializerMethodField()
    empresa_razao_social = serializers.CharField(source='empresa.razao_social', read_only=True)
    empresa = serializers.PrimaryKeyRelatedField(queryset=UsuarioEmpresa.objects.all())
    resposta = serializers.SerializerMethodField()
    arquivos_upload = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False, source='arquivos'
    )
    arquivos = ArquivoSerializer(many=True, read_only=True)

    class Meta:
        model = Reclamacao
        fields = (
            'id', 'usuario_consumidor', 'usuario_consumidor_nome', 'empresa', 
            'empresa_razao_social', 'titulo', 'descricao', 'data_criacao', 'status', 'resposta',
            'arquivos_upload', 'arquivos'
        )
        read_only_fields = ('id', 'data_criacao', 'usuario_consumidor', 'arquivos')

    def get_usuario_consumidor_nome(self, obj):
        if obj.usuario_consumidor and obj.usuario_consumidor.usuario:
            return obj.usuario_consumidor.usuario.nome or obj.usuario_consumidor.usuario.email
        return "Consumidor Desconhecido"

    def get_resposta(self, obj):
        # Modificado para pegar a última resposta, se houver múltiplas
        resposta = RespostaReclamacao.objects.filter(reclamacao=obj).order_by('-data_criacao').first()
        if resposta:
            return RespostaReclamacaoSerializer(resposta).data
        return None

    def create(self, validated_data):
        arquivos_data = validated_data.pop('arquivos', [])
        reclamacao = Reclamacao.objects.create(**validated_data)
        for arquivo_data in arquivos_data:
            Arquivo.objects.create(
                reclamacao=reclamacao,
                arquivo=arquivo_data,
                nome_arquivo=arquivo_data.name,
                tipo_arquivo=arquivo_data.content_type
            )
        return reclamacao

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