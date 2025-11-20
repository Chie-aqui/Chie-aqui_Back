from django.contrib import admin
from .models import (
    Usuario, UsuarioConsumidor, UsuarioEmpresa, Administrador,
    EstatisticaEmpresa, Reclamacao, Arquivo, RespostaReclamacao, Relatorio
)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'nome', 'date_joined') # AbstractUser usa 'date_joined'
    list_filter = ('date_joined', 'is_staff', 'is_active')
    search_fields = ('email', 'nome')
    ordering = ('-date_joined',)

@admin.register(UsuarioConsumidor)
class UsuarioConsumidorAdmin(admin.ModelAdmin):
    list_display = ('usuario_email', 'usuario_nome', 'usuario_data_cadastro')
    search_fields = ('usuario__email', 'usuario__nome')

    def usuario_email(self, obj):
        return obj.usuario.email
    usuario_email.short_description = 'Email'

    def usuario_nome(self, obj):
        return obj.usuario.nome
    usuario_nome.short_description = 'Nome'

    def usuario_data_cadastro(self, obj):
        return obj.usuario.date_joined
    usuario_data_cadastro.short_description = 'Data de Cadastro'

@admin.register(UsuarioEmpresa)
class UsuarioEmpresaAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'cnpj', 'usuario_email', 'usuario_nome', 'usuario_data_cadastro')
    list_filter = ('usuario__date_joined',)
    search_fields = ('razao_social', 'cnpj', 'usuario__email', 'usuario__nome')
    ordering = ('-usuario__date_joined',)

    def usuario_email(self, obj):
        return obj.usuario.email
    usuario_email.short_description = 'Email'

    def usuario_nome(self, obj):
        return obj.usuario.nome
    usuario_nome.short_description = 'Nome'

    def usuario_data_cadastro(self, obj):
        return obj.usuario.date_joined
    usuario_data_cadastro.short_description = 'Data de Cadastro'

@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('usuario_email', 'usuario_nome', 'usuario_data_cadastro')
    search_fields = ('usuario__email', 'usuario__nome')

    def usuario_email(self, obj):
        return obj.usuario.email
    usuario_email.short_description = 'Email'

    def usuario_nome(self, obj):
        return obj.usuario.nome
    usuario_nome.short_description = 'Nome'

    def usuario_data_cadastro(self, obj):
        return obj.usuario.date_joined
    usuario_data_cadastro.short_description = 'Data de Cadastro'

@admin.register(EstatisticaEmpresa)
class EstatisticaEmpresaAdmin(admin.ModelAdmin):
    list_display = ('usuario_empresa', 'total_reclamacoes', 'reclamacoes_resolvidas', 'reclamacoes_pendentes')
    search_fields = ('usuario_empresa__razao_social',)

@admin.register(Reclamacao)
class ReclamacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario_consumidor', 'empresa', 'status', 'data_criacao')
    list_filter = ('status', 'data_criacao', 'empresa')
    search_fields = ('titulo', 'descricao', 'usuario_consumidor__usuario__nome', 'empresa__razao_social')
    ordering = ('-data_criacao',)

@admin.register(Arquivo)
class ArquivoAdmin(admin.ModelAdmin):
    list_display = ('nome_arquivo', 'reclamacao', 'tipo_arquivo', 'data_upload')
    list_filter = ('tipo_arquivo', 'data_upload',)
    search_fields = ('nome_arquivo', 'reclamacao__titulo')

@admin.register(RespostaReclamacao)
class RespostaReclamacaoAdmin(admin.ModelAdmin):
    list_display = ('reclamacao', 'empresa', 'status_resolucao', 'data_criacao')
    list_filter = ('status_resolucao', 'data_criacao', 'empresa')
    search_fields = ('reclamacao__titulo', 'empresa__razao_social', 'descricao')
    ordering = ('-data_criacao',)

@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'administrador', 'data_geracao')
    list_filter = ('data_geracao', 'administrador')
    search_fields = ('titulo', 'conteudo', 'administrador__usuario__nome')
    ordering = ('-data_geracao',)
