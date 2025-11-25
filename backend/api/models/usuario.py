# app_usuarios/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Necessário para usar o campo 'email' como USERNAME_FIELD
class UsuarioManager(BaseUserManager):
    """
    Gerenciador de usuários personalizado para usar email como identificador.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email deve ser definido')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractUser):
    # O AbstractUser já define username, first_name, last_name, email, is_staff, etc.
    username = None # Remove o campo 'username' padrão de AbstractUser
    
    nome = models.CharField(max_length=255, blank=True, null=True)
    # Sobrescreve o email de AbstractUser para ser único e null=False (padrão)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True) 

    # Configurações obrigatórias para um modelo de usuário personalizado
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome'] 

    objects = UsuarioManager() # Usa o gerenciador de usuários personalizado

    def __str__(self):
        return self.email



# from django.db import models
# from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.models import AbstractUser, BaseUserManager

# class Usuario(AbstractUser):
#     # O campo 'email' já é único e pode ser usado como USERNAME_FIELD em AbstractUser
#     # Mas se quisermos um 'nome' separado para exibição, podemos adicioná-lo
#     nome = models.CharField(max_length=255, blank=True, null=True)
#     email = models.EmailField(unique=True) # Sobrescreve o email de AbstractUser para ser único

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['nome'] # Campo requerido durante a criação de superusuário

#     def __str__(self):
#         return self.email

# # Os modelos abaixo agora serão perfis que se relacionam com o modelo Usuario
# # usando OneToOneField, em vez de herança de modelo multi-tabela.

# class UsuarioConsumidor(models.Model):
#     usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

#     def __str__(self):
#         return self.usuario.nome or self.usuario.email

# class UsuarioEmpresa(models.Model):
#     usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
#     cnpj = models.CharField(max_length=18, unique=True)
#     razao_social = models.CharField(max_length=255)
#     nome_social = models.CharField(max_length=255, blank=True, null=True)
#     descricao = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return self.razao_social

# class Administrador(models.Model):
#     usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

#     def __str__(self):
#         return self.usuario.nome or self.usuario.email