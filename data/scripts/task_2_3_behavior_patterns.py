import pandas as pd
import numpy as np

# ── Chargement ───────────────────────────────────────────────────────
ais = pd.read_csv("data/raw/ais_data_large.csv")
ais["timestamp"] = pd.to_datetime(ais["timestamp"])
ais = ais.sort_values(["mmsi", "timestamp"])

patterns = []

for mmsi, group in ais.groupby("mmsi"):
    group = group.sort_values("timestamp").reset_index(drop=True)

    # ── 1. Comportement convoi : plusieurs navires se déplacent ensemble
    # On détecte si un navire a des positions très proches d'un autre
    # (traité globalement après la boucle)

    # ── 2. Dead zone : AIS éteint dans une zone spécifique ───────────
    group["time_diff"] = group["timestamp"].diff().dt.total_seconds() / 3600
    dead_zones = group[
        (group["time_diff"] > 12) &
        (group["status"] != "At Anchor") &
        (group["status"] != "Moored")
    ]
    if len(dead_zones) > 0:
        for _, row in dead_zones.iterrows():
            patterns.append({
                "mmsi": mmsi,
                "pattern_type": "Dead Zone",
                "detail": f"AIS éteint pendant {round(row['time_diff'], 1)}h à lat={round(row['latitude'], 2)}, lon={round(row['longitude'], 2)}",
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "timestamp": str(row["timestamp"])
            })

    # ── 3. Changement de cap brutal : virage > 90° ───────────────────
    group["course_diff"] = group["course"].diff().abs()
    group["course_diff"] = group["course_diff"].apply(lambda x: min(x, 360 - x) if pd.notna(x) else np.nan)
    sharp_turns = group[group["course_diff"] > 90]
    for _, row in sharp_turns.iterrows():
        patterns.append({
            "mmsi": mmsi,
            "pattern_type": "Sharp Turn",
            "detail": f"Changement de cap de {round(row['course_diff'], 1)}° détecté",
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "timestamp": str(row["timestamp"])
        })

# ── 4. Comportement convoi : navires proches au même moment ──────────
ais_snapshot = ais.copy()
ais_snapshot["lat_round"] = ais_snapshot["latitude"].round(0)
ais_snapshot["lon_round"] = ais_snapshot["longitude"].round(0)
ais_snapshot["time_round"] = ais_snapshot["timestamp"].dt.floor("24h")

convoy = ais_snapshot.groupby(["lat_round", "lon_round", "time_round"])["mmsi"].nunique().reset_index()
convoy = convoy[convoy["mmsi"] > 1]

for _, row in convoy.iterrows():
    patterns.append({
        "mmsi": "MULTIPLE",
        "pattern_type": "Convoy",
        "detail": f"{row['mmsi']} navires détectés ensemble à lat={row['lat_round']}, lon={row['lon_round']}",
        "latitude": row["lat_round"],
        "longitude": row["lon_round"],
        "timestamp": str(row["time_round"])
    })

# ── Export ───────────────────────────────────────────────────────────
df_patterns = pd.DataFrame(patterns)
df_patterns.to_csv("data/processed/behavior_patterns.csv", index=False)

print(f"✅ {len(df_patterns)} patterns détectés")
print(df_patterns["pattern_type"].value_counts())

# ── Fusion avec anomalies existantes ─────────────────────────────────
existing = pd.read_csv("data/processed/anomalies_detected.csv")

new_anomalies = df_patterns[df_patterns["pattern_type"] != "Convoy"][["mmsi", "pattern_type", "timestamp"]].copy()
new_anomalies = new_anomalies[new_anomalies["mmsi"] != "MULTIPLE"]
new_anomalies["mmsi"] = new_anomalies["mmsi"].astype(int)
new_anomalies.columns = ["mmsi", "type", "timestamp"]
new_anomalies["confidence"] = 0.75
new_anomalies["detail"] = "Pattern comportemental détecté"

all_anomalies = pd.concat([existing, new_anomalies], ignore_index=True)
all_anomalies.to_csv("data/processed/anomalies_detected.csv", index=False)

print(f"\n✅ Anomalies avant : {len(existing)}")
print(f"✅ Nouvelles anomalies ajoutées : {len(new_anomalies)}")
print(f"✅ Total anomalies : {len(all_anomalies)}")