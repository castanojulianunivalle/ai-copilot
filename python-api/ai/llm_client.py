"""
Sprint 5 · HU-06 · AISCOP-41: cliente HTTP del LLM.

Habla el dialecto OpenAI de `/chat/completions`, que es el que exponen el
Hugging Face Router, vLLM, Ollama y Together. Cambiar de proveedor es cambiar
LLM_BASE_URL y LLM_MODEL, sin tocar codigo.

Este modulo solo se ocupa del transporte: construir la peticion, reintentar lo
que vale la pena reintentar y devolver el texto crudo. Interpretar ese texto es
trabajo de `parser.py`.
"""
from __future__ import annotations

import logging
import os
import random
import time
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Reintentables: rate limit y fallos transitorios del proveedor. Un 400 o un 401
# no se reintentan porque volverian a fallar igual y solo gastan la latencia del
# request que tiene esperando al cliente.
_ESTADOS_REINTENTABLES = {408, 429, 500, 502, 503, 504}


class LLMError(RuntimeError):
    """El LLM no pudo responder. Quien llama debe caer al motor de reglas."""


@dataclass(frozen=True)
class RespuestaLLM:
    texto: str
    modelo: str
    latencia_ms: int
    tokens_prompt: int | None = None
    tokens_salida: int | None = None


@dataclass(frozen=True)
class ConfigLLM:
    base_url: str
    api_key: str | None
    modelo: str
    timeout: float
    max_reintentos: int
    temperatura: float
    max_tokens: int
    habilitado: bool

    @classmethod
    def desde_entorno(cls) -> "ConfigLLM":
        return cls(
            base_url=os.getenv("LLM_BASE_URL", "https://router.huggingface.co/v1").rstrip("/"),
            api_key=os.getenv("LLM_API_KEY") or None,
            modelo=os.getenv("LLM_MODEL", "meta-llama/Llama-3.1-8B-Instruct"),
            timeout=float(os.getenv("LLM_TIMEOUT", "20")),
            max_reintentos=int(os.getenv("LLM_MAX_REINTENTOS", "2")),
            temperatura=float(os.getenv("LLM_TEMPERATURA", "0")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "300")),
            # Apagado por defecto: sin la variable puesta el sistema se comporta
            # exactamente como el Semestre 1 y no intenta salir a la red.
            habilitado=os.getenv("LLM_ENABLED", "").lower() in ("1", "true", "yes"),
        )


class ClienteLLM:
    def __init__(self, config: ConfigLLM | None = None, transporte: httpx.BaseTransport | None = None):
        self.config = config or ConfigLLM.desde_entorno()
        # `transporte` existe para poder probar el cliente sin salir a la red.
        self._transporte = transporte

    @property
    def habilitado(self) -> bool:
        return self.config.habilitado

    def _cabeceras(self) -> dict[str, str]:
        cabeceras = {"Content-Type": "application/json"}
        if self.config.api_key:
            cabeceras["Authorization"] = f"Bearer {self.config.api_key}"
        return cabeceras

    def completar(self, sistema: str, usuario: str) -> RespuestaLLM:
        """Envia el par (system, user) y devuelve el texto de la respuesta."""
        if not self.config.habilitado:
            raise LLMError("LLM deshabilitado (LLM_ENABLED no esta activo)")

        cuerpo: dict[str, Any] = {
            "model": self.config.modelo,
            "messages": [
                {"role": "system", "content": sistema},
                {"role": "user", "content": usuario},
            ],
            # Temperatura 0: la clasificacion debe ser reproducible. Si el mismo
            # ticket cambia de categoria entre corridas, la matriz de confusion
            # del Sprint 6 deja de significar algo.
            "temperature": self.config.temperatura,
            "max_tokens": self.config.max_tokens,
            "response_format": {"type": "json_object"},
        }

        inicio = time.perf_counter()
        ultimo_error: Exception | None = None

        for intento in range(self.config.max_reintentos + 1):
            try:
                with httpx.Client(timeout=self.config.timeout, transport=self._transporte) as cliente:
                    respuesta = cliente.post(
                        f"{self.config.base_url}/chat/completions",
                        json=cuerpo,
                        headers=self._cabeceras(),
                    )

                if respuesta.status_code in _ESTADOS_REINTENTABLES:
                    ultimo_error = LLMError(
                        f"HTTP {respuesta.status_code}: {respuesta.text[:200]}"
                    )
                    if intento < self.config.max_reintentos:
                        self._esperar(intento, respuesta)
                        continue
                    raise ultimo_error

                if respuesta.status_code >= 400:
                    raise LLMError(f"HTTP {respuesta.status_code}: {respuesta.text[:200]}")

                return self._extraer(respuesta.json(), inicio)

            except (httpx.TimeoutException, httpx.TransportError) as exc:
                ultimo_error = exc
                if intento < self.config.max_reintentos:
                    self._esperar(intento, None)
                    continue
                raise LLMError(f"Fallo de red hacia el LLM: {exc}") from exc

        raise LLMError(f"LLM sin respuesta tras {self.config.max_reintentos + 1} intentos: {ultimo_error}")

    def _esperar(self, intento: int, respuesta: httpx.Response | None) -> None:
        """Backoff exponencial con jitter. Respeta Retry-After si el proveedor lo manda."""
        if respuesta is not None:
            cabecera = respuesta.headers.get("Retry-After")
            if cabecera:
                try:
                    time.sleep(min(float(cabecera), 10.0))
                    return
                except ValueError:
                    pass
        # El jitter evita que varios tickets creados a la vez reintenten en fase
        # y vuelvan a chocar contra el mismo rate limit.
        espera = min(2**intento * 0.5, 4.0) + random.uniform(0, 0.3)
        time.sleep(espera)

    def _extraer(self, datos: dict[str, Any], inicio: float) -> RespuestaLLM:
        latencia_ms = int((time.perf_counter() - inicio) * 1000)
        try:
            texto = datos["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"Respuesta del LLM con forma inesperada: {str(datos)[:200]}") from exc

        if not texto or not texto.strip():
            raise LLMError("El LLM devolvio contenido vacio")

        uso = datos.get("usage") or {}
        logger.info(
            "LLM %s respondio en %d ms (%s tokens salida)",
            datos.get("model", self.config.modelo),
            latencia_ms,
            uso.get("completion_tokens", "?"),
        )
        return RespuestaLLM(
            texto=texto,
            modelo=datos.get("model") or self.config.modelo,
            latencia_ms=latencia_ms,
            tokens_prompt=uso.get("prompt_tokens"),
            tokens_salida=uso.get("completion_tokens"),
        )
