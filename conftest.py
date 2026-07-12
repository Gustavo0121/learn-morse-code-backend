"""Fixtures compartilhadas de toda a suíte."""

from collections.abc import Iterator

import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def _isolated_cache(settings) -> Iterator[None]:
    """Usa cache em memória e o limpa a cada teste.

    O rate limiting (throttle) guarda contadores no cache default; sem isso os
    testes dependeriam do Redis local e vazariam estado entre execuções.
    """
    settings.CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    }
    cache.clear()
    yield
    cache.clear()
