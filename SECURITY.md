# 🔒 Security Policy
## Marine Nationale Hackathon — Ghost Fleet Detection

## ⚠️ Données sensibles — NE JAMAIS pusher sur GitHub
- Fichiers CSV bruts (données navires)
- Clés API (AISHub, Marine Traffic)
- Tokens GitHub
- Données personnelles
- Coordonnées GPS réelles de navires militaires

## ✅ Ce qui est autorisé sur GitHub
- Scripts Python
- Fichiers JSON mock (données fictives)
- Documentation
- README et guides

## 🔑 Gestion des clés API
- Toujours stocker dans un fichier `.env`
- Le fichier `.env` est dans le `.gitignore`
- Ne jamais écrire une clé directement dans le code

## 📋 En cas de fuite de données
1. Prévenir immédiatement Person 4 (DevOps)
2. Révoquer le token ou la clé compromise
3. Supprimer le commit problématique

## 👥 Contact sécurité
Person 4 — DevOps & Validation
cdurand@albertschool.com
