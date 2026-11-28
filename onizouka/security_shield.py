"""
ONIZUKA SHOP - Bouclier de Défense & Détection Anti-Intrusion (WAF / IDS / IPS)
Intercepte les tentatives de piratage, bannit automatiquement les récidivistes,
journalise chaque incident en base de données et envoie une alerte temps réel
ultra-complète à admin@danayaplus.com avec toutes les informations de l'attaquant.
"""
import hashlib
import logging
import os
import re
import threading
from datetime import timedelta
from urllib.parse import unquote, unquote_plus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_login_failed
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.http import HttpResponseForbidden
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger('security')

# Destinataire officiel des alertes de sécurité / intrusion
SECURITY_ALERT_EMAIL = os.environ.get('SECURITY_ALERT_EMAIL', 'admin@danayaplus.com').strip() or 'admin@danayaplus.com'

# IPs locales de développement / bouclage à ne pas auto-bannir définitivement lors de tests internes
LOCAL_SAFE_IPS = {'127.0.0.1', '::1', 'localhost'}

# 1. Signatures d'outils de piratage et scanners de vulnérabilités connus (User-Agent)
HACKER_TOOLS_SIGNATURES = [
    (r'sqlmap', 'Outil d\'injection SQL automatisé (SQLMap)'),
    (r'nikto', 'Scanner de vulnérabilités Web (Nikto)'),
    (r'nmap|nse', 'Scanner réseau & scripts Nmap'),
    (r'nuclei', 'Scanner d\'exploits automatisé (Nuclei)'),
    (r'acunetix|wvsc', 'Scanner de failles Web (Acunetix)'),
    (r'nessus|openvas', 'Scanner de vulnérabilités (Nessus/OpenVAS)'),
    (r'gobuster|dirbuster|dirb|feroxbuster|ffuf|wfuzz', 'Bruteforce de répertoires & fichiers cachés'),
    (r'wpscan', 'Scanner d\'exploitation WordPress (WPScan)'),
    (r'hydra|medusa|patator', 'Outil de cassage de mots de passe (Hydra/Medusa)'),
    (r'metasploit|meterpreter', 'Framework d\'exploitation (Metasploit)'),
    (r'havij|pangolin|sqlninja', 'Outil d\'exploitation SQLi automatisé'),
    (r'masscan|zgrab|censysinspect', 'Scanneur de masse offensif'),
    (r'burpcollaborator|interact\.sh|oastify', 'Sonde d\'exploitation Out-of-Band (SSRF/XXE)'),
    (r'commix', 'Outil d\'injection de commandes OS (Commix)'),
    (r'xsstrike|dalfox', 'Outil d\'attaque XSS automatisé'),
]
COMPILED_TOOL_SIGNATURES = [(re.compile(pat, re.IGNORECASE), label) for pat, label in HACKER_TOOLS_SIGNATURES]

# 2. Chemins pièges (Honeypots) & Sondes de fichiers sensibles
SUSPICIOUS_PATHS = [
    r'(?:^|/)\.env(?:\.|$|/)',
    r'(?:^|/)\.git(?:/|$)',
    r'(?:^|/)\.svn(?:/|$)',
    r'(?:^|/)\.hg(?:/|$)',
    r'(?:^|/)\.aws(?:/|$)',
    r'(?:^|/)\.ssh(?:/|$)',
    r'(?:^|/)\.htaccess$',
    r'(?:^|/)\.htpasswd$',
    r'(?:^|/)wp-login\.php$',
    r'(?:^|/)wp-admin(?:/|$)',
    r'(?:^|/)wp-config\.php',
    r'(?:^|/)xmlrpc\.php$',
    r'(?:^|/)(?:phpmyadmin|pma|myadmin|dbadmin)(?:/|$)',
    r'(?:^|/)adminer(?:\.php|/|$)',
    r'(?:^|/)phpinfo\.php$',
    r'(?:^|/)vendor/phpunit(?:/|$)',
    r'(?:^|/)eval-stdin\.php$',
    r'(?:^|/)(?:shell|c99|r57|alfa|webshell|backdoor|cmd|upload)\.php$',
    r'(?:^|/)cgi-bin(?:/|$)',
    r'(?:^|/)boaform(?:/|$)',
    r'(?:^|/)actuator(?:/|$)',
    r'(?:^|/)(?:db\.sqlite3|database\.sqlite|dump\.sql|backup\.sql|backup\.zip)$',
    r'(?:^|/)backups(?:/|$)',
]
SUSPICIOUS_PATH_REGEX = re.compile('|'.join(SUSPICIOUS_PATHS), re.IGNORECASE)

# 3. Signatures d'attaques dans l'URL, la Query String et les champs POST non-authentifiés
ATTACK_PATTERNS = [
    # Path Traversal & Local File Inclusion (LFI)
    (
        r'(?:\.\./|\.\.\\|%2e%2e%2f|%2e%2e/|/etc/passwd|/etc/shadow|/proc/self/environ|c:\\windows\\win\.ini|boot\.ini)',
        'Tentative de Path Traversal / Inclusion de fichier système (LFI)',
        'critical',
    ),
    # SQL Injection (SQLi) - formulé avec précision (inclut l'obfuscation par commentaires /**/ et +)
    (
        r'(?i)(?:union(?:[\s+]|/\*.*?\*/)+(?:all(?:[\s+]|/\*.*?\*/)+)?select\b|'
        r'(?:\'|"|\))[\s+]*(?:or|and)[\s+]*(?:\'?"?\d+\'?"?[\s+]*=[\s+]*\'?"?\d+|\'[^\']*\'[\s+]*=[\s+]*\'[^\']*\')|'
        r'\b(?:information_schema|pg_catalog|sys\.tables)\b|'
        r'\b(?:sleep|pg_sleep)\s*\(\s*\d+\s*\)|'
        r'\bbenchmark\s*\(\s*\d+|'
        r'\bwaitfor[\s+]+delay[\s+]+[\'"]|'
        r'\b(?:load_file|into[\s+]+(?:out|dump)file|extractvalue|updatexml)\s*\(|'
        r';[\s+]*(?:drop|truncate|alter)[\s+]+table\b)',
        'Tentative d\'Injection SQL (SQLi)',
        'critical',
    ),
    # Cross-Site Scripting (XSS)
    (
        r'(?i)(?:<\s*script\b|javascript\s*:|vbscript\s*:|'
        r'\bon(?:error|load|mouseover|focus|toggle|animationstart)\s*=\s*[\'"a-z0-9_]|'
        r'<\s*(?:svg|img|body|iframe|object|embed)\b[^>]*\bon\w+\s*=|'
        r'document\.cookie|String\.fromCharCode\s*\()',
        'Tentative d\'Injection de Script Cross-Site (XSS)',
        'high',
    ),
    # Remote Code Execution (RCE) / OS Command Injection
    (
        r'(?i)(?:;\s*(?:cat|ls|id|whoami|uname|wget|curl|nc|netcat|bash|sh)\s+|'
        r'\|\s*(?:/bin/(?:ba)?sh|cmd\.exe|powershell)\b|'
        r'\$\((?:whoami|id|uname|cat\s+|wget\s+|curl\s+)|'
        r'`(?:whoami|id|uname|cat\s+|wget\s+|curl\s+)`|'
        r'\b(?:passthru|shell_exec|system|phpinfo)\s*\()',
        'Tentative d\'Exécution de Commande à Distance (RCE)',
        'critical',
    ),
    # JNDI / Log4Shell / Server-Side Template Injection (SSTI)
    (
        r'(?i)(?:\$\{jndi:(?:ldap|rmi|dns|nis|iiop|corba|http)s?://|'
        r'\{\{\s*.*?(?:__class__|__mro__|__subclasses__|__globals__|config\.items).*?\}\})',
        'Tentative d\'Injection Template SSTI / JNDI (Log4Shell)',
        'critical',
    ),
]
COMPILED_ATTACK_PATTERNS = [(re.compile(pat), desc, sev) for pat, desc, sev in ATTACK_PATTERNS]

# 4. Extensions de fichiers strictement interdites à l'upload
DANGEROUS_UPLOAD_EXTENSIONS = {
    '.php', '.php3', '.php4', '.php5', '.php7', '.phtml', '.phar',
    '.py', '.pyc', '.pyo', '.sh', '.bash', '.zsh',
    '.exe', '.dll', '.bat', '.cmd', '.ps1', '.vbs', '.msi', '.scr',
    '.jsp', '.jspx', '.asp', '.aspx', '.cer', '.asa',
    '.cgi', '.pl', '.htaccess', '.htpasswd', '.config', '.jar', '.war',
}

# Clés sensibles à ne jamais enregistrer en clair dans les logs ou emails
SENSITIVE_FIELD_NAMES = {
    'password', 'password1', 'password2', 'old_password', 'new_password',
    'csrfmiddlewaretoken', 'token', 'access_token', 'refresh_token',
    'secret', 'api_key', 'private_key', 'credit_card', 'cvv', 'pin', 'otp',
}


def get_client_ip_info(request):
    """
    Extrait l'adresse IP réelle de l'attaquant ainsi que la chaîne complète des proxies.
    Retourne un tuple (real_ip, forwarded_chain, country).
    """
    meta = request.META or {}
    xff = (meta.get('HTTP_X_FORWARDED_FOR') or '').strip()
    cf_ip = (meta.get('HTTP_CF_CONNECTING_IP') or '').strip()
    true_ip = (meta.get('HTTP_TRUE_CLIENT_IP') or '').strip()
    real_ip_hdr = (meta.get('HTTP_X_REAL_IP') or '').strip()
    remote_addr = (meta.get('REMOTE_ADDR') or 'Inconnue').strip()
    country = (meta.get('HTTP_CF_IPCOUNTRY') or meta.get('HTTP_X_COUNTRY_CODE') or '').strip()

    # Priorité aux en-têtes proxy de confiance
    if cf_ip:
        real_ip = cf_ip
    elif true_ip:
        real_ip = true_ip
    elif real_ip_hdr:
        real_ip = real_ip_hdr
    elif xff:
        real_ip = xff.split(',')[0].strip()
    else:
        real_ip = remote_addr

    chain_parts = []
    if xff:
        chain_parts.append(f"XFF: {xff}")
    if real_ip_hdr and real_ip_hdr != real_ip:
        chain_parts.append(f"X-Real-IP: {real_ip_hdr}")
    if remote_addr and remote_addr != real_ip:
        chain_parts.append(f"Socket: {remote_addr}")

    return real_ip or 'Inconnue', ' | '.join(chain_parts) or 'Connexion directe', country or 'Non résolu'


def fingerprint_attacker_agent(user_agent):
    """Analyse le User-Agent pour identifier le système d'exploitation, le navigateur ou l'outil offensif."""
    if not user_agent:
        return "Suspect : Aucun User-Agent (Script brut / Socket)"

    for regex, tool_name in COMPILED_TOOL_SIGNATURES:
        if regex.search(user_agent):
            return f"⚠️ {tool_name}"

    ua_low = user_agent.lower()
    if 'python-requests' in ua_low or 'urllib' in ua_low or 'aiohttp' in ua_low or 'httpx' in ua_low:
        return "Script automatisé Python (requests/httpx/urllib)"
    if 'curl/' in ua_low:
        return "Ligne de commande cURL"
    if 'wget/' in ua_low:
        return "Ligne de commande Wget"
    if 'go-http-client' in ua_low:
        return "Bot automatisé Go (Go-http-client)"
    if 'postmanruntime' in ua_low or 'insomnia' in ua_low:
        return "Client d'inspection API (Postman / Insomnia)"
    if 'headlesschrome' in ua_low or 'phantomjs' in ua_low or 'playwright' in ua_low or 'selenium' in ua_low:
        return "Navigateur automatisé Headless (Bot)"

    os_label = "OS Inconnu"
    if 'kali' in ua_low or 'parrot' in ua_low:
        os_label = "⚠️ Linux Offensif (Kali / Parrot)"
    elif 'windows nt 10.0' in ua_low:
        os_label = "Windows 10/11"
    elif 'windows' in ua_low:
        os_label = "Windows"
    elif 'android' in ua_low:
        os_label = "Android Mobile"
    elif 'iphone' in ua_low or 'ipad' in ua_low:
        os_label = "iOS (iPhone/iPad)"
    elif 'mac os x' in ua_low or 'macintosh' in ua_low:
        os_label = "macOS"
    elif 'linux' in ua_low:
        os_label = "Linux"

    browser_label = "Navigateur"
    if 'edg/' in ua_low:
        browser_label = "Microsoft Edge"
    elif 'opr/' in ua_low or 'opera' in ua_low:
        browser_label = "Opera"
    elif 'chrome/' in ua_low:
        browser_label = "Google Chrome"
    elif 'firefox/' in ua_low:
        browser_label = "Mozilla Firefox"
    elif 'safari/' in ua_low:
        browser_label = "Apple Safari"

    return f"{os_label} • {browser_label}"


def extract_sanitized_payload(request):
    """
    Extrait un aperçu lisible des paramètres POST et fichiers envoyés par l'attaquant,
    tout en masquant strictement les mots de passe, jetons CSRF et clés secrètes.
    """
    parts = []
    try:
        if request.method in ('POST', 'PUT', 'PATCH'):
            if hasattr(request, 'POST') and request.POST:
                items = []
                for k in list(request.POST.keys())[:25]:
                    k_clean = str(k)
                    if any(sec in k_clean.lower() for sec in SENSITIVE_FIELD_NAMES):
                        items.append(f"{k_clean}=[MASQUÉ]")
                    else:
                        val = str(request.POST.get(k, ''))[:220]
                        items.append(f"{k_clean}={val}")
                if items:
                    parts.append("POST: " + " & ".join(items))
            else:
                # Corps brut JSON/XML éventuel (limité aux 500 premiers octets)
                content_type = (request.META.get('CONTENT_TYPE') or '').lower()
                if any(t in content_type for t in ('json', 'xml', 'text', 'urlencoded')):
                    raw_body = request.body[:500].decode('utf-8', errors='replace')
                    # Masquer d'éventuels champs password dans le JSON brut
                    raw_body = re.sub(
                        r'("(?:password|token|secret|pin|otp)"\s*:\s*)"[^"]*"',
                        r'\1"[MASQUÉ]"',
                        raw_body,
                        flags=re.IGNORECASE,
                    )
                    if raw_body.strip():
                        parts.append(f"BODY: {raw_body.strip()}")

        if hasattr(request, 'FILES') and request.FILES:
            files_desc = []
            for field_name, fobj in request.FILES.items():
                files_desc.append(f"{field_name}: '{fobj.name}' ({fobj.content_type}, {fobj.size} octets)")
            if files_desc:
                parts.append("FILES: " + ", ".join(files_desc))
    except Exception:
        pass

    return " | ".join(parts)[:1200] if parts else "Aucune charge POST"


