# 🎯 Demo Script — Ghost Fleet Detection
## Marine Nationale Hackathon — Mai 2026

## Introduction (30 secondes)
"Bonjour, nous sommes l'équipe Sujet 3.
Notre système détecte les navires suspects
en croisant données AIS, signatures radio
et sanctions OFAC en temps réel."

## Live Demo (3 minutes)

### 🔴 Navire 1 — Pétrolier Iranien (OFAC)
- Zoomer sur le Golfe Persique
- Cliquer sur navire rouge HIGH risk
- Montrer : AIS désactivé depuis 24h
- Montrer : statut OFAC = true
- Montrer : destination prédite = Bandar Abbas
- Dire : "Ce navire transporte du pétrole
  sous sanctions iraniennes"

### 🔴 Navire 2 — Changement de cap suspect
- Zoomer sur Méditerranée
- Cliquer sur navire rouge HIGH risk
- Montrer : anomalie Course Anomaly
- Montrer : trajectoire bizarre sur la carte
- Dire : "Ce navire a changé de cap
  brutalement 3 fois en 24h"

### 🔴 Navire 3 — Faux pavillon
- Zoomer sur Mer Rouge
- Cliquer sur navire rouge HIGH risk
- Montrer : anomalie Fake Flag
- Montrer : pavillon Panama mais signature
  radio typique Libéria
- Dire : "Ce navire usurpe son identité"

## Conclusion (30 secondes)
- Montrer les filtres HIGH risk + OFAC
- Dire : "Notre pipeline est 100% OSINT,
  open-source, et transposable
  dans votre environnement"
