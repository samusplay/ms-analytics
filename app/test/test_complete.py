# test_complete.py
import requests
import psycopg2
import json

BASE_URL = "http://localhost:8000"

# 1. Probar endpoint de scoring
print("=== 1. Ejecutando Scoring ===")
response = requests.post(
    f"{BASE_URL}/api/v1/analytics/internal/sync/100",
    headers={"Content-Type": "application/json"},
    json={
        "data": [
            {
                "zone_code": "Z001",
                "zone_name": "Zona Norte",
                "region": "Norte",
                "metrics": {
                    "poblacion": 1.2,
                    "ingreso": 45000,
                    "educacion": 0.95,
                    "competencia": 0.15
                }
            },
            {
                "zone_code": "Z002",
                "zone_name": "Zona Sur",
                "region": "Sur",
                "metrics": {
                    "poblacion": 0.8,
                    "ingreso": 28000,
                    "educacion": 0.70,
                    "competencia": 0.45
                }
            }
        ]
    }
)

print(f"Status: {response.status_code}")
result = response.json()
print(f"Response: {json.dumps(result, indent=2)}")

if result.get("success"):
    execution_id = result["data"]["execution_id"]
    print(f"\n✅ Ejecución exitosa! ID: {execution_id}")
    
    # 2. Verificar en BD
    print("\n=== 2. Verificando Base de Datos ===")
    conn = psycopg2.connect(
        host="localhost",
        database="ms_analytics",
        user="usuario",
        password="password"
    )
    cur = conn.cursor()
    
    # Verificar score_execution
    cur.execute("SELECT id, dataset_id, status FROM score_execution ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    print(f"ScoreExecution: ID={row[0]}, Dataset={row[1]}, Status={row[2]}")
    
    # Verificar zone_score
    cur.execute("SELECT zone_code, score_value, rank_position FROM zone_score WHERE execution_id=%s", (row[0],))
    zones = cur.fetchall()
    print(f"ZoneScores: {len(zones)} registros")
    for z in zones:
        print(f"  - {z[0]}: score={z[1]}, rank={z[2]}")
    
    # Verificar trace
    cur.execute("SELECT zone_code, LEFT(formula, 50) FROM trace WHERE execution_id=%s", (row[0],))
    traces = cur.fetchall()
    print(f"Traces: {len(traces)} registros")
    for t in traces:
        print(f"  - {t[0]}: {t[1]}...")
    
    cur.close()
    conn.close()
    
    # 3. Consultar resultados por API
    print("\n=== 3. Consultando resultados por API ===")
    results_response = requests.get(f"{BASE_URL}/api/v1/analytics/scoring/results/{execution_id}")
    print(json.dumps(results_response.json(), indent=2))
    
else:
    print(f"❌ Error: {result.get('error')}")

print("\n=== Validación SOLID completa ===")