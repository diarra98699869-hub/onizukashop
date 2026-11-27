#!/bin/bash
# ==============================================================================
# ONIZUKA SHOP - Configuration et Démarrage Automatique Redis Privé sur o2switch
# Compte : sc1vuxe8870
# ==============================================================================

set -e

USER_HOME="/home/sc1vuxe8870"
REDIS_DIR="$USER_HOME/.redis"
REDIS_SOCK="$REDIS_DIR/redis.sock"
REDIS_CONF="$REDIS_DIR/redis.conf"
APP_DIR="$USER_HOME/repositories/onizukashop"

echo "=========================================================="
echo "    CONFIGURATION DU SERVEUR REDIS PRIVÉ (o2switch)"
echo "=========================================================="

# 1. Vérifier la disponibilité de redis-server
if ! command -v redis-server &> /dev/null; then
    echo "[-] Erreur : le binaire 'redis-server' n'est pas dans le PATH."
    echo "    Veuillez vérifier l'activation de Redis dans votre cPanel o2switch."
    exit 1
fi

echo "[+] Binaire redis-server détecté : $(command -v redis-server)"

# 2. Créer le répertoire .redis sécurisé (droits 700)
mkdir -p "$REDIS_DIR"
chmod 700 "$REDIS_DIR"

# 3. Arrêter une ancienne instance Redis éventuelle
if [ -S "$REDIS_SOCK" ]; then
    echo "[*] Arrêt de l'ancien processus Redis..."
    redis-cli -s "$REDIS_SOCK" shutdown 2>/dev/null || true
    sleep 1
    rm -f "$REDIS_SOCK"
fi

# 4. Générer la configuration Redis optimisée en RAM (64 Mo max, LRU)
cat << 'EOF' > "$REDIS_CONF"
daemonize yes
port 0
unixsocket /home/sc1vuxe8870/.redis/redis.sock
unixsocketperm 700
timeout 0
pidfile /home/sc1vuxe8870/.redis/redis.pid
logfile /home/sc1vuxe8870/.redis/redis.log
dir /home/sc1vuxe8870/.redis
maxmemory 64mb
maxmemory-policy allkeys-lru
save ""
EOF

echo "[+] Fichier de configuration généré dans $REDIS_CONF"

# 5. Démarrer le serveur Redis
redis-server "$REDIS_CONF"
sleep 1

# 6. Tester la connexion avec redis-cli
if command -v redis-cli &> /dev/null && [ -S "$REDIS_SOCK" ]; then
    PONG_RES=$(redis-cli -s "$REDIS_SOCK" ping 2>/dev/null || echo "FAIL")
    if [ "$PONG_RES" = "PONG" ]; then
        echo "[✓] SUCCÈS : Redis répond parfaitement ($PONG_RES) sur $REDIS_SOCK !"
    else
        echo "[!] Avertissement : Redis démarré mais redis-cli ping a renvoyé : $PONG_RES"
    fi
else
    echo "[*] Socket unix créé : $REDIS_SOCK"
fi

# 7. S'assurer que .env contient bien la bonne URL Redis
cd "$APP_DIR" || exit 1
if [ -f .env ]; then
    if grep -q "^REDIS_URL=" .env; then
        sed -i 's|^REDIS_URL=.*|REDIS_URL=unix:///home/sc1vuxe8870/.redis/redis.sock?db=1|' .env
    else
        echo "REDIS_URL=unix:///home/sc1vuxe8870/.redis/redis.sock?db=1" >> .env
    fi
    echo "[+] Fichier .env mis à jour avec REDIS_URL."
fi

# 8. Ajouter une tâche Cron pour relancer Redis au redémarrage serveur
CRON_CMD="@reboot /usr/bin/redis-server /home/sc1vuxe8870/.redis/redis.conf >/dev/null 2>&1"
( crontab -l 2>/dev/null | grep -v "redis.conf" ; echo "$CRON_CMD" ) | crontab - 2>/dev/null || true
echo "[+] Cron automatique @reboot configuré."

echo "=========================================================="
echo "    REDIS EST PRÊT ET ACTIF EN CACHE RAM !"
echo "=========================================================="
