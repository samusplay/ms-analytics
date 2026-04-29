import httpx
import os
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models import ScoreExecution, ZoneScore

MS_TRANSFORM_URL = os.getenv("MS_TRANSFORM_URL", "http://ms-transform:8000")

class AnalyticsService:
    """USE CASE: Lógica de negocio para Analytics"""

    async def fetch_zone_data(self, zone_codes: List[str]) -> List[Dict[str, Any]]:
        """
        Consulta ms-transform para obtener las métricas reales de las zonas solicitadas.
        Usa el endpoint /zones/metrics?names=ZONA1,ZONA2
        """
        names_param = ",".join(zone_codes)
        url = f"{MS_TRANSFORM_URL}/api/v1/transform/zones/metrics?names={names_param}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                return data.get("data", {}).get("zones", [])
                
            except Exception as e:
                print(f"Error comunicando con ms-transform: {e}")
                raise ValueError("No se pudo obtener la data de las zonas solicitadas.")

    async def calculate_comparison_scores(self, dataset_id: str, zone_codes: List[str], db: Session) -> List[Dict[str, Any]]:
        """Calcula el score final para la tabla/radar combinando la BD y Transformación"""
        if not zone_codes or len(zone_codes) < 2:
            raise ValueError("Se requieren al menos 2 zonas para comparar.")
            
        zones_data = await self.fetch_zone_data(zone_codes)
        
        # 1. Intentar buscar el Score Real en la Base de Datos (ZoneScore)
        real_scores = {}
        try:
            execution = db.query(ScoreExecution).filter(ScoreExecution.dataset_id == dataset_id).first()
            if execution:
                scores = db.query(ZoneScore).filter(
                    ZoneScore.execution_id == execution.id,
                    ZoneScore.zone_code.in_(zone_codes)
                ).all()
                for s in scores:
                    real_scores[s.zone_code] = s.score_value
        except Exception as e:
            print(f"La base de datos aun no tiene scores: {e}")
        
        # 2. Ensamblar los datos para el Frontend
        results = []
        for zone in zones_data:
            metrics = zone.get("metrics", {})
            ingresos = float(metrics.get("INGRESOS", 10000)) if metrics else 10000
            poblacion = float(metrics.get("POBLACION", 5000)) if metrics else 5000
            competencia = float(metrics.get("COMPETENCIA", 10)) if metrics else 10
            
            # ms-transform devuelve {"name": "VALLE", "record_count": 5}
            zone_name = zone.get("name", "Zona desconocida")
            
            # Usamos el Score de la Base de Datos. Si la BD está vacía, lo calculamos:
            if zone_name in real_scores:
                score_final = real_scores[zone_name]
            else:
                score_final = (ingresos * 0.05) + (poblacion * 0.03) - (competencia * 2)
                score_final = max(0, min(100, score_final / 100))
            
            results.append({
                "zone_code": zone_name,   # usamos name como identificador
                "zone_name": zone_name,
                "ingresos": ingresos,
                "poblacion": poblacion,
                "competencia": competencia,
                "score_final": round(score_final, 2)
            })
            
        return results
