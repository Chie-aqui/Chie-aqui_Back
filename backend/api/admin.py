from django.contrib import admin

# Register your models here.
# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Empresa, Consumidor, Administrador

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """Configuração do admin para o modelo Usuario"""
    list_display = ('username', 'nome', 'email', 'tipo_usuario', 'ativo', 'data_cadastro')
    list_filter = ('tipo_usuario', 'ativo', 'data_cadastro')
    search_fields = ('username', 'nome', 'email')
    ordering = ('-data_cadastro',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('nome', 'telefone', 'tipo_usuario', 'ativo')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informações Adicionais', {
            'fields': ('nome', 'email', 'telefone', 'tipo_usuario')
        }),
    )

class EmpresaInline(admin.StackedInline):
    """Inline para editar dados da empresa junto com o usuário"""
    model = Empresa
    can_delete = False
    verbose_name_plural = 'Dados da Empresa'

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    """Configuração do admin para o modelo Empresa"""
    list_display = ('nome_fantasia', 'razao_social', 'cnpj', 'get_email', 'get_data_cadastro')
    list_filter = ('usuario__data_cadastro',)
    search_fields = ('nome_fantasia', 'razao_social', 'cnpj', 'usuario__nome', 'usuario__email')
    ordering = ('-usuario__data_cadastro',)
    
    def get_email(self, obj):
        return obj.usuario.email
    get_email.short_description = 'Email'
    
    def get_data_cadastro(self, obj):
        return obj.usuario.data_cadastro
    get_data_cadastro.short_description = 'Data de Cadastro'

@admin.register(Consumidor)
class ConsumidorAdmin(admin.ModelAdmin):
    """Configuração do admin para o modelo Consumidor"""
    list_display = ('get_nome', 'get_email', 'get_data_cadastro')
    search_fields = ('usuario__nome', 'usuario__email')
    
    def get_nome(self, obj):
        return obj.usuario.nome
    get_nome.short_description = 'Nome'
    
    def get_email(self, obj):
        return obj.usuario.email
    get_email.short_description = 'Email'
    
    def get_data_cadastro(self, obj):
        return obj.usuario.data_cadastro
    get_data_cadastro.short_description = 'Data de Cadastro'

@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    """Configuração do admin para o modelo Administrador"""
    list_display = ('get_nome', 'get_email', 'get_data_cadastro')
    search_fields = ('usuario__nome', 'usuario__email')
    
    def get_nome(self, obj):
        return obj.usuario.nome
    get_nome.short_description = 'Nome'
    
    def get_email(self, obj):
        return obj.usuario.email
    get_email.short_description = 'Email'
    
    def get_data_cadastro(self, obj):
        return obj.usuario.data_cadastro
    get_data_cadastro.short_description = 'Data de Cadastro'