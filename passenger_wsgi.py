"""
ONIZOUKA SHOP - Point d'entrée Phusion Passenger pour hébergement o2switch (cPanel)
"""
import os
import sys
import traceback

# Répertoire racine du projet
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Ajouter le site-packages de l'environnement virtuel Python
for venv_site_packages in [
    '/home/sc1vuxe8870/virtualenv/repositories/onizukashop/3.11/lib/python3.11/site-packages',
    '/home/sc1vuxe8870/virtualenv/repositories/onizukashop/3.12/lib/python3.12/site-packages',
]:
    if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
        sys.path.insert(0, venv_site_packages)

# Charger les variables d'environnement depuis le fichier .env (pure Python sans dépendance externe)
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    k = k.strip()
                    v = v.strip().strip("'").strip('"')
                    os.environ[k] = v
    except Exception:
        pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onizouka.settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    err_trace = traceback.format_exc()

    def application(environ, start_response):
        start_response('500 Internal Server Error', [('Content-Type', 'text/html; charset=utf-8')])
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Diagnostic Django - Onizouka Shop</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; padding: 30px; background: #fff1f2; color: #881337;">
            <div style="max-width: 900px; margin: 0 auto; background: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #fecdd3; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <h2 style="color: #be123c; margin-top: 0;">Diagnostic de Démarrage Django</h2>
                <p style="color: #4b5563;">Une erreur est survenue lors de l'initialisation de l'application :</p>
                <pre style="background: #1e293b; color: #f8fafc; padding: 18px; border-radius: 8px; overflow-x: auto; font-size: 13px; line-height: 1.5;">{err_trace}</pre>
                <hr style="border: 0; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="font-size: 12px; color: #6b7280;">Python Executable: {sys.executable}<br>Sys Path: {sys.path[:4]}</p>
            </div>
        </body>
        </html>
        """
        return [html.encode('utf-8')]
