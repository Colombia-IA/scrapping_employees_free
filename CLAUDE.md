# Scraping Employees Free - MVP

Buscador de ofertas de empleo gratuito usando scraping de sitios web.

## Repositorio
https://github.com/Colombia-IA/scrapping_employees_free.git

## Descripcion

Script simple que busca ofertas de empleo en multiples sitios (LinkedIn, Indeed, Glassdoor) usando la libreria JobSpy. Permite parametrizar la busqueda por cargo y ubicacion.

## Como funciona

1. El usuario ejecuta el script con parametros de cargo y ubicacion
2. JobSpy hace scraping de LinkedIn, Indeed y Glassdoor simultaneamente
3. Se filtran y procesan los resultados
4. Se muestran las ofertas encontradas en consola

## Arquitectura

```
scraping_employee_free/
├── buscar_empleo.py    # Script principal
├── requirements.txt    # Dependencias (solo python-jobspy)
└── CLAUDE.md          # Esta documentacion
```

## Uso

```bash
# Instalar dependencia
pip install -r requirements.txt

# Buscar empleos
python buscar_empleo.py --cargo "python developer" --ubicacion "Colombia"
python buscar_empleo.py -c "data analyst" -u "Mexico"
python buscar_empleo.py -c "react junior" -u "Remote" -n 30
```

## Parametros

| Parametro | Corto | Descripcion | Ejemplo |
|-----------|-------|-------------|---------|
| `--cargo` | `-c` | Cargo o puesto a buscar | "python developer" |
| `--ubicacion` | `-u` | Ciudad, pais o "Remote" | "Colombia", "Remote" |
| `--cantidad` | `-n` | Numero de resultados (default: 20) | 10, 30 |

## Sitios soportados

- **LinkedIn** - Funciona globalmente
- **Indeed** - Funciona globalmente
- **Glassdoor** - Solo USA (se omite automaticamente para otros paises)

## Dependencias

- `python-jobspy` - Libreria de scraping de empleos (gratuita)
- Python 3.10+

## Notas tecnicas

- JobSpy maneja internamente los headers y delays para evitar bloqueos
- Los resultados se limitan a ofertas de los ultimos 7 dias
- El encoding se maneja automaticamente para Windows (caracteres especiales)
