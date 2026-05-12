import pandas as pd
import json

# ── Chargement ───────────────────────────────────────────────────────
ships = pd.read_csv("data/raw/ships_large.csv")
scores = pd.read_csv("data/processed/risk_scores.csv")
anomalies = pd.read_csv("data/processed/anomalies_detected.csv")
predictions = pd.read_csv("data/processed/trajectory_predictions.csv")

# ── Construction du JSON final ───────────────────────────────────────
output = []

for _, ship in ships.iterrows():
    mmsi = ship["mmsi"]

    # Score et niveau de risque
    score_row = scores[scores["mmsi"] == mmsi]
    risk_score = float(score_row["risk_score"].values[0]) if not score_row.empty else 0
    risk_level = score_row["risk_level"].values[0] if not score_row.empty else "LOW"

    # Anomalies du navire
    ship_anomalies = anomalies[anomalies["mmsi"] == mmsi][["type", "confidence", "timestamp"]].to_dict(orient="records")

    # Prédiction de trajectoire
    pred_row = predictions[predictions["mmsi"] == mmsi]
    if not pred_row.empty:
        predicted_destination = pred_row["predicted_destination"].values[0]
        eta_days = pred_row["eta_days"].values[0]
        confidence = float(pred_row["confidence"].values[0])
    else:
        predicted_destination = None
        eta_days = None
        confidence = None

    output.append({
        "mmsi": int(mmsi),
        "name": ship["name"],
        "flag": ship["flag"],
        "type": ship["type"],
        "risk_score": risk_score,
        "risk_level": risk_level,
        "anomalies": ship_anomalies,
        "predicted_destination": {
            "port": predicted_destination,
            "eta_days": float(eta_days) if eta_days else None,
            "confidence": confidence
        }
    })

# ── Export JSON ──────────────────────────────────────────────────────
with open("outputs/ships_final.json", "w") as f:
    json.dump(output, f, indent=2, default=str)

# ── Validation ───────────────────────────────────────────────────────
print(f"✅ {len(output)} navires exportés dans outputs/ships_final.json")

high = sum(1 for s in output if s["risk_level"] == "HIGH")
medium = sum(1 for s in output if s["risk_level"] == "MEDIUM")
low = sum(1 for s in output if s["risk_level"] == "LOW")

print(f"\nDistribution finale :")
print(f"  HIGH   : {high}")
print(f"  MEDIUM : {medium}")
print(f"  LOW    : {low}")

# Exemple d'un navire HIGH risk
high_ships = [s for s in output if s["risk_level"] == "HIGH"]
if high_ships:
    print(f"\nExemple navire HIGH risk :")
    example = high_ships[0]
    print(f"  MMSI      : {example['mmsi']}")
    print(f"  Nom       : {example['name']}")
    print(f"  Pavillon  : {example['flag']}")
    print(f"  Score     : {example['risk_score']}")
    print(f"  Anomalies : {len(example['anomalies'])}")
    print(f"  Destination prédite : {example['predicted_destination']['port']}")