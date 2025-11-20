from django.db import models
from .empresa import UsuarioEmpresa

class EstatisticaEmpresa(models.Model):
    usuario_empresa = models.OneToOneField(UsuarioEmpresa, on_delete=models.CASCADE, primary_key=True)
    total_reclamacoes = models.IntegerField(default=0)
    reclamacoes_resolvidas = models.IntegerField(default=0)
    reclamacoes_pendentes = models.IntegerField(default=0)
    media_tempo_resolucao = models.FloatField(default=0.0, help_text="Média de tempo para resolução em horas")

    def __str__(self):
        return f"Estatísticas de {self.usuario_empresa.razao_social}"
