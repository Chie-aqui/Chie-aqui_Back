# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from datetime import datetime

class Usuario(AbstractUser):
    """
    Modelo base para todos os usuários do sistema.
    Herda de AbstractUser para usar o sistema de autenticação do Django.
    """
    nome = models.CharField(max_length=150)
    telefone = models.CharField(
        max_length=15, 
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        blank=True
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    # Campos para identificar o tipo de usuário
    TIPO_USUARIO_CHOICES = [
        ('consumidor', 'Consumidor'),
        ('empresa', 'Empresa'),
        ('administrador', 'Administrador'),
    ]
    tipo_usuario = models.CharField(max_length=15, choices=TIPO_USUARIO_CHOICES)
    
    # Adicionando 'related_name' para evitar conflito com o 'AbstractUser'
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_usuario_set',  # Evita o conflito de nomes
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_usuario_permissions',  # Evita o conflito de nomes
        blank=True
    )

    def __str__(self):
        return self.nome or self.username

class Empresa(models.Model):
    """
    Perfil específico para empresas
    Relacionado ao Usuario através de OneToOneField
    """
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_empresa', null=True, blank=True)
    cnpj = models.CharField(
        max_length=18, 
        unique=True,
        null=True,  # Permite valores nulos
        blank=True,
        validators=[RegexValidator(r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$')]
    )
    nome_fantasia = models.CharField(max_length=150,default='Nome Fantasia Não Informado')
    razao_social = models.CharField(max_length=150,default='Razao social Não Informado')
    descricao = models.TextField(blank=True,default='Descricao Não Informado')
    
    def __str__(self):
        return self.nome_fantasia
    
    def visualizar_reclamacoes(self):
        """Método para visualizar reclamações da empresa"""
        return self.reclamacoes.all()
    
    def responder_reclamacao(self, reclamacao, resposta):
        """Método para responder uma reclamação"""
        # Implementar lógica de resposta
        pass
    
    def visualizar_estatisticas(self):
        """Método para visualizar estatísticas da empresa"""
        # Implementar lógica de estatísticas
        pass

class Consumidor(models.Model):
    """
    Perfil específico para consumidores
    Relacionado ao Usuario através de OneToOneField
    """
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_consumidor')
    
    def __str__(self):
        return f"Consumidor: {self.usuario.nome}"
    
    def registrar_reclamacao(self, empresa, titulo, descricao):
        """Método para registrar uma reclamação"""
        # Implementar lógica de registro de reclamação
        pass
    
    def visualizar_reclamacoes(self):
        """Método para visualizar reclamações do consumidor"""
        return self.reclamacoes.all()

class Administrador(models.Model):
    """
    Perfil específico para administradores
    Relacionado ao Usuario através de OneToOneField
    """
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_administrador')
    
    def __str__(self):
        return f"Administrador: {self.usuario.nome}"
    
    def visualizar_usuarios(self):
        """Método para visualizar todos os usuários"""
        return Usuario.objects.all()
    
    def visualizar_empresas(self):
        """Método para visualizar todas as empresas"""
        return Empresa.objects.all()
    
    def remover_usuario(self, usuario):
        """Método para remover um usuário"""
        usuario.delete()