from django.db import models
from django.core.exceptions import ValidationError
from api.models import Usuario

# REMOVIDA: from .empresa import UsuarioEmpresa  <-- Isso causava o ciclo

class UsuarioConsumidor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

    def save(self, *args, **kwargs):
        # IMPORTAÇÃO TARDIA: Importa o modelo conflitante APENAS quando o save for chamado
        from .empresa import UsuarioEmpresa
        
        # 1. VERIFICAÇÃO DE CONFLITO
        if UsuarioEmpresa.objects.filter(usuario=self.usuario).exists():
            raise ValidationError(
                'Um usuário cadastrado como Consumidor não pode ser também uma Empresa.'
            )
        
        # 2. Continua com a operação save padrão
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Consumidor"
        verbose_name_plural = "Consumidores"

    def __str__(self):
        return self.usuario.nome or self.usuario.email