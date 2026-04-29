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

    def _get_metrics_dict(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """Extrae las 3 métricas principales de forma inteligente y sin repetir columnas."""
        defaults = {"ingresos": 10000.0, "poblacion": 5000.0, "competencia": 10.0}
        if not metrics:
            return defaults
            
        normalized = {str(k).upper(): v for k, v in metrics.items()}
        
        # 1. Palabras que ignoramos SOLO si la columna se llama EXACTAMENTE así
        blacklist_exact = ["AÑO", "YEAR", "ID", "CODIGO", "CODE", "CONSECUTIVO"]
        
        # 2. Definir prioridades de búsqueda (Sinónimos)
        search_patterns = [
            ("ingresos", ["INGRESOS", "GANANCIAS", "REVENUE", "VENTAS", "MONTO", "VALOR"]),
            ("poblacion", ["POBLACION", "HABITANTES", "PERSONAS", "CANTIDAD", "VIVIENDAS", "TOTAL", "TERMINADAS"]),
            ("competencia", ["COMPETENCIA", "EMPRESAS", "RIVALES", "STORES", "NEGOCIOS"])
        ]
        
        results = {}
        used_keys = set()
        
        def clean_val(v):
            """Limpia strings como '4,279' o '1.500,50' a float"""
            s = str(v).replace('"', '').replace(" ", "").strip()
            # Caso común en CSV: 4,279 -> 4279
            if "," in s and "." not in s: s = s.replace(",", "")
            # Caso: 1.234,56 -> 1234.56
            elif "." in s and "," in s: s = s.replace(".", "").replace(",", ".")
            return float(s)

        # Fase A: Buscar por nombres específicos
        for metric_name, synonyms in search_patterns:
            for s in synonyms:
                # Buscamos si el sinónimo está contenido en alguna llave del CSV
                for k in normalized.keys():
                    if s in k and k not in used_keys and k not in blacklist_exact:
                        try:
                            results[metric_name] = clean_val(normalized[k])
                            used_keys.add(k)
                            break
                        except: continue
                if metric_name in results: break
        
        # Fase B: Rellenar con cualquier columna numérica sobrante
        available_numeric_cols = []
        for k, v in normalized.items():
            if k not in used_keys and k not in blacklist_exact:
                try:
                    f_val = clean_val(v)
                    # Ignorar si es un año puro (ej: 2023) y la columna es corta
                    if 1900 <= f_val <= 2100 and len(k) <= 5:
                        continue
                    available_numeric_cols.append(f_val)
                except: continue

        for metric_name in ["ingresos", "poblacion", "competencia"]:
            if metric_name not in results:
                if available_numeric_cols:
                    results[metric_name] = available_numeric_cols.pop(0)
                else:
                    results[metric_name] = defaults[metric_name]
                    
        return results

    async def calculate_comparison_scores(self, dataset_id: str, zone_codes: List[str], db: Session) -> List[Dict[str, Any]]:
        """Calcula el score final para la tabla/radar combinando la BD y Transformación"""
        if not zone_codes or len(zone_codes) < 2:
            raise ValueError("Se requieren al menos 2 zonas para comparar.")
            
        zones_data = await self.fetch_zone_data(zone_codes)
        
        # 1. Intentar buscar el Score Real en la Base de Datos
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
        
        # 2. Ensamblar los datos con la nueva lógica inteligente
        raw_results = []
        for zone in zones_data:
            metrics_dict = self._get_metrics_dict(zone.get("metrics", {}))
            zone_name = zone.get("name", "Zona desconocida")
            score_final = real_scores.get(zone_name)
            
            if score_final is None:
                score_final = (metrics_dict["ingresos"] * 0.05) + (metrics_dict["poblacion"] * 0.03) - (metrics_dict["competencia"] * 2)
                score_final = max(0, min(100, score_final / 100))
            
            raw_results.append({
                "zone_name": zone_name,
                "ingresos": metrics_dict["ingresos"],
                "poblacion": metrics_dict["poblacion"],
                "competencia": metrics_dict["competencia"],
                "score_final": round(score_final, 2)
            })

        # 3. NORMALIZACIÓN para el Radar (Escala 0-100)
        # Buscamos los máximos de cada categoría para escalar
        max_vals = {
            "ingresos": max([r["ingresos"] for r in raw_results] + [1]),
            "poblacion": max([r["poblacion"] for r in raw_results] + [1]),
            "competencia": max([r["competencia"] for r in raw_results] + [1]),
            "score_final": max([r["score_final"] for r in raw_results] + [1])
        }

        final_results = []
        for r in raw_results:
            final_results.append({
                **r,
                "zone_code": r["zone_name"],
                # Estos campos son los que usará el Radar para verse "equilibrado"
                "ingresos_norm": round((r["ingresos"] / max_vals["ingresos"]) * 100, 2),
                "poblacion_norm": round((r["poblacion"] / max_vals["poblacion"]) * 100, 2),
                "competencia_norm": round((r["competencia"] / max_vals["competencia"]) * 100, 2),
                "score_norm": round((r["score_final"] / max_vals["score_final"]) * 100, 2)
            })
            
        return final_results
