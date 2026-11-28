"""
ONIZUKA SHOP - Vues Globales Système
Gestionnaires d'erreurs HTTP & Récupération CSRF avec surveillance anti-intrusion
"""
import logging
from django.core.cache import cache
from django.shortcuts import render

logger = logging.getLogger(__name__)


def csrf_failure(request, reason=""):
    """
    Vue sur-mesure de secours lors d'un échec de vérification CSRF (403).
    Déclenche une alerte d'intrusion à admin@danayaplus.com en cas de tentatives
    répétées de falsification CSRF ou d'attaque POST automatisée depuis une même IP.
    """
    try:
        from onizouka.security_shield import get_client_ip_info, collect_forensic_summary, record_and_alert_intrusion
        ip, _, _ = get_client_ip_info(request)
        csrf_key = f"sec_csrf_fail_{ip}"
        fails = cache.get(csrf_key, 0) + 1
        cache.set(csrf_key, fails, timeout=300)

        if fails >= 4:
            summary = collect_forensic_summary(
                request,
                attack_type="Attaque CSRF / Soumissions POST Forgées Répétées",
                details=f"{fails} rejets CSRF consécutifs en moins de 5 minutes (motif Django : {reason}).",
                severity='medium',
                action_taken="Requête POST rejetée (HTTP 403 CSRF)",
            )
            record_and_alert_intrusion(summary)
    except Exception:
        pass

    logger.warning(
        "CSRF Failure sur Onizuka Shop: %s - URL: %s - Referer: %s - Host: %s - Scheme: %s",
        reason,
        request.path,
        request.META.get('HTTP_REFERER', 'N/A'),
        request.get_host(),
        request.scheme
    )
    return render(
        request,
        '403_csrf.html',
        {
            'reason': reason,
            'current_path': request.get_full_path(),
        },
        status=403
    )
