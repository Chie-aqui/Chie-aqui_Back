from django.db import models
from .administrador import Administrador

class Relatorio(models.Model):
    administrador = models.ForeignKey(Administrador, on_delete=models.SET_NULL, null=True, blank=True, related_name='relatorios_gerados')
    titulo = models.CharField(max_length=255)
    data_geracao = models.DateTimeField(auto_now_add=True)
    conteudo = models.TextField()

    def __str__(self):
        return self.titulo
