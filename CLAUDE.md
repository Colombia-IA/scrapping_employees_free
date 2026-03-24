# Scraping Employees Free

Buscador de ofertas de empleo gratuito para ayudar a personas que buscan trabajo.

## Repositorio
https://github.com/Colombia-IA/scrapping_employees_free.git

## Proposito

Cuando ves a alguien en LinkedIn publicando su hoja de vida porque no tiene trabajo, puedes usar este script para buscarle ofertas de empleo relevantes y compartirle la informacion.

## Como funciona

1. Ves un post de alguien buscando trabajo
2. Ejecutas el script con el cargo y pais que busca esa persona
3. El script busca en LinkedIn, Indeed y Glassdoor
4. Te muestra las ofertas encontradas
5. Guarda un historial de las busquedas en JSON

## Uso

```bash
# Instalar dependencia
pip install -r requirements.txt

# Buscar empleos
python buscar_empleo.py -c "marketing" -ci "Bogota" -p "Colombia"
python buscar_empleo.py -c "desarrollador web" -p "Mexico"
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
| `--pais` | `-p` | Si | Pais o "worldwide" para remoto |
| `--ciudad` | `-ci` | No | Ciudad especifica |
| `--cantidad` | `-n` | No | Numero de resultados (default: 20) |
| `--no-guardar` | - | No | No guardar en historial |
| `--paises` | - | No | Ver lista de paises soportados |

## Paises soportados

### Latinoamerica
argentina, brazil, chile, colombia, costa rica, ecuador, mexico, panama, peru, uruguay, venezuela

### Opciones globales
worldwide, remote, usa, uk, canada, spain

### NO soportados
Nicaragua, Guatemala, Honduras, El Salvador - usar `worldwide` para estos paises

## Estructura

```
scraping_employee_free/
├── buscar_empleo.py           # Script principal
├── requirements.txt           # Dependencias
├── CLAUDE.md                  # Esta documentacion
├── .gitignore
└── data/
    └── historial_busquedas.json   # Historial de busquedas
```

## Historial

El historial guarda cada busqueda con:
- Fecha
- Cargo, ciudad, pais
- Lista de ofertas encontradas (titulo, empresa, link, fuente)

Archivo: `data/historial_busquedas.json`

Se mantienen las ultimas 100 busquedas automaticamente.

## Sitios de empleo

| Sitio | Cobertura |
|-------|-----------|
| LinkedIn | Global |
| Indeed | Global |
| Glassdoor | Solo USA |

## Dependencias

- `python-jobspy` - Libreria de scraping de empleos (gratuita)
- Python 3.10+

## Limitaciones

- LinkedIn tiene medidas anti-scraping, puede fallar ocasionalmente
- Glassdoor solo funciona para USA
- Algunos paises de Centroamerica no estan soportados
