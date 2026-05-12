import pandas as pd
import numpy as np

# ── Chargement ───────────────────────────────────────────────────────
ais = pd.read_csv("data/raw/ais_data_large.csv")
ships = pd.read_csv("data/raw/ships_large.csv")
scores = pd.read_csv("data/processed/risk_scores.csv")

ais["timestamp"] = pd.to_datetime(ais["timestamp"])
ais = ais.sort_values(["mmsi", "timestamp"])

# ── On travaille uniquement sur les navires HIGH risk ────────────────
high_risk = scores[scores["risk_level"] == "HIGH"]["mmsi"].tolist()
ais_high = ais[ais["mmsi"].isin(high_risk)]

# ── Ports principaux (base de référence) ────────────────────────────
major_ports = {
    "Rotterdam":    (51.9, 4.5),
    "Singapore":    (1.3, 103.8),
    "Shanghai":     (31.2, 121.5),
    "Houston":      (29.7, -95.4),
    "Dubai":        (25.2, 55.3),
    "Marseille":    (43.3, 5.4),
    "New York":     (40.7, -74.0),
    "Tokyo":        (35.7, 139.8),
    "Los Angeles":  (33.7, -118.2),
    "Hamburg":      (53.5, 10.0),
}

def nearest_port(lat, lon):
    """Retourne le port le plus proche et la distance en km"""
    min_dist = float("inf")
    nearest = None
    for port, (plat, plon) in major_ports.items():
        dist = np.sqrt((lat - plat)**2 + (lon - plon)**2) * 111
        if dist < min_dist:
            min_dist = dist
            nearest = port
    return nearest, round(min_dist)

def estimate_eta(distance_km, speed_knots):
    """Estime l'ETA en jours"""
    if speed_knots <= 0:
        return None
    speed_kmh = speed_knots * 1.852
    eta_hours = distance_km / speed_kmh
    return round(eta_hours / 24, 1)

# ── Prédiction par navire ────────────────────────────────────────────
predictions = []

for mmsi, group in ais_high.groupby("mmsi"):
    group = group.sort_values("timestamp")
    last = group.iloc[-1]

    lat = last["latitude"]
    lon = last["longitude"]
    speed = last["speed"] if last["speed"] > 0 else group["speed"].mean()
    heading = last["course"]

    # Port déclaré dans ships
    ship_info = ships[ships["mmsi"] == mmsi]
    declared_dest = ship_info["destination"].values[0] if not ship_info.empty else "Unknown"

    # Port prédit par proximité + cap
    predicted_port, dist_km = nearest_port(lat, lon)
    eta = estimate_eta(dist_km, speed)
    
    # Niveau de confiance basé sur la cohérence cap/destination
    confidence = 0.7 if declared_dest == predicted_port else 0.5

    predictions.append({
        "mmsi": mmsi,
        "last_lat": round(lat, 4),
        "last_lon": round(lon, 4),
        "speed_knots": round(speed, 1),
        "heading": heading,
        "declared_destination": declared_dest,
        "predicted_destination": predicted_port,
        "distance_to_port_km": dist_km,
        "eta_days": eta,
        "confidence": confidence
    })

# ── Export ───────────────────────────────────────────────────────────
df_pred = pd.DataFrame(predictions)
df_pred.to_csv("data/processed/trajectory_predictions.csv", index=False)

print(f"✅ {len(df_pred)} prédictions générées")
print(f"\nDestinations prédites les plus fréquentes:")
print(df_pred["predicted_destination"].value_counts().head(5))
print(f"\nETA moyen : {df_pred['eta_days'].mean():.1f} jours")
print(f"Confiance moyenne : {df_pred['confidence'].mean():.2f}")