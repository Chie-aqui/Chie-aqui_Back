from django.db import models
from django.core.exceptions import ValidationError
from api.models import Usuario

# REMOVIDA: from .consumidor import UsuarioConsumidor <-- Isso causava o ciclo

class UsuarioEmpresa(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    cnpj = models.CharField(max_length=18, unique=True)
    razao_social = models.CharField(max_length=255)
    nome_social = models.CharField(max_length=255, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        from .consumidor import UsuarioConsumidor
        if UsuarioConsumidor.objects.filter(usuario=self.usuario).exists():
            raise ValidationError(
                'Um usuário cadastrado como Empresa não pode ser também um Consumidor.'
            )
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.razao_social