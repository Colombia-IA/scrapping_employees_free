"""
Scraper para Tecoloco.com - Empleos en Centroamerica

Sitios soportados:
- tecoloco.com.ni (Nicaragua)
- tecoloco.com.gt (Guatemala)
- tecoloco.com.sv (El Salvador)
- tecoloco.com.hn (Honduras)
- tecoloco.com (Costa Rica)
"""

import re
import time
import random
from typing import Optional
from datetime import datetime

import httpx
from bs4 import BeautifulSoup


# Dominios por pais
TECOLOCO_DOMINIOS = {
    "nicaragua": "www.tecoloco.com.ni",
    "guatemala": "www.tecoloco.com.gt",
    "el salvador": "www.tecoloco.com.sv",
    "honduras": "www.tecoloco.com.hn",
    "costa rica": "www.tecoloco.com",
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


def get_random_headers() -> dict:
    """Genera headers aleatorios para evitar bloqueos."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


def buscar_tecoloco(
    cargo: str,
    pais: str,
    ciudad: str = "",
    cantidad: int = 20
) -> list[dict]:
    """
    Busca empleos en Tecoloco.

    Args:
        cargo: Cargo o puesto a buscar
        pais: Pais (nicaragua, guatemala, el salvador, honduras, costa rica)
        ciudad: Ciudad especifica (opcional)
        cantidad: Numero maximo de resultados

    Returns:
        Lista de ofertas encontradas
    """
    pais_lower = pais.lower().strip()

    # Obtener dominio
    dominio = TECOLOCO_DOMINIOS.get(pais_lower)
    if not dominio:
        print(f"  Tecoloco: Pais '{pais}' no soportado")
        return []

    # Construir URL de busqueda
    cargo_url = cargo.lower().replace(" ", "-")
    url = f"https://{dominio}/empleos?q={cargo_url}"

    if ciudad:
        url += f"&ubicacion={ciudad.lower()}"

    print(f"  Tecoloco ({pais}): Buscando '{cargo}'...")

    empleos = []

    try:
        # Delay aleatorio para evitar bloqueos
        time.sleep(random.uniform(1, 3))

        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.get(url, headers=get_random_headers())
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Buscar contenedores de ofertas
            # Tecoloco usa diferentes estructuras, intentamos varias
            ofertas = soup.find_all("a", href=re.compile(r"/\d+/.*\.aspx"))

            seen_links = set()

            for oferta in ofertas[:cantidad * 2]:  # Obtener mas para filtrar
                try:
                    href = oferta.get("href", "")

                    # Evitar duplicados
                    if href in seen_links or not href:
                        continue
                    seen_links.add(href)

                    # Construir link completo
                    link = f"https://{dominio}{href}" if href.startswith("/") else href

                    # Extraer titulo
                    titulo = oferta.get_text(strip=True)
                    if not titulo or len(titulo) < 3:
                        continue

                    # Limpiar titulo (remover texto extra)
                    titulo = re.sub(r"\s+", " ", titulo)

                    # Buscar empresa y ubicacion en elementos cercanos
                    parent = oferta.find_parent(["div", "li", "article"])
                    empresa = "No especificada"
                    ubicacion = ciudad if ciudad else pais

                    if parent:
                        # Buscar texto que parezca empresa
                        texto_parent = parent.get_text(" ", strip=True)
                        # Buscar ubicacion
                        ubicacion_match = re.search(
                            r"(Managua|Guatemala|San Salvador|Tegucigalpa|San José|"
                            r"León|Matagalpa|Chinandega|Masaya|Granada|Estelí|Jinotega|"
                            r"Chontales|Rivas|Carazo|Boaco|Madriz|Nueva Segovia|"
                            r"Río San Juan|RAAN|RAAS|Nicaragua|Guatemala|Honduras|"
                            r"El Salvador|Costa Rica)",
                            texto_parent,
                            re.IGNORECASE
                        )
                        if ubicacion_match:
                            ubicacion = ubicacion_match.group(0)

                    empleo = {
                        "titulo": titulo[:100],
                        "empresa": empresa,
                        "ubicacion": f"{ubicacion}, {pais.title()}",
                        "link": link,
                        "fuente": "Tecoloco",
                        "descripcion": "",
                    }

                    empleos.append(empleo)

                    if len(empleos) >= cantidad:
                        break

                except Exception as e:
                    continue

        print(f"  Tecoloco: {len(empleos)} ofertas encontradas")

    except httpx.HTTPStatusError as e:
        print(f"  Tecoloco: Error HTTP {e.response.status_code}")
    except httpx.RequestError as e:
        print(f"  Tecoloco: Error de conexion - {e}")
    except Exception as e:
        print(f"  Tecoloco: Error - {e}")

    return empleos


def paises_soportados() -> list[str]:
    """Retorna lista de paises soportados por Tecoloco."""
    return list(TECOLOCO_DOMINIOS.keys())


if __name__ == "__main__":
    # Test
    print("=== Test Tecoloco ===\n")

    empleos = buscar_tecoloco("marketing", "nicaragua", cantidad=5)

    for i, emp in enumerate(empleos, 1):
        print(f"\n{i}. {emp['titulo']}")
        print(f"   Ubicacion: {emp['ubicacion']}")
        print(f"   Link: {emp['link']}")
