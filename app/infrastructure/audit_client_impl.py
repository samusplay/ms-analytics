import os
import httpx
from datetime import datetime

from app.domain.repository.audit_client_port import AuditClientPort

AUDIT_API_URL = os.getenv("MS_AUDITORIA_URL", "http://ms-auditoria:8000")

class AuditClientImpl(AuditClientPort):
    """
    Adaptador de Infraestructura: Implementa el envío de eventos de auditoría
    a través de peticiones HTTP REST usando httpx.
    """
    
    async def send_event(self, event_type: str, reference_id: str, summary: str, trace_id: str) -> None:
        url = f"{AUDIT_API_URL}/api/v1/events"
        payload = {
            "event_type": event_type,
            "service_name": "ms-analytics",
            "reference_id": str(reference_id),
            "event_summary": summary,
            "trace_id": trace_id
        }
        
        try:
            async with httpx.AsyncClient() as client:
                await client.post(url, json=payload, timeout=5.0)
        except Exception as e:
            print(f"⚠️ Error enviando evento a auditoría: {e}")

    async def send_calculation_event(self, trace_id: str, estado: str, summary: str) -> None:
        url = f"{AUDIT_API_URL}/api/v1/events"
        payload = {
            "trace_id": trace_id,
            "service_name": "ms-analytics",
            "estado": estado,
            "event_summary": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            async with httpx.AsyncClient() as client:
                await client.post(url, json=payload, timeout=5.0)
        except Exception as e:
            print(f"⚠️ Error enviando evento a auditoría (Cálculo): {e}")

    async def send_operation_event(self, status: str, summary: str) -> None:
        url = f"{AUDIT_API_URL}/audit/events"
        payload = {
            "service_name": "ms-analytics",
            "execution_status": status,
            "event_summary": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            async with httpx.AsyncClient() as client:
                await client.post(url, json=payload, timeout=5.0)
        except Exception as e:
            print(f"⚠️ Error enviando evento a auditoría (Operación): {e}")
