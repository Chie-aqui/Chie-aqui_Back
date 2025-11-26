from django.db import models
from .empresa import UsuarioEmpresa
from .consumidor import UsuarioConsumidor

class Reclamacao(models.Model):
    class StatusReclamacao(models.TextChoices):
        ABERTA = 'ABERTA', 'Aberta'
        ENCERRADA = 'ENCERRADA', 'Encerrada'

    usuario_consumidor = models.ForeignKey(UsuarioConsumidor, on_delete=models.CASCADE, related_name='reclamacoes')
    empresa = models.ForeignKey(UsuarioEmpresa, on_delete=models.CASCADE, related_name='reclamacoes_recebidas')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=StatusReclamacao.choices,
        default=StatusReclamacao.ABERTA
    )

    def __str__(self):
        return self.titulo
