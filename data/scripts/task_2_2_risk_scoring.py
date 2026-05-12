import pandas as pd

# ── Chargement ───────────────────────────────────────────────────────
ships = pd.read_csv("data/raw/ships_large.csv")
anomalies = pd.read_csv("data/processed/anomalies_detected.csv")

# ── Calcul des composantes ───────────────────────────────────────────
anomaly_count = anomalies.groupby("mmsi").size().reset_index(name="anomaly_count")

ofac = anomalies[anomalies["type"] == "OFAC Listed"][["mmsi"]].drop_duplicates()
ofac["ofac_listed"] = 1

# ── Assemblage ───────────────────────────────────────────────────────
scores = ships[["mmsi"]].copy()
scores = scores.merge(anomaly_count, on="mmsi", how="left")
scores = scores.merge(ofac, on="mmsi", how="left")
scores["anomaly_count"] = scores["anomaly_count"].fillna(0)
scores["ofac_listed"] = scores["ofac_listed"].fillna(0)

# ── Score anomaly_count par paliers ─────────────────────────────────
def anomaly_score(n):
    if n <= 5:
        return 10
    elif n <= 10:
        return 30
    elif n <= 15:
        return 60
    else:
        return 90

scores["score_anomaly"] = scores["anomaly_count"].apply(anomaly_score)

# ── Score OFAC ───────────────────────────────────────────────────────
scores["score_ofac"] = scores["ofac_listed"] * 30

# ── Score final ──────────────────────────────────────────────────────
scores["risk_score"] = (scores["score_anomaly"] + scores["score_ofac"]).clip(upper=100)

# ── Niveaux de risque ────────────────────────────────────────────────
def assign_level(score):
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    else:
        return "LOW"

scores["risk_level"] = scores["risk_score"].apply(assign_level)

# ── Validation ───────────────────────────────────────────────────────
print(scores["risk_level"].value_counts())
print(f"\n✅ Navires HIGH risk : {len(scores[scores['risk_level'] == 'HIGH'])}")
print(f"\nDistribution des scores:")
print(scores["risk_score"].value_counts().sort_index())

# ── Export ───────────────────────────────────────────────────────────
scores.to_csv("data/processed/risk_scores.csv", index=False)
print("\n✅ risk_scores.csv exporté dans data/processed/")