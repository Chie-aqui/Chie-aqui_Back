from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Reclamacao, RespostaReclamacao, EstatisticaEmpresa, UsuarioEmpresa
import logging

logger = logging.getLogger(__name__)

def update_company_statistics(company_user_empresa):
    """Calculates and updates statistics for a given company."""
    if not isinstance(company_user_empresa, UsuarioEmpresa):
        logger.error(f"Invalid company_user_empresa type: {type(company_user_empresa)}")
        return

    stats, created = EstatisticaEmpresa.objects.get_or_create(usuario_empresa=company_user_empresa)

    all_complaints = Reclamacao.objects.filter(empresa=company_user_empresa)
    stats.total_reclamacoes = all_complaints.count()
    stats.reclamacoes_resolvidas = all_complaints.filter(status='Resolvida').count()
    stats.reclamacoes_pendentes = all_complaints.exclude(status='Resolvida').count()

    resolved_complaints = all_complaints.filter(status='Resolvida')
    total_resolution_time = timezone.timedelta(0)
    resolved_count = 0

    for complaint in resolved_complaints:
        # Find the first response that marked it as 'Resolvida'
        first_resolved_response = RespostaReclamacao.objects.filter(
            reclamacao=complaint,
            status_resolucao='Resolvida'
        ).order_by('data_criacao').first()

        if first_resolved_response:
            time_to_resolve = first_resolved_response.data_criacao - complaint.data_criacao
            total_resolution_time += time_to_resolve
            resolved_count += 1
    
    if resolved_count > 0:
        average_time_delta = total_resolution_time / resolved_count
        # Convert timedelta to hours (float)
        stats.media_tempo_resolucao = average_time_delta.total_seconds() / 3600
    else:
        stats.media_tempo_resolucao = 0.0

    stats.save()
    logger.info(f"Statistics updated for company {company_user_empresa.razao_social} (ID: {company_user_empresa.pk})")


@receiver(post_save, sender=Reclamacao)
def reclamacao_post_save(sender, instance, created, **kwargs):
    """Updates company statistics when a Reclamacao is saved."""
    logger.info(f"Reclamacao saved: {instance.id}, Created: {created}, Status: {instance.status}")
    update_company_statistics(instance.empresa)


@receiver(post_save, sender=RespostaReclamacao)
def resposta_reclamacao_post_save(sender, instance, created, **kwargs):
    """Updates company statistics when a RespostaReclamacao is saved."""
    logger.info(f"RespostaReclamacao saved: {instance.id}, Created: {created}, Status: {instance.status_resolucao}")
    
    complaint = instance.reclamacao
    original_complaint_status = complaint.status
    
    status_changed = False
    if instance.status_resolucao == 'Resolvida' and complaint.status != 'Resolvida':
        complaint.status = 'Resolvida'
        status_changed = True
    elif instance.status_resolucao == 'Em Análise' and complaint.status != 'Em Análise':
        complaint.status = 'Em Análise'
        status_changed = True
    
    if status_changed:
        complaint.save(update_fields=['status']) # This will trigger reclamacao_post_save, which updates statistics
    else:
        # If the complaint status didn't change, still update statistics to reflect
        # potential changes in resolution time or other metrics
        update_company_statistics(instance.empresa)

