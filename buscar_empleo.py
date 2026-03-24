#!/usr/bin/env python3
"""
Buscador de Empleos - Ayuda a personas a encontrar trabajo

Busca ofertas de trabajo en LinkedIn, Indeed y Glassdoor.
Guarda historial de busquedas para seguimiento.

Uso:
    python buscar_empleo.py --cargo "marketing" --ciudad "Bogota" --pais "Colombia"
    python buscar_empleo.py -c "desarrollador" -ci "Managua" -p "worldwide"
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Fix encoding para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from jobspy import scrape_jobs

# Directorio para datos
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORIAL_FILE = DATA_DIR / "historial_busquedas.json"

# Paises soportados por JobSpy/Indeed
PAISES_SOPORTADOS = [
    "argentina", "australia", "austria", "bahrain", "belgium", "brazil",
    "canada", "chile", "china", "colombia", "costa rica", "czech republic",
    "denmark", "ecuador", "egypt", "finland", "france", "germany", "greece",
    "hong kong", "hungary", "india", "indonesia", "ireland", "israel", "italy",
    "japan", "kuwait", "luxembourg", "malaysia", "malta", "mexico", "morocco",
    "netherlands", "new zealand", "nigeria", "norway", "oman", "pakistan",
    "panama", "peru", "philippines", "poland", "portugal", "qatar", "romania",
    "saudi arabia", "singapore", "south africa", "south korea", "spain",
    "sweden", "switzerland", "taiwan", "thailand", "turkey", "ukraine",
    "united arab emirates", "uk", "united kingdom", "usa", "united states",
    "uruguay", "venezuela", "vietnam", "worldwide", "remote"
]

# Paises donde Glassdoor NO funciona
PAISES_SIN_GLASSDOOR = [
    "colombia", "mexico", "argentina", "chile", "peru", "brazil", "ecuador",
    "venezuela", "panama", "costa rica", "uruguay", "spain", "espana"
]


def limpiar_texto(texto: str) -> str:
    """Limpia caracteres problematicos para la consola."""
    if not texto:
        return ""
    return texto.encode('ascii', 'ignore').decode('ascii')


def cargar_historial() -> dict:
    """Carga el historial de busquedas desde JSON."""
    if HISTORIAL_FILE.exists():
        try:
            with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"busquedas": []}


def guardar_historial(historial: dict) -> None:
    """Guarda el historial de busquedas en JSON."""
    try:
        with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Error guardando historial: {e}")


def guardar_busqueda(cargo: str, ciudad: str, pais: str, empleos: list[dict]) -> None:
    """Guarda una busqueda en el historial."""
    historial = cargar_historial()

    busqueda = {
        "fecha": datetime.now().isoformat(),
        "cargo": cargo,
        "ciudad": ciudad,
        "pais": pais,
        "total_ofertas": len(empleos),
        "ofertas": [
            {
                "titulo": e["titulo"],
                "empresa": e["empresa"],
                "ubicacion": e["ubicacion"],
                "link": e["link"],
                "fuente": e["fuente"]
            }
            for e in empleos
        ]
    }

    historial["busquedas"].append(busqueda)

    # Mantener solo las ultimas 100 busquedas
    if len(historial["busquedas"]) > 100:
        historial["busquedas"] = historial["busquedas"][-100:]

    guardar_historial(historial)
    print(f"\n[Guardado en historial: {HISTORIAL_FILE}]")


def verificar_pais(pais: str) -> tuple[bool, str]:
    """
    Verifica si el pais esta soportado y sugiere alternativas.

    Returns:
        (soportado, mensaje)
    """
    pais_lower = pais.lower().strip()

    if pais_lower in PAISES_SOPORTADOS:
        return True, ""

    # Buscar paises similares
    sugerencias = [p for p in PAISES_SOPORTADOS if pais_lower[:3] in p]

    msg = f"'{pais}' no esta soportado por los sitios de empleo.\n"
    msg += "Paises de LATAM soportados: argentina, brazil, chile, colombia, costa rica, ecuador, mexico, panama, peru, uruguay, venezuela\n"
    msg += "Tip: Usa 'worldwide' o 'remote' para buscar empleos remotos globales."

    if sugerencias:
        msg += f"\nSugerencias: {', '.join(sugerencias[:5])}"

    return False, msg


def buscar_empleos(cargo: str, ciudad: str, pais: str, cantidad: int = 20) -> list[dict]:
    """
    Busca empleos usando JobSpy (gratuito).

    Args:
        cargo: El cargo o puesto a buscar
        ciudad: Ciudad especifica (puede ser vacio)
        pais: Pais o "worldwide"/"remote"
        cantidad: Numero maximo de resultados

    Returns:
        Lista de ofertas de empleo encontradas
    """
    # Construir ubicacion
    if ciudad and ciudad.lower() != pais.lower():
        ubicacion = f"{ciudad}, {pais}"
    else:
        ubicacion = pais

    print(f"\nBuscando: '{cargo}' en '{ubicacion}'...")
    print("-" * 50)

    empleos = []
    pais_lower = pais.lower().strip()

    # Verificar pais soportado
    soportado, mensaje = verificar_pais(pais)
    if not soportado:
        print(f"\nADVERTENCIA: {mensaje}")
        print("\nIntentando busqueda de todas formas...\n")

    # Determinar sitios segun pais
    if pais_lower in PAISES_SIN_GLASSDOOR:
        sitios = ["indeed", "linkedin"]
    else:
        sitios = ["indeed", "linkedin", "glassdoor"]

    # Determinar country_indeed
    pais_indeed_map = {
        "colombia": "Colombia",
        "mexico": "Mexico",
        "argentina": "Argentina",
        "chile": "Chile",
        "peru": "Peru",
        "brazil": "Brazil",
        "ecuador": "Ecuador",
        "spain": "Spain",
        "espana": "Spain",
        "worldwide": "USA",
        "remote": "USA",
    }
    country_indeed = pais_indeed_map.get(pais_lower, "USA")

    try:
        df = scrape_jobs(
            site_name=sitios,
            search_term=cargo,
            location=ubicacion,
            results_wanted=cantidad,
            hours_old=168,  # Ultima semana
            country_indeed=country_indeed,
        )

        if df is None or df.empty:
            print("No se encontraron ofertas en los sitios consultados.")
            return empleos

        print(f"Encontradas {len(df)} ofertas en {', '.join(sitios)}\n")

        for _, row in df.iterrows():
            titulo = str(row.get('title', ''))
            empresa = str(row.get('company', ''))

            if not titulo or titulo == 'nan':
                continue

            empleo = {
                'titulo': titulo,
                'empresa': empresa if empresa != 'nan' else 'No especificada',
                'ubicacion': str(row.get('location', ubicacion)) if str(row.get('location', '')) != 'nan' else ubicacion,
                'link': str(row.get('job_url', '')) if str(row.get('job_url', '')) != 'nan' else '',
                'fuente': str(row.get('site', 'Desconocido')).capitalize(),
                'descripcion': str(row.get('description', ''))[:300] if str(row.get('description', '')) != 'nan' else '',
            }
            empleos.append(empleo)

    except Exception as e:
        error_msg = str(e)
        if "Invalid country" in error_msg:
            print(f"Error: El pais '{pais}' no esta soportado.")
            print("Usa 'worldwide' para buscar empleos remotos globales.")
        else:
            print(f"Error durante la busqueda: {e}")

    return empleos


def mostrar_resultados(empleos: list[dict]) -> None:
    """Muestra los resultados de forma legible en consola."""
    if not empleos:
        print("\nNo hay resultados para mostrar.")
        return

    print("=" * 60)
    print(f"RESULTADOS: {len(empleos)} ofertas encontradas")
    print("=" * 60)

    for i, empleo in enumerate(empleos, 1):
        titulo = limpiar_texto(empleo['titulo'])
        empresa = limpiar_texto(empleo['empresa'])
        ubicacion_emp = limpiar_texto(empleo['ubicacion'])
        descripcion = limpiar_texto(empleo.get('descripcion', ''))

        print(f"\n{i}. {titulo}")
        print(f"   Empresa: {empresa}")
        print(f"   Ubicacion: {ubicacion_emp}")
        print(f"   Fuente: {empleo['fuente']}")
        if empleo['link']:
            print(f"   Link: {empleo['link']}")
        if descripcion:
            print(f"   Descripcion: {descripcion[:150]}...")


def mostrar_paises_soportados():
    """Muestra lista de paises soportados."""
    print("\nPAISES SOPORTADOS:")
    print("-" * 40)

    latam = ["argentina", "brazil", "chile", "colombia", "costa rica",
             "ecuador", "mexico", "panama", "peru", "uruguay", "venezuela"]

    print("\nLatinoamerica:")
    print(", ".join(latam))

    print("\nOpciones globales:")
    print("worldwide, remote, usa, uk, canada, spain")

    print("\nNOTA: Nicaragua, Guatemala, Honduras, El Salvador NO estan soportados.")
    print("Para estos paises usa 'worldwide' o 'remote'.")


def main():
    parser = argparse.ArgumentParser(
        description='Buscador de empleos - Ayuda a personas a encontrar trabajo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python buscar_empleo.py -c "marketing" -ci "Bogota" -p "Colombia"
  python buscar_empleo.py -c "desarrollador web" -p "Mexico"
  python buscar_empleo.py -c "publicidad" -p "worldwide"
  python buscar_empleo.py --paises   # Ver paises soportados
        """
    )

    parser.add_argument(
        '--cargo', '-c',
        type=str,
        help='Cargo o puesto a buscar (ej: "marketing", "desarrollador")'
    )

    parser.add_argument(
        '--ciudad', '-ci',
        type=str,
        default="",
        help='Ciudad especifica (opcional, ej: "Bogota", "CDMX")'
    )

    parser.add_argument(
        '--pais', '-p',
        type=str,
        help='Pais o "worldwide" para remoto (ej: "Colombia", "worldwide")'
    )

    parser.add_argument(
        '--cantidad', '-n',
        type=int,
        default=20,
        help='Numero de resultados a buscar (default: 20)'
    )

    parser.add_argument(
        '--no-guardar',
        action='store_true',
        help='No guardar en historial'
    )

    parser.add_argument(
        '--paises',
        action='store_true',
        help='Mostrar lista de paises soportados'
    )

    args = parser.parse_args()

    # Mostrar paises y salir
    if args.paises:
        mostrar_paises_soportados()
        return

    # Validar argumentos requeridos
    if not args.cargo or not args.pais:
        parser.print_help()
        print("\nError: --cargo y --pais son requeridos.")
        print("Usa --paises para ver la lista de paises soportados.")
        return

    print("\n" + "=" * 60)
    print("BUSCADOR DE EMPLEOS")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    empleos = buscar_empleos(
        cargo=args.cargo,
        ciudad=args.ciudad,
        pais=args.pais,
        cantidad=args.cantidad
    )

    mostrar_resultados(empleos)

    # Guardar en historial
    if empleos and not args.no_guardar:
        guardar_busqueda(args.cargo, args.ciudad, args.pais, empleos)

    print("\n" + "-" * 60)
    print(f"Busqueda completada. Total: {len(empleos)} ofertas")
    print("-" * 60)


if __name__ == "__main__":
    main()
