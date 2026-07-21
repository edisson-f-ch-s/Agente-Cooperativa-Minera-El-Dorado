"""
Limitador de peticiones en memoria para proteger la cuota gratuita de Gemini
durante la evaluación del challenge (uso compartido por evaluadores/estudiantes).
"""
import os
import time
from collections import deque


def _parse_limit(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default)).strip()
    try:
        return max(0, int(raw))
    except ValueError:
        return default


class RateLimiter:
    """Ventana deslizante por minuto y contador diario (UTC)."""

    def __init__(self, rpm: int, rpd: int) -> None:
        self.rpm = rpm
        self.rpd = rpd
        self._minute_window: deque[float] = deque()
        self._day_count = 0
        self._day_start = self._current_day()

    @staticmethod
    def _current_day() -> int:
        return int(time.time() // 86400)

    def _reset_day_if_needed(self) -> None:
        today = self._current_day()
        if today != self._day_start:
            self._day_start = today
            self._day_count = 0

    def check(self) -> tuple[bool, str | None]:
        """
        Devuelve (permitido, mensaje_de_error).
        Si rpm=0 y rpd=0, no aplica límites.
        """
        if self.rpm == 0 and self.rpd == 0:
            return True, None

        now = time.time()
        self._reset_day_if_needed()

        if self.rpd > 0 and self._day_count >= self.rpd:
            return False, (
                "Límite diario de consultas alcanzado. "
                "El servicio estará disponible mañana o puede desplegar con su propia clave de API."
            )

        if self.rpm > 0:
            while self._minute_window and self._minute_window[0] <= now - 60:
                self._minute_window.popleft()
            if len(self._minute_window) >= self.rpm:
                return False, (
                    "Demasiadas consultas en poco tiempo. "
                    "Espere un minuto e intente de nuevo."
                )

        if self.rpm > 0:
            self._minute_window.append(now)
        if self.rpd > 0:
            self._day_count += 1

        return True, None


def get_rate_limiter() -> RateLimiter:
    """Singleton del limitador configurado por entorno."""
    if not hasattr(get_rate_limiter, "_instance"):
        rpm = _parse_limit("RATE_LIMIT_RPM", 8)
        rpd = _parse_limit("RATE_LIMIT_RPD", 400)
        get_rate_limiter._instance = RateLimiter(rpm=rpm, rpd=rpd)
    return get_rate_limiter._instance
