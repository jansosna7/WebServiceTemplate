import asyncio
from typing import Callable, Any, Dict, List

class EventBus:
    """
    Prosty asynchroniczny system zdarzen pozwalajacy na 
    komunikacje miedzy modulami bez ich sztywnego laczenia.
    """
    def __init__(self):
        # Slownik przechowujacy listy funkcji obslugujacych dane zdarzenie
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        """Rejestruje funkcje (handler) dla danego typu zdarzenia."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    async def publish(self, event_type: str, data: Any):
        """
        Publikuje zdarzenie. Wszystkie zarejestrowane funkcje 
        zostana wywolane asynchronicznie w tle.
        """
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                # Wywolanie handlera jako zadanie asyncio (Background Task)[cite: 10]
                asyncio.create_task(handler(data))

# Globalna instancja dostepna dla wszystkich modulow
event_bus = EventBus()
