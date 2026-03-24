#!/usr/bin/env python3
"""
MVP - Buscador de Empleos

Busca ofertas de trabajo en LinkedIn, Indeed y Glassdoor.
Uso:
    python buscar_empleo.py --cargo "python developer" --ubicacion "Colombia"
    python buscar_empleo.py -c "data analyst" -u "Remote"
"""

import argparse
import sys
from datetime import datetime

# Fix encoding para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from jobspy import scrape_jobs


def limpiar_texto(texto: str) -> str:
    """Limpia caracteres problematicos para la consola."""
    if not texto:
        return ""
    # Reemplazar emojis y caracteres especiales
    return texto.encode('ascii', 'ignore').decode('ascii')


def buscar_empleos(cargo: str, ubicacion: str, cantidad: int = 20) -> list[dict]:
    """
    Busca empleos usando JobSpy (gratuito).

    Args:
        cargo: El cargo o puesto a buscar (ej: "python developer", "analista de datos")
        ubicacion: Ciudad, pais o "Remote" (ej: "Colombia", "Bogota", "Remote")
        cantidad: Numero maximo de resultados por sitio

    Returns:
        Lista de ofertas de empleo encontradas
    """
    print(f"\nBuscando: '{cargo}' en '{ubicacion}'...")
    print("-" * 50)

    empleos = []
    ubicacion_lower = ubicacion.lower()

    # Determinar sitios y pais segun ubicacion
    # Glassdoor solo funciona para USA
    if any(pais in ubicacion_lower for pais in ['colombia', 'mexico', 'argentina', 'chile', 'peru', 'espana', 'spain']):
        sitios = ["indeed", "linkedin"]
        pais_indeed = "Colombia" if "colombia" in ubicacion_lower else ubicacion
    else:
        sitios = ["indeed", "linkedin", "glassdoor"]
        pais_indeed = "USA"

    try:
        # Scrape de los sitios disponibles
        df = scrape_jobs(
            site_name=sitios,
            search_term=cargo,
            location=ubicacion,
            results_wanted=cantidad,
            hours_old=168,  # Ultima semana
            country_indeed=pais_indeed,
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
                'descripcion': str(row.get('description', ''))[:200] if str(row.get('description', '')) != 'nan' else '',
            }
            empleos.append(empleo)

    except Exception as e:
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
        ubicacion = limpiar_texto(empleo['ubicacion'])
        descripcion = limpiar_texto(empleo.get('descripcion', ''))

        print(f"\n{i}. {titulo}")
        print(f"   Empresa: {empresa}")
        print(f"   Ubicacion: {ubicacion}")
        print(f"   Fuente: {empleo['fuente']}")
        if empleo['link']:
            print(f"   Link: {empleo['link']}")
        if descripcion:
            print(f"   Descripcion: {descripcion[:100]}...")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Busca ofertas de empleo en LinkedIn, Indeed y Glassdoor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python buscar_empleo.py --cargo "python developer" --ubicacion "Colombia"
  python buscar_empleo.py -c "analista de datos" -u "Bogota"
  python buscar_empleo.py -c "react developer" -u "Remote" -n 30
        """
    )

    parser.add_argument(
        '--cargo', '-c',
        type=str,
        required=True,
        help='Cargo o puesto a buscar (ej: "python developer")'
    )

    parser.add_argument(
        '--ubicacion', '-u',
        type=str,
        required=True,
        help='Ciudad, pais o "Remote" (ej: "Colombia", "Bogota", "Remote")'
    )

    parser.add_argument(
        '--cantidad', '-n',
        type=int,
        default=20,
        help='Numero de resultados a buscar (default: 20)'
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("BUSCADOR DE EMPLEOS - MVP")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    empleos = buscar_empleos(
        cargo=args.cargo,
        ubicacion=args.ubicacion,
        cantidad=args.cantidad
    )

    mostrar_resultados(empleos)

    print("-" * 60)
    print(f"Busqueda completada. Total: {len(empleos)} ofertas")
    print("-" * 60)


if __name__ == "__main__":
    main()
