"""
Scrapers adicionales para sitios de empleo.

Modulos:
- tecoloco: Empleos en Centroamerica (Nicaragua, Guatemala, El Salvador, Honduras, Costa Rica)
"""

from .tecoloco import buscar_tecoloco, paises_soportados as tecoloco_paises

__all__ = ["buscar_tecoloco", "tecoloco_paises"]
