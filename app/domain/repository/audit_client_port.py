from abc import ABC, abstractmethod

class AuditClientPort(ABC):
    """
    Puerto de Dominio: Define los métodos requeridos para emitir eventos de auditoría,
    independientemente de la tecnología subyacente.
    """
    
    @abstractmethod
    async def send_event(self, event_type: str, reference_id: str, summary: str, trace_id: str) -> None:
        """Emite un evento de auditoría de forma asíncrona."""
        pass