def collect_forensic_summary(request, attack_type, details="", severity="high", targeted_user=None, action_taken="Requête bloquée (HTTP 403 Forbidden)", ip_auto_banned=False):
    """Rassemble toutes les métadonnées médico-légales sur l'attaquant et la requête."""
    now_local = timezone.localtime(timezone.now())
    ip, forwarded_ips, country = get_client_ip_info(request)
    meta = request.META or {}

    user_agent = (meta.get('HTTP_USER_AGENT') or '').strip()
    attacker_tool = fingerprint_attacker_agent(user_agent)
    referer = (meta.get('HTTP_REFERER') or meta.get('HTTP_ORIGIN') or 'Aucun (accès direct / outil externe)').strip()
    accept_lang = (meta.get('HTTP_ACCEPT_LANGUAGE') or 'Non spécifiée').strip()[:120]
    method = request.method or 'GET'
    host = meta.get('HTTP_HOST') or meta.get('SERVER_NAME') or 'onizukashop.com'
    scheme = 'HTTPS' if request.is_secure() else 'HTTP'
    remote_port = str(meta.get('REMOTE_PORT') or 'N/A')
    path = request.path or '/'
    query_string = (meta.get('QUERY_STRING') or '')[:800]
    full_url = f"{scheme.lower()}://{host}{request.get_full_path()[:600]}"

    if not targeted_user:
        req_user = getattr(request, 'user', None)
        if req_user and getattr(req_user, 'is_authenticated', False):
            role = 'Superadmin IT' if req_user.is_superuser else ('Staff Direction' if req_user.is_staff else 'Client connecté')
            targeted_user = f"{req_user.username} ({role})"
        else:
            targeted_user = "Visiteur Anonyme (Non authentifié)"

    # En-têtes HTTP pertinents (sans cookies ni Authorization)
    headers_dict = {}
    excluded_headers = {'HTTP_COOKIE', 'HTTP_AUTHORIZATION', 'HTTP_PROXY_AUTHORIZATION'}
    for k, v in sorted(meta.items()):
        if (k.startswith('HTTP_') or k in ('CONTENT_TYPE', 'CONTENT_LENGTH', 'REMOTE_ADDR', 'REMOTE_PORT', 'SERVER_PROTOCOL')) and k not in excluded_headers:
            clean_k = k[5:].replace('_', '-').title() if k.startswith('HTTP_') else k.replace('_', '-').title()
            headers_dict[clean_k] = str(v)[:350]

    headers_lines = "\n".join(f"{k}: {v}" for k, v in headers_dict.items())
    payload_excerpt = extract_sanitized_payload(request)

    # Identifiant unique d'incident traçable
    raw_hash = hashlib.sha256(f"{now_local.isoformat()}|{ip}|{attack_type}|{path}".encode('utf-8', errors='ignore')).hexdigest()[:6].upper()
    incident_id = f"SEC-{now_local.strftime('%Y%m%d')}-{raw_hash}"

    return {
        'incident_id': incident_id,
        'severity': severity,
        'severity_label': {
            'critical': 'CRITIQUE (URGENCE)',
            'high': 'ÉLEVÉE',
            'medium': 'MOYENNE',
            'low': 'FAIBLE',
        }.get(severity, 'ÉLEVÉE'),
        'attack_type': attack_type,
        'details': details or "Activité suspecte interceptée par le pare-feu applicatif.",
        'timestamp': now_local.strftime('%d/%m/%Y à %H:%M:%S'),
        'ip': ip,
        'forwarded_ips': forwarded_ips,
        'country': country,
        'remote_port': remote_port,
        'scheme': scheme,
        'user_agent': user_agent or 'Aucun User-Agent transmis',
        'attacker_tool': attacker_tool,
        'referer': referer[:500],
        'accept_language': accept_lang,
        'method': method,
        'host': host,
        'path': path[:500],
        'query_string': query_string,
        'full_url': full_url,
        'payload_excerpt': payload_excerpt,
        'targeted_user': str(targeted_user)[:150],
        'headers_dict': headers_dict,
        'headers_dump': headers_lines[:3500],
        'action_taken': action_taken,
        'ip_auto_banned': ip_auto_banned,
        'alert_recipient': SECURITY_ALERT_EMAIL,
    }


def is_ip_blocked(ip):
    """Vérifie en mémoire cache (ultra-rapide) puis en BDD si une IP est bannie."""
    if not ip or ip in ('Inconnue',):
        return False

    cache_key = f"sec_blocked_ip_{ip}"
    cached = cache.get(cache_key)
    if cached is not None:
        return bool(cached)

    try:
        from backoffice.models import BlockedIP
        ban = BlockedIP.objects.filter(ip_address=ip, is_active=True).first()
        if ban:
            if ban.is_currently_blocked:
                cache.set(cache_key, True, timeout=300)
                return True
            else:
                # Le bannissement temporaire a expiré : lever proprement
                ban.is_active = False
                ban.save(update_fields=['is_active', 'updated_at'])
        cache.set(cache_key, False, timeout=120)
    except Exception:
        pass
    return False


def register_strike_and_maybe_autoban(ip, reason, user_agent="", force_ban=False, hours=24):
    """
    Incrémente le compteur d'infractions d'une IP.
    Au bout de 3 attaques critiques en 15 minutes (ou immédiatement si force_ban=True),
    bannit automatiquement l'adresse IP pendant 24h.
    """
    if not ip or ip in LOCAL_SAFE_IPS or ip == 'Inconnue':
        return False

    strike_key = f"sec_strikes_{ip}"
    strikes = cache.get(strike_key, 0) + 1
    cache.set(strike_key, strikes, timeout=900)  # Fenêtre de 15 minutes

    if not force_ban and strikes < 3:
        return False

    try:
        from backoffice.models import BlockedIP
        expires = timezone.now() + timedelta(hours=hours)
        ban, created = BlockedIP.objects.get_or_create(
            ip_address=ip,
            defaults={
                'reason': reason[:250],
                'attempts_count': strikes,
                'user_agent_sample': (user_agent or '')[:250],
                'is_active': True,
                'is_permanent': False,
                'expires_at': expires,
            },
        )
        if not created:
            ban.is_active = True
            ban.reason = reason[:250]
            ban.attempts_count = (ban.attempts_count or 0) + 1
            if user_agent:
                ban.user_agent_sample = user_agent[:250]
            if not ban.is_permanent:
                ban.expires_at = expires
            ban.save()

        cache.set(f"sec_blocked_ip_{ip}", True, timeout=hours * 3600)
        logger.error(f"[SECURITY AUTO-BAN] IP {ip} bannie automatiquement pour {hours}h : {reason}")
        return True
    except Exception as e:
        logger.error(f"[SECURITY] Impossible d'enregistrer le bannissement IP {ip}: {e}")
        return False


def _get_security_sender():
    """Construit l'expéditeur SMTP authentifié pour garantir la délivrabilité sur o2switch / cPanel."""
    raw_from = getattr(settings, 'DEFAULT_FROM_EMAIL', '') or getattr(settings, 'EMAIL_HOST_USER', 'contact@onizukashop.com')
    if '<' in raw_from and '>' in raw_from:
        addr = raw_from.split('<', 1)[1].split('>', 1)[0].strip()
    else:
        addr = raw_from.strip() or 'contact@onizukashop.com'
    return f"ONIZUKA SECURITY SHIELD <{addr}>"


