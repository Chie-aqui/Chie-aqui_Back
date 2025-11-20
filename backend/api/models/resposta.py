from django.db import models
from .reclamacao import Reclamacao
from .empresa import UsuarioEmpresa

class RespostaReclamacao(models.Model):
    class StatusResolucao(models.TextChoices):
        RESOLVIDA = 'RESOLVIDA', 'Resolvida'
        NAO_RESOLVIDA = 'NAO_RESOLVIDA', 'Não Resolvida'
        EM_ANALISE = 'EM_ANALISE', 'Em Análise'

    reclamacao = models.ForeignKey(Reclamacao, on_delete=models.CASCADE, related_name='respostas')
    empresa = models.ForeignKey(UsuarioEmpresa, on_delete=models.CASCADE, related_name='respostas_enviadas')
    descricao = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    status_resolucao = models.CharField(
        max_length=20,
        choices=StatusResolucao.choices,
        default=StatusResolucao.EM_ANALISE
    )

    def __str__(self):
        return f"Resposta para: {self.reclamacao.titulo}"
