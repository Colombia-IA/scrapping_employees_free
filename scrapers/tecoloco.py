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
from urllib.parse import quote_plus

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

    # Construir URL de busqueda con encoding correcto
    cargo_encoded = quote_plus(cargo)
    url = f"https://{dominio}/empleos?q={cargo_encoded}&PerPage=40"

    print(f"  Tecoloco ({pais}): Buscando '{cargo}'...")

    empleos = []
    cargo_lower = cargo.lower()

    # Sinonimos comunes para mejorar busqueda
    sinonimos = {
        "marketing": ["marketing", "mercadeo", "marca", "publicidad", "brand", "digital"],
        "ventas": ["ventas", "vendedor", "comercial", "asesor comercial", "ejecutivo de ventas"],
        "contabilidad": ["contabilidad", "contable", "contador", "contadora", "finanzas"],
        "administracion": ["administracion", "administrativo", "administrativa", "admin"],
        "sistemas": ["sistemas", "ti", "it", "tecnologia", "developer", "programador"],
        "recursos humanos": ["recursos humanos", "rrhh", "talento", "seleccion"],
    }

    # Palabras clave para filtrar resultados relevantes
    palabras_cargo = set(cargo_lower.split())

    # Agregar sinonimos si aplica
    for key, values in sinonimos.items():
        if key in cargo_lower or any(v in cargo_lower for v in values):
            palabras_cargo.update(values)
            break

    try:
        # Delay aleatorio para evitar bloqueos
        time.sleep(random.uniform(1, 2))

        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.get(url, headers=get_random_headers())
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Buscar todos los contenedores de ofertas
            # Tecoloco usa divs con clase que contiene "job" o "result"
            job_containers = soup.find_all("div", class_=re.compile(r"job|result|offer|card", re.I))

            # Si no encuentra con clases, buscar por estructura de enlaces
            if not job_containers:
                job_containers = soup.find_all("a", href=re.compile(r"/\d+/[^/]+\.aspx"))

            seen_links = set()

            for container in job_containers:
                try:
                    # Buscar el enlace de la oferta
                    if container.name == "a":
                        link_elem = container
                    else:
                        link_elem = container.find("a", href=re.compile(r"/\d+/[^/]+\.aspx"))

                    if not link_elem:
                        continue

                    href = link_elem.get("href", "")
                    if not href or href in seen_links:
                        continue

                    # Construir link completo
                    if href.startswith("/"):
                        link = f"https://{dominio}{href}"
                    else:
                        link = href

                    seen_links.add(href)

                    # Extraer titulo
                    titulo = link_elem.get_text(strip=True)
                    if not titulo or len(titulo) < 3:
                        # Intentar buscar h2, h3, h4 dentro del contenedor
                        titulo_elem = container.find(["h2", "h3", "h4", "strong"])
                        if titulo_elem:
                            titulo = titulo_elem.get_text(strip=True)

                    if not titulo or len(titulo) < 3:
                        continue

                    # Limpiar titulo
                    titulo = re.sub(r"\s+", " ", titulo).strip()

                    # Filtrar: verificar si el titulo tiene relacion con el cargo buscado
                    titulo_lower = titulo.lower()
                    es_relevante = False

                    # Verificar si alguna palabra del cargo esta en el titulo
                    for palabra in palabras_cargo:
                        if len(palabra) >= 3 and palabra in titulo_lower:
                            es_relevante = True
                            break

                    # Si no es relevante por titulo, verificar en el contexto
                    if not es_relevante:
                        texto_contexto = container.get_text(" ", strip=True).lower()
                        for palabra in palabras_cargo:
                            if len(palabra) >= 3 and palabra in texto_contexto:
                                es_relevante = True
                                break

                    # Si no es relevante, no incluir
                    if not es_relevante:
                        continue

                    # Buscar empresa
                    empresa = "No especificada"
                    empresa_elem = container.find(class_=re.compile(r"company|empresa|employer", re.I))
                    if empresa_elem:
                        empresa = empresa_elem.get_text(strip=True)
                    else:
                        # Buscar en spans o divs secundarios
                        for elem in container.find_all(["span", "div", "p"]):
                            texto = elem.get_text(strip=True)
                            # Si parece nombre de empresa (no es fecha, no es ubicacion)
                            if texto and len(texto) > 2 and len(texto) < 50:
                                if not re.search(r"expira|fecha|managua|guatemala|honduras|nicaragua|ver oferta", texto.lower()):
                                    empresa = texto
                                    break

                    # Buscar ubicacion
                    ubicacion = ciudad if ciudad else ""
                    ubicacion_match = re.search(
                        r"(Managua|Guatemala City|Guatemala|San Salvador|Tegucigalpa|San José|"
                        r"León|Matagalpa|Chinandega|Masaya|Granada|Estelí|Jinotega|"
                        r"Chontales|Rivas|Carazo|Boaco|Madriz|Nueva Segovia|"
                        r"Quetzaltenango|Escuintla|Santa Ana|San Miguel)",
                        container.get_text(" ", strip=True),
                        re.IGNORECASE
                    )
                    if ubicacion_match:
                        ubicacion = ubicacion_match.group(0)

                    if not ubicacion:
                        ubicacion = pais.title()

                    empleo = {
                        "titulo": titulo[:100],
                        "empresa": empresa[:50] if empresa else "No especificada",
                        "ubicacion": f"{ubicacion}, {pais.title()}",
                        "link": link,
                        "fuente": "Tecoloco",
                        "descripcion": "",
                    }

                    empleos.append(empleo)

                    if len(empleos) >= cantidad:
                        break

                except Exception:
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

    empleos = buscar_tecoloco("marketing", "nicaragua", cantidad=10)

    for i, emp in enumerate(empleos, 1):
        print(f"\n{i}. {emp['titulo']}")
        print(f"   Empresa: {emp['empresa']}")
        print(f"   Ubicacion: {emp['ubicacion']}")
        print(f"   Link: {emp['link']}")