def record_and_alert_intrusion(summary, bypass_throttle=False, sync=False):
    """
    1. Enregistre l'incident de sécurité en base de données (`SecurityIncident`).
    2. Envoie l'email d'alerte HTML + Texte à `admin@danayaplus.com` avec toutes les infos de l'attaquant.
    """
    def _worker():
        incident_obj = None
        try:
            from backoffice.models import SecurityIncident
            incident_obj = SecurityIncident.objects.create(
                incident_id=summary['incident_id'],
                severity=summary['severity'],
                attack_type=summary['attack_type'][:140],
                details=summary['details'],
                ip_address=summary['ip'][:64],
                forwarded_ips=summary['forwarded_ips'][:255],
                country=summary['country'][:32],
                user_agent=summary['user_agent'],
                attacker_tool=summary['attacker_tool'][:120],
                referer=summary['referer'],
                accept_language=summary['accept_language'][:120],
                method=summary['method'][:12],
                host=summary['host'][:150],
                path=summary['path'],
                query_string=summary['query_string'],
                payload_excerpt=summary['payload_excerpt'],
                targeted_user=summary['targeted_user'][:150],
                headers_dump=summary['headers_dump'],
                action_taken=summary['action_taken'][:160],
                ip_auto_banned=bool(summary.get('ip_auto_banned')),
                alert_sent=False,
            )
        except Exception as db_err:
            logger.error(f"[SECURITY] Échec sauvegarde BDD SecurityIncident: {db_err}")

        # Anti-flood email : max 1 email par couple (IP, type d'attaque) toutes les 3 minutes (sauf si auto-ban ou test)
        ip = summary['ip']
        throttle_key = f"sec_mail_throttle_{ip}_{hashlib.md5(summary['attack_type'].encode('utf-8', 'ignore')).hexdigest()[:8]}"
        if not bypass_throttle and not summary.get('ip_auto_banned') and cache.get(throttle_key):
            logger.warning(f"[SECURITY] Alerte email regroupée (anti-spam actif pour {ip}) - Incident {summary['incident_id']}")
            return False

        cache.set(throttle_key, True, timeout=180)

        ban_tag = " [IP BANNIE]" if summary.get('ip_auto_banned') else ""
        subject = f"🚨 [INTRUSION ONIZUKA SHOP]{ban_tag} {summary['attack_type']} • IP {ip}"
        from_email = _get_security_sender()

        text_body = (
            f"===================================================================\n"
            f"ALERTE D'INTRUSION & TENTATIVE DE PIRATAGE - ONIZUKA SHOP\n"
            f"Référence Incident : {summary['incident_id']} | Sévérité : {summary['severity_label']}\n"
            f"===================================================================\n\n"
            f"1. RÉSUMÉ DE L'ATTAQUE\n"
            f"-------------------------------------------------------------------\n"
            f"- Type d'attaque   : {summary['attack_type']}\n"
            f"- Diagnostic       : {summary['details']}\n"
            f"- Date & Heure     : {summary['timestamp']} (Bamako GMT)\n"
            f"- Mesure appliquée : {summary['action_taken']}\n"
            f"- Bannissement IP  : {'OUI - IP BANNIE AUTOMATIQUEMENT (24h)' if summary.get('ip_auto_banned') else 'Sous surveillance active'}\n\n"
            f"2. IDENTITÉ & TRAÇABILITÉ DE L'ATTAQUANT\n"
            f"-------------------------------------------------------------------\n"
            f"- Adresse IP Réelle   : {ip}\n"
            f"- Chaîne Proxies/VPN  : {summary['forwarded_ips']}\n"
            f"- Pays / Réseau       : {summary['country']}\n"
            f"- Port Distant        : {summary['remote_port']} ({summary['scheme']})\n"
            f"- Outil / OS Détecté  : {summary['attacker_tool']}\n"
            f"- User-Agent Complet  : {summary['user_agent']}\n"
            f"- Langue Navigateur   : {summary['accept_language']}\n"
            f"- Referer / Origine   : {summary['referer']}\n"
            f"- Compte Ciblé        : {summary['targeted_user']}\n\n"
            f"3. REQUÊTE & CHARGE UTILE INTERCEPTÉES\n"
            f"-------------------------------------------------------------------\n"
            f"- Requête HTTP     : {summary['method']} {summary['full_url']}\n"
            f"- Paramètres GET   : {summary['query_string'] or 'Aucun'}\n"
            f"- Payload Assaini  : {summary['payload_excerpt']}\n\n"
            f"4. EN-TÊTES HTTP COMPLETS DE L'ATTAQUANT\n"
            f"-------------------------------------------------------------------\n"
            f"{summary['headers_dump']}\n\n"
            f"5. LIENS D'INVESTIGATION RAPIDE\n"
            f"-------------------------------------------------------------------\n"
            f"- Géolocalisation & ASN : https://ipinfo.io/{ip}\n"
            f"- Réputation AbuseIPDB  : https://www.abuseipdb.com/check/{ip}\n"
            f"- Centre Sécurité IT    : https://{summary['host']}/gestion/securite/\n"
            f"===================================================================\n"
        )

        try:
            html_body = render_to_string('emails/security_intrusion_alert.html', {'s': summary})
        except Exception as tpl_err:
            logger.error(f"[SECURITY] Erreur rendu HTML alerte sécurité: {tpl_err}")
            html_body = None

        try:
            msg = EmailMultiAlternatives(
                subject=subject[:250],
                body=text_body,
                from_email=from_email,
                to=[SECURITY_ALERT_EMAIL],
            )
            if html_body:
                msg.attach_alternative(html_body, "text/html")
            msg.send(fail_silently=False)

            if incident_obj:
                incident_obj.alert_sent = True
                incident_obj.save(update_fields=['alert_sent'])

            try:
                from backoffice.models import EmailLog
                EmailLog.objects.create(
                    email_type='security_alert',
                    recipient=SECURITY_ALERT_EMAIL,
                    subject=subject[:255],
                    status='sent',
                )
            except Exception:
                pass

            logger.warning(f"[SECURITY ALERT SENT] {summary['incident_id']} envoyé à {SECURITY_ALERT_EMAIL} (Attaquant: {ip})")
            return True
        except Exception as mail_err:
            logger.error(f"[SECURITY EMAIL ERROR] Échec d'envoi vers {SECURITY_ALERT_EMAIL}: {mail_err}")
            try:
                from backoffice.models import EmailLog
                EmailLog.objects.create(
                    email_type='security_alert',
                    recipient=SECURITY_ALERT_EMAIL,
                    subject=subject[:255],
                    status='failed',
                    error_message=str(mail_err)[:500],
                )
            except Exception:
                pass
            return False

    if sync:
        return _worker()

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    return True


