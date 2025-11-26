from django.db import models
from .reclamacao import Reclamacao

class Arquivo(models.Model):
    reclamacao = models.ForeignKey(Reclamacao, on_delete=models.CASCADE, related_name='arquivos')
    arquivo = models.FileField(upload_to='arquivos_reclamacoes/')
    nome_arquivo = models.CharField(max_length=255)
    tipo_arquivo = models.CharField(max_length=100)
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome_arquivo
