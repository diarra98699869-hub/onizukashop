#!/bin/bash
# ==============================================================================
# Script de Déploiement Automatique 1-Clic pour ONIZUKA SHOP sur o2switch
# Domaine : onizukashop.com
# ==============================================================================

set -e

echo "=========================================================="
echo "    DÉPLOIEMENT ONIZUKA SHOP (o2switch / cPanel)"
echo "=========================================================="

APP_DIR="/home/sc1vuxe8870/repositories/onizukashop"
VENV_DIR="/home/sc1vuxe8870/virtualenv/repositories/onizukashop/3.12"

cd "$APP_DIR" || exit 1

echo ">>> [1/7] Récupération du code et des assets depuis GitHub..."
git pull origin main

echo ">>> [2/7] Configuration de l'environnement (.env)..."
if [ ! -f .env ]; then
    cp .env.production .env
    echo "Fichier .env initialisé depuis .env.production."
fi

echo ">>> [3/7] Activation de l'environnement virtuel Python..."
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
elif [ -d "/home/sc1vuxe8870/virtualenv/repositories/onizukashop/3.11" ]; then
    source "/home/sc1vuxe8870/virtualenv/repositories/onizukashop/3.11/bin/activate"
elif [ -f "../virtualenv/bin/activate" ]; then
    source "../virtualenv/bin/activate"
fi

echo ">>> [4/7] Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo ">>> [5/7] Application des migrations PostgreSQL..."
python manage.py migrate --noinput

echo ">>> [6/7] Chargement des données du catalogue..."
python manage.py loaddata fixtures/demo_data.json || echo "Note : Fixtures déjà chargées ou sautées."

echo ">>> [7/7] Collecte des fichiers statiques (CSS, JS, images)..."
python manage.py collectstatic --noinput

echo ">>> Redémarrage de l'application WSGI Phusion Passenger..."
mkdir -p tmp
touch tmp/restart.txt

echo "=========================================================="
echo "    DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !"
echo "    Boutique : https://onizukashop.com"
echo "    ERP Direction : https://onizukashop.com/gestion/"
echo "=========================================================="