def _forbidden_shield_response(incident_id, banned=False):
    """Réponse HTTP 403 sobre et sécurisée qui ne divulgue aucune information technique du serveur."""
    status_msg = "Votre adresse IP a été bannie par le système de protection." if banned else "Activité malveillante bloquée et journalisée."
    html = (
        "<!DOCTYPE html><html lang='fr'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>403 Accès Bloqué • Onizuka Security Shield</title>"
        "<style>body{background:#0d0e12;color:#f8fafc;font-family:system-ui,sans-serif;display:flex;"
        "align-items:center;justify-content:center;min-height:100vh;margin:0;padding:20px}"
        ".box{max-width:460px;background:#16181f;border:1px solid rgba(239,68,68,.4);border-radius:16px;"
        "padding:28px;text-align:center;box-shadow:0 20px 40px rgba(0,0,0,.5)}"
        ".badge{display:inline-block;padding:4px 12px;border-radius:99px;background:rgba(239,68,68,.15);"
        "color:#f87171;font-weight:800;font-size:12px;letter-spacing:.06em;text-transform:uppercase}"
        "h1{font-size:20px;margin:14px 0 8px}p{color:#94a3b8;font-size:13px;line-height:1.5;margin:0 0 14px}"
        "code{display:inline-block;background:#0d0e12;color:#fbbf24;padding:6px 12px;border-radius:8px;"
        "font-size:12px;border:1px solid rgba(251,191,36,.2)}</style></head><body>"
        f"<div class='box'><span class='badge'>Onizuka Security Shield</span>"
        f"<h1>Accès Interdit (403)</h1><p>{status_msg}<br>Les paramètres de votre connexion ont été transmis à l'équipe sécurité.</p>"
        f"<code>Réf : {incident_id}</code></div></body></html>"
    )
    resp = HttpResponseForbidden(html)
    resp['X-Content-Type-Options'] = 'nosniff'
    resp['X-Frame-Options'] = 'DENY'
    resp['Cache-Control'] = 'no-store'
    return resp


