import pandas as pd
import numpy as np

# ── Chargement des données ──────────────────────────────────────────
ais = pd.read_csv("data/raw/ais_data_large.csv")
ships = pd.read_csv("data/raw/ships_large.csv")

ais["timestamp"] = pd.to_datetime(ais["timestamp"])
ais = ais.sort_values(["mmsi", "timestamp"])

anomalies = []

for mmsi, group in ais.groupby("mmsi"):
    group = group.sort_values("timestamp")

    # ── 1. AIS Disabled : gap > 24h hors port ───────────────────────
    group["time_diff"] = group["timestamp"].diff().dt.total_seconds() / 3600
    gaps = group[
        (group["time_diff"] > 24) &
        (group["status"] != "At Anchor") &
        (group["status"] != "Moored")
    ]
    for _, row in gaps.iterrows():
        anomalies.append({
            "mmsi": mmsi,
            "type": "AIS Disabled",
            "confidence": 0.85,
            "timestamp": str(row["timestamp"]),
            "detail": f"Gap de {round(row['time_diff'], 1)}h détecté"
        })

    # ── 2. Position Jump : distance > 400km en une nuit ─────────────
    group["lat_diff"] = group["latitude"].diff().abs()
    group["lon_diff"] = group["longitude"].diff().abs()
    group["approx_dist"] = np.sqrt(group["lat_diff"]**2 + group["lon_diff"]**2) * 111
    jumps = group[group["approx_dist"] > 400]
    for _, row in jumps.iterrows():
        anomalies.append({
            "mmsi": mmsi,
            "type": "Position Jump",
            "confidence": 0.90,
            "timestamp": str(row["timestamp"]),
            "detail": f"Saut de ~{round(row['approx_dist'])} km détecté"
        })

    # ── 3. Flag Mismatch : fréquence radio vs pays du pavillon ───────
    ship_info = ships[ships["mmsi"] == mmsi]
    if not ship_info.empty:
        flag = str(ship_info["flag"].values[0]).upper()
        if flag in ["RU", "IR", "KP", "VE", "SY"]:
            anomalies.append({
                "mmsi": mmsi,
                "type": "Flag Mismatch",
                "confidence": 0.75,
                "timestamp": str(group["timestamp"].iloc[-1]),
                "detail": f"Pavillon à risque détecté : {flag}"
            })

# ── 4. Cross-reference is_suspicious ────────────────────────────────
if "is_suspicious" in ships.columns:
    suspicious_ships = ships[ships["is_suspicious"] == True]["mmsi"].tolist()
    for mmsi in suspicious_ships:
        anomalies.append({
            "mmsi": mmsi,
            "type": "OFAC Listed",
            "confidence": 1.0,
            "timestamp": "N/A",
            "detail": "Navire marqué comme suspect (is_suspicious)"
        })

# ── 5. Flag Mismatch : fréquence radio vs pavillon ──────────────────
radio = pd.read_csv("data/raw/radio_signatures_large.csv")

# Plages de fréquences attendues par pavillon (MHz)
flag_freq_ranges = {
    "Denmark":          (156.0, 158.0),
    "Singapore":        (156.5, 159.0),
    "France":           (156.0, 158.0),
    "Marshall Islands": (157.0, 160.0),
    "China":            (157.5, 161.0),
    "Panama":           (158.0, 161.0),
    "USA":              (156.0, 158.5),
    "Malta":            (156.5, 159.5),
    "Bahamas":          (158.0, 162.0),
    "Liberia":          (157.5, 161.0),
}

for _, ship in ships.iterrows():
    mmsi = ship["mmsi"]
    flag = str(ship["flag"])

    if flag not in flag_freq_ranges:
        continue

    ship_signals = radio[radio["mmsi"] == mmsi]
    if ship_signals.empty:
        continue

    avg_freq = ship_signals["frequency"].mean()
    expected_min, expected_max = flag_freq_ranges[flag]

    if not (expected_min <= avg_freq <= expected_max):
        anomalies.append({
            "mmsi": mmsi,
            "type": "Flag Mismatch",
            "confidence": 0.80,
            "timestamp": str(ship_signals["timestamp"].iloc[-1]),
            "detail": f"Frequence moyenne {round(avg_freq, 2)} MHz incoherente avec pavillon {flag}"
        })

# ── Export ───────────────────────────────────────────────────────────
df_anomalies = pd.DataFrame(anomalies)
df_anomalies.to_csv("data/processed/anomalies_detected.csv", index=False)

print(f"✅ {len(df_anomalies)} anomalies détectées")
print(df_anomalies["type"].value_counts())