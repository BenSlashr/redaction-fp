#!/bin/bash

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Installation des dépendances pour le projet RFP...${NC}"

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 n'est pas installé. Veuillez l'installer avant de continuer.${NC}"
    exit 1
fi

# Vérifier si Node.js est installé
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js n'est pas installé. Veuillez l'installer avant de continuer.${NC}"
    exit 1
fi

# Vérifier si npm est installé
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm n'est pas installé. Veuillez l'installer avant de continuer.${NC}"
    exit 1
fi

# Créer un environnement virtuel Python si nécessaire
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}Création de l'environnement virtuel Python...${NC}"
    cd backend
    python3 -m venv venv
    cd ..
    echo -e "${GREEN}Environnement virtuel créé avec succès.${NC}"
else
    echo -e "${GREEN}L'environnement virtuel existe déjà.${NC}"
fi

# Activer l'environnement virtuel et installer les dépendances backend
echo -e "${YELLOW}Installation des dépendances backend...${NC}"
cd backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Vérifier si les variables d'environnement sont configurées
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Création du fichier .env...${NC}"
    cat > .env << EOL
OPENAI_API_KEY=your_openai_api_key_here
VALUESERP_API_KEY=your_valueserp_api_key_here
THOT_API_KEY=your_thot_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
LOG_LEVEL=INFO
EOL
    echo -e "${GREEN}Fichier .env créé. Veuillez le modifier avec vos clés API.${NC}"
else
    # Vérifier si la variable GOOGLE_API_KEY existe déjà dans le fichier .env
    if ! grep -q "GOOGLE_API_KEY" .env; then
        echo -e "${YELLOW}Ajout de GOOGLE_API_KEY au fichier .env...${NC}"
        echo "GOOGLE_API_KEY=your_google_api_key_here" >> .env
        echo -e "${GREEN}GOOGLE_API_KEY ajouté au fichier .env. Veuillez le modifier avec votre clé API Google.${NC}"
    fi
fi

deactivate
cd ..

# Installer les dépendances frontend
echo -e "${YELLOW}Installation des dépendances frontend...${NC}"
cd frontend
npm install --legacy-peer-deps

# Vérifier si les variables d'environnement sont configurées
if [ ! -f ".env.local" ]; then
    echo -e "${YELLOW}Création du fichier .env.local...${NC}"
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
    echo -e "${GREEN}Fichier .env.local créé.${NC}"
fi

cd ..

echo -e "${GREEN}Installation terminée avec succès!${NC}"
echo -e "${YELLOW}Pour démarrer le backend:${NC}"
echo -e "cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo -e "${YELLOW}Pour démarrer le frontend:${NC}"
echo -e "cd frontend && npm run dev"
echo -e "${YELLOW}N'oubliez pas de configurer vos clés API dans le fichier backend/.env${NC}"