class IntrusionDetectionMiddleware:
    """
    Pare-feu applicatif (WAF) et Système de Prévention d'Intrusions (IPS) :
    - Vérifie la liste noire d'IPs bannies
    - Bloque les scanners offensifs (SQLMap, Nikto, Nuclei, WPScan, etc.)
    - Bloque l'accès aux chemins pièges (.env, .git, wp-admin, phpmyadmin, db.sqlite3, etc.)
    - Analyse l'URL, la Query String, les uploads de fichiers et les formulaires publics contre SQLi, XSS, LFI, RCE, SSTI
    - Surveille les tentatives d'accès non autorisées au Backoffice et à Django Admin
    - Ajoute les en-têtes de durcissement HTTP sur chaque réponse
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip, _, _ = get_client_ip_info(request)
        path = request.path or '/'
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Ignorer les fichiers statiques légitimes pour des performances maximales (sauf si traversal ..)
        if (path.startswith('/static/') or path == '/favicon.ico') and '..' not in path and '%2e' not in path.lower():
            response = self.get_response(request)
            return self._apply_security_headers(response)

        # 0. Vérification immédiate si l'IP est déjà sur liste noire (IPS)
        if is_ip_blocked(ip):
            return _forbidden_shield_response("IP-BLACKLISTED", banned=True)

        # 1. Détection d'outils de piratage automatisés dans le User-Agent
        if user_agent:
            for tool_regex, tool_label in COMPILED_TOOL_SIGNATURES:
                if tool_regex.search(user_agent):
                    banned = register_strike_and_maybe_autoban(ip, f"Outil offensif détecté : {tool_label}", user_agent, force_ban=True)
                    summary = collect_forensic_summary(
                        request,
                        attack_type=tool_label,
                        details=f"Signature d'outil de piratage détectée dans l'en-tête User-Agent : '{user_agent[:180]}'",
                        severity='critical',
                        action_taken="Bloqué immédiatement (HTTP 403) + Bannissement IP 24h" if banned else "Bloqué immédiatement (HTTP 403)",
                        ip_auto_banned=banned,
                    )
                    record_and_alert_intrusion(summary)
                    return _forbidden_shield_response(summary['incident_id'], banned=banned)

        # 2. Détection de sondes sur fichiers sensibles / panneaux cachés (.env, .git, wp-login, phpmyadmin...)
        decoded_path = unquote(path)
        if SUSPICIOUS_PATH_REGEX.search(decoded_path):
            banned = register_strike_and_maybe_autoban(ip, f"Scan fichier sensible : {decoded_path[:100]}", user_agent)
            summary = collect_forensic_summary(
                request,
                attack_type="Scan de vulnérabilités / Fichiers sensibles",
                details=f"Tentative d'accès à une ressource sensible ou piège honeypot : {decoded_path}",
                severity='high',
                action_taken="Bloqué (HTTP 403) + IP bannie 24h" if banned else "Bloqué (HTTP 403)",
                ip_auto_banned=banned,
            )
            record_and_alert_intrusion(summary)
            return _forbidden_shield_response(summary['incident_id'], banned=banned)

        # 3. Inspection approfondie de l'URL et des paramètres GET (décodés contre double-encodage URL et '+')
        raw_query = request.META.get('QUERY_STRING', '')
        inspected_uri = unquote_plus(unquote_plus(f"{path}?{raw_query}" if raw_query else path))
        for pattern_regex, attack_desc, sev in COMPILED_ATTACK_PATTERNS:
            match = pattern_regex.search(inspected_uri)
            if match:
                banned = register_strike_and_maybe_autoban(ip, f"{attack_desc} via URL", user_agent)
                summary = collect_forensic_summary(
                    request,
                    attack_type=attack_desc,
                    details=f"Motif d'attaque intercepté dans l'URL : '{match.group(0)[:120]}'",
                    severity=sev,
                    action_taken="Bloqué (HTTP 403) + IP bannie 24h" if banned else "Bloqué (HTTP 403)",
                    ip_auto_banned=banned,
                )
                record_and_alert_intrusion(summary)
                return _forbidden_shield_response(summary['incident_id'], banned=banned)

        # 4. Protection des requêtes POST / PUT / Upload de fichiers
        if request.method in ('POST', 'PUT', 'PATCH'):
            req_user = getattr(request, 'user', None)
            is_trusted_staff = bool(req_user and getattr(req_user, 'is_authenticated', False) and req_user.is_staff)

            # 4a. Vérification systématique des fichiers uploadés (même pour un compte compromis !)
            if hasattr(request, 'FILES') and request.FILES:
                for field_name, uploaded_file in request.FILES.items():
                    fname = (uploaded_file.name or '').lower()
                    _, ext = os.path.splitext(fname)
                    # Double extension suspecte ex: image.php.jpg ou shell.php%00.png
                    has_executable_double_ext = bool(re.search(r'\.(php\d?|phtml|phar|py|sh|exe|jsp|aspx?)\.', fname))
                    if ext in DANGEROUS_UPLOAD_EXTENSIONS or has_executable_double_ext or '\x00' in fname:
                        banned = register_strike_and_maybe_autoban(ip, f"Upload malveillant ({uploaded_file.name})", user_agent, force_ban=True)
                        summary = collect_forensic_summary(
                            request,
                            attack_type="Tentative d'Upload de Webshell / Fichier Exécutable",
                            details=f"Fichier exécutable interdit intercepté dans '{field_name}' : '{uploaded_file.name}' ({uploaded_file.content_type})",
                            severity='critical',
                            action_taken="Upload bloqué (HTTP 403) + IP bannie 24h",
                            ip_auto_banned=banned,
                        )
                        record_and_alert_intrusion(summary)
                        return _forbidden_shield_response(summary['incident_id'], banned=banned)

            # 4b. Inspection des champs POST publics (visiteurs / clients hors backoffice staff)
            if not is_trusted_staff and hasattr(request, 'POST') and request.POST:
                for field_key, field_val in request.POST.items():
                    if any(sec in field_key.lower() for sec in SENSITIVE_FIELD_NAMES):
                        # Ne pas déclencher de faux positif sur un mot de passe complexe légitime,
                        # sauf injection SQL flagrante sur le champ login/username
                        continue
                    val_str = unquote_plus(str(field_val or ''))
                    for pattern_regex, attack_desc, sev in COMPILED_ATTACK_PATTERNS:
                        match = pattern_regex.search(val_str)
                        if match:
                            banned = register_strike_and_maybe_autoban(ip, f"{attack_desc} via champ POST '{field_key}'", user_agent)
                            summary = collect_forensic_summary(
                                request,
                                attack_type=f"{attack_desc} (Formulaire POST)",
                                details=f"Charge malveillante détectée dans le champ '{field_key}' : '{match.group(0)[:120]}'",
                                severity=sev,
                                action_taken="Requête POST bloquée (HTTP 403)" + (" + IP bannie 24h" if banned else ""),
                                ip_auto_banned=banned,
                            )
                            record_and_alert_intrusion(summary)
                            return _forbidden_shield_response(summary['incident_id'], banned=banned)

            # 4c. Anti-Bruteforce renforcé sur les pages de connexion
            if path in ('/accounts/login/', '/admin/login/', '/compte/connexion/'):
                bf_key = f"sec_login_post_rate_{ip}"
                bf_count = cache.get(bf_key, 0) + 1
                cache.set(bf_key, bf_count, timeout=600)  # 10 minutes
                if bf_count > 10:
                    targeted = request.POST.get('login') or request.POST.get('username') or 'Inconnu'
                    banned = register_strike_and_maybe_autoban(ip, f"Brute-force connexion ({bf_count} essais / 10 min)", user_agent, force_ban=True, hours=6)
                    summary = collect_forensic_summary(
                        request,
                        attack_type="Attaque Brute-Force sur la Connexion",
                        details=f"{bf_count} soumissions rapides d'authentification en moins de 10 minutes (cible : '{targeted}').",
                        severity='critical',
                        targeted_user=targeted,
                        action_taken="Connexion verrouillée (HTTP 403) + IP bannie 6h",
                        ip_auto_banned=banned,
                    )
                    record_and_alert_intrusion(summary)
                    return _forbidden_shield_response(summary['incident_id'], banned=banned)

        # 5. Détection d'escalade de privilèges vers /gestion/ ou /admin/ par un utilisateur connecté non autorisé
        req_user = getattr(request, 'user', None)
        if req_user and getattr(req_user, 'is_authenticated', False):
            if path.startswith('/gestion/') and not req_user.is_staff:
                summary = collect_forensic_summary(
                    request,
                    attack_type="Tentative d'accès non autorisé au Portail de Gestion",
                    details=f"Le compte client non-staff '{req_user.username}' ({req_user.email}) a tenté d'accéder à l'URL réservée '{path}'.",
                    severity='high',
                    action_taken="Accès refusé et redirigé",
                )
                record_and_alert_intrusion(summary)
            elif path.startswith('/admin/') and not req_user.is_superuser and not req_user.is_staff:
                summary = collect_forensic_summary(
                    request,
                    attack_type="Tentative d'accès non autorisé à Django Admin IT",
                    details=f"Le compte sans privilèges '{req_user.username}' a tenté d'accéder à '{path}'.",
                    severity='high',
                    action_taken="Accès refusé",
                )
                record_and_alert_intrusion(summary)

        response = self.get_response(request)
        return self._apply_security_headers(response)

    @staticmethod
    def _apply_security_headers(response):
        """Ajoute les en-têtes de protection modernes contre le sniffing MIME, le clickjacking et les fuites Referer."""
        if 'X-Content-Type-Options' not in response:
            response['X-Content-Type-Options'] = 'nosniff'
        if 'Referrer-Policy' not in response:
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        if 'Permissions-Policy' not in response:
            response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), payment=()'
        if 'X-XSS-Protection' not in response:
            response['X-XSS-Protection'] = '1; mode=block'
        return response


# ---------------------------------------------------------------------------
# Signaux d'authentification : Surveillance des échecs de connexion
# ---------------------------------------------------------------------------

@receiver(user_login_failed)
def on_user_login_failed_signal(sender, credentials, request, **kwargs):
    """
    Déclenché à chaque mot de passe erroné (Allauth, Django Admin ou Login personnalisé).
    - Alerte immédiate dès 3 échecs sur un compte sensible / staff / superuser.
    - Alerte + Bannissement temporaire dès 6 échecs depuis la même IP tous comptes confondus.
    """
    if not request:
        return

    ip, _, _ = get_client_ip_info(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    attempted_login = str(
        credentials.get('username')
        or credentials.get('email')
        or credentials.get('login')
        or 'Inconnu'
    ).strip()

    # Compteur global d'échecs par IP (fenêtre de 15 minutes)
    ip_fail_key = f"sec_auth_fail_ip_{ip}"
    ip_fails = cache.get(ip_fail_key, 0) + 1
    cache.set(ip_fail_key, ip_fails, timeout=900)

    # Vérifier si le compte visé est un compte privilégié (Staff, Superadmin ou noms clés)
    is_privileged_target = attempted_login.lower() in {
        'admin', 'root', 'administrator', 'superuser',
        'alasko_ff', 'alasko6e6ui3e@gmail.com',
        'admin_onizuka', 'admin_onizouka',
        'direction@onizukashop.com', 'admin@danayaplus.com',
    }
    if not is_privileged_target:
        try:
            User = get_user_model()
            u = User.objects.filter(username__iexact=attempted_login).first() or User.objects.filter(email__iexact=attempted_login).first()
            if u and (u.is_superuser or u.is_staff):
                is_privileged_target = True
        except Exception:
            pass

    logger.warning(f"[SECURITY AUTH FAIL] Échec #{ip_fails} pour '{attempted_login}' depuis IP {ip} (Privilégié={is_privileged_target})")

    if is_privileged_target and ip_fails >= 3:
        banned = False
        if ip_fails >= 6:
            banned = register_strike_and_maybe_autoban(
                ip,
                f"Tentative de piratage compte privilégié '{attempted_login}' ({ip_fails} échecs)",
                user_agent,
                force_ban=True,
                hours=12,
            )
        summary = collect_forensic_summary(
            request,
            attack_type=f"Tentative d'intrusion sur compte Administrateur ({attempted_login})",
            details=f"{ip_fails} tentatives de connexion échouées avec mot de passe incorrect sur le compte sensible '{attempted_login}'.",
            severity='critical',
            targeted_user=f"{attempted_login} (Compte Privilégié)",
            action_taken="IP bannie automatiquement pour 12h" if banned else "Échec bloqué • Surveillance renforcée active",
            ip_auto_banned=banned,
        )
        record_and_alert_intrusion(summary, bypass_throttle=(ip_fails in (3, 6)))

    elif ip_fails >= 6:
        banned = register_strike_and_maybe_autoban(
            ip,
            f"Credential Stuffing / Brute-Force ({ip_fails} mots de passe échoués)",
            user_agent,
            force_ban=True,
            hours=6,
        )
        summary = collect_forensic_summary(
            request,
            attack_type="Attaque Brute-Force / Credential Stuffing",
            details=f"{ip_fails} échecs d'authentification consécutifs depuis l'adresse IP {ip} (dernier compte visé : '{attempted_login}').",
            severity='high',
            targeted_user=attempted_login,
            action_taken="IP bannie automatiquement pour 6h" if banned else "Tentative rejetée",
            ip_auto_banned=banned,
        )
        record_and_alert_intrusion(summary, bypass_throttle=(ip_fails == 6))
