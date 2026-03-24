# Scraping Employees Free

Buscador de ofertas de empleo gratuito para ayudar a personas que buscan trabajo.

## Repositorio
https://github.com/Colombia-IA/scrapping_employees_free.git

## Proposito

Cuando ves a alguien en LinkedIn publicando su hoja de vida porque no tiene trabajo, puedes usar este script para buscarle ofertas de empleo relevantes y compartirle la informacion.

## Plataformas soportadas

| Plataforma | Sitios | Cobertura |
|------------|--------|-----------|
| **JobSpy** | LinkedIn, Indeed, Glassdoor, Google Jobs, ZipRecruiter | Global (40+ paises) |
| **Tecoloco** | tecoloco.com.ni/gt/sv/hn | Centroamerica |

## Uso

```bash
# Instalar dependencias
pip install -r requirements.txt

# Buscar empleos
python buscar_empleo.py -c "marketing" -ci "Bogota" -p "Colombia"
python buscar_empleo.py -c "ventas" -ci "Managua" -p "Nicaragua"
python buscar_empleo.py -c "developer" -p "usa"
python buscar_empleo.py -c "publicidad" -p "worldwide"

# Ver paises soportados
python buscar_empleo.py --paises

# Buscar sin guardar en historial
python buscar_empleo.py -c "ventas" -p "Peru" --no-guardar
```

## Parametros

| Parametro | Corto | Requerido | Descripcion |
|-----------|-------|-----------|-------------|
| `--cargo` | `-c` | Si | Cargo o puesto a buscar |
| `--pais` | `-p` | Si | Pais (ver lista abajo) |
| `--ciudad` | `-ci` | No | Ciudad especifica |
| `--cantidad` | `-n` | No | Numero de resultados (default: 20) |
| `--no-guardar` | - | No | No guardar en historial |
| `--paises` | - | No | Ver lista de paises soportados |

## Paises soportados

### JobSpy (LinkedIn, Indeed, Glassdoor, Google Jobs)
**Latinoamerica:** argentina, brazil, chile, colombia, costa rica, ecuador, mexico, panama, peru, uruguay, venezuela

**Global:** usa, uk, canada, spain, worldwide, remote

### Tecoloco (Centroamerica)
nicaragua, guatemala, el salvador, honduras, costa rica

### ZipRecruiter
Solo USA

## Estructura

```
scraping_employee_free/
├── buscar_empleo.py           # Script principal
├── requirements.txt           # Dependencias
├── CLAUDE.md                  # Esta documentacion
├── .gitignore
├── scrapers/                  # Scrapers adicionales
│   ├── __init__.py
│   └── tecoloco.py           # Scraper Centroamerica
└── data/
    └── historial_busquedas.json   # Historial (local, no se sube)
```

## Historial

El historial guarda cada busqueda con:
- Fecha
- Cargo, ciudad, pais
- Lista de ofertas encontradas (titulo, empresa, link, fuente)

Archivo: `data/historial_busquedas.json`

Se mantienen las ultimas 100 busquedas automaticamente.

## Dependencias

- `python-jobspy` - Scraping de LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter
- `httpx` - HTTP client para scrapers adicionales
- `beautifulsoup4` - Parser HTML
- `lxml` - Parser XML/HTML rapido
- Python 3.10+

## Agregar nuevos scrapers

Para agregar soporte a nuevos sitios de empleo:

1. Crear archivo en `scrapers/nuevo_sitio.py`
2. Implementar funcion `buscar_nuevo_sitio(cargo, pais, ciudad, cantidad)`
3. Importar en `scrapers/__init__.py`
4. Integrar en `buscar_empleo.py`

## Limitaciones

- LinkedIn tiene rate limiting agresivo
- Glassdoor solo funciona para USA
- Algunos sitios bloquean requests directos (requieren browser)
- Tecoloco no extrae nombre de empresa (limitacion de la pagina)
