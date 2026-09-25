# Proyecto 3 — Automatización Cross-Browser con Selenium WebDriver
**Grupo 10** — Alexis Zelaya, Dario Exequiel Pereyra, Thiago Agustín Sandoval
Técnicas Avanzadas de Programación (TAP) — Sprint 1

## 1. Qué es esto

Este repositorio contiene el primer artefacto funcional del proyecto de especialización en
Selenium WebDriver. El objetivo del Sprint 1 es demostrar automatización cross-browser: el
mismo flujo de prueba corriendo sobre distintos navegadores (Chrome, Firefox y Edge) sin
duplicar código.

## 2. Sistema bajo prueba

**ParaBank** (`https://parabank.parasoft.com`), un banco de práctica publicado por Parasoft
específicamente para entrenar herramientas de automatización de pruebas. No requiere
autorización adicional porque fue creado con ese propósito. Ver `Ficha_Sistema_Bajo_Prueba.docx`
para el detalle completo (qué es, por qué se eligió, cómo se verificó la autorización).

## 3. Estructura del repositorio

```
TAP_Sprint1_Selenium_Grupo10/
├── README.md
├── .gitignore
├── requirements.txt
├── conftest.py              # fixture cross-browser (chrome / firefox / edge)
├── pytest.ini
└── tests/
    └── test_login.py        # registro de usuario + login válido, y login con credenciales inválidas
```

## 4. Requisitos previos

- Python 3.9 o superior
- Google Chrome y/o Mozilla Firefox y/o Microsoft Edge instalados en la máquina
- No hace falta descargar los drivers a mano: desde Selenium 4.6, **Selenium Manager**
  (integrado en la propia librería `selenium`) detecta el navegador instalado y resuelve
  el driver correcto de forma automática, la primera vez que corre cada navegador.

## 5. Instalación

```bash
# 1. Clonar el repositorio
git clone <URL_DEL_REPO>
cd proyecto3-selenium

# 2. Crear entorno virtual (recomendado)
python3 -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

## 6. Cómo ejecutar los tests

```bash
# Correr todo en Chrome (navegador por defecto)
pytest

# Correr en un navegador específico
pytest --browser=chrome
pytest --browser=firefox
pytest --browser=edge

# Correr en modo headless (sin abrir ventana, útil en CI o máquinas sin entorno gráfico)
pytest --browser=chrome --headless

# Correr en LOS TRES navegadores en una sola invocación (matriz cross-browser)
pytest --browser=chrome && pytest --browser=firefox && pytest --browser=edge

# Ver más detalle por consola
pytest -v

# Generar un reporte HTML de la corrida (queda en report.html)
pytest --html=report.html --self-contained-html
```

## 7. Qué prueba cada test

| Archivo | Qué verifica | Por qué importa |
|---|---|---|
| `test_login.py::test_registro_y_login_exitoso` | Registra un usuario nuevo (con datos generados en cada corrida), confirma que ParaBank loguea automáticamente tras el registro, cierra sesión, y vuelve a loguear manualmente con ese mismo usuario. | Camino feliz de punta a punta: alta de cliente + autenticación real, sin depender de una cuenta fija que otra persona pudo haber modificado (ParaBank es un sitio público compartido). |
| `test_login.py::test_login_credenciales_invalidas` | Con un usuario inexistente y contraseña incorrecta, la app no redirige a `/overview.htm` y muestra el mensaje de error. | Caso negativo: la app no debe dejar pasar credenciales inválidas ni fallar silenciosamente. |

## 8. Errores comunes durante la instalación (y cómo se resolvieron)

Completar por cada integrante según lo que le haya pasado en su máquina. Ejemplos típicos:

- **`SessionNotCreatedException: This version of ChromeDriver only supports Chrome version X`**
  → Ya no debería pasar: al usar Selenium Manager (en vez de la vieja `webdriver-manager`), la
  versión del driver siempre se resuelve contra el navegador realmente instalado en la máquina.
- **`ConnectionError: Could not reach host. Are you offline?` al bajar el driver de Edge**
  → Esto pasaba con la librería `webdriver-manager`, porque dependía de un endpoint de Microsoft
  (`msedgedriver.azureedge.net`) que fue dado de baja. Se resolvió sacando esa librería del
  proyecto y dejando que Selenium Manager (integrado en `selenium` 4.6+) resuelva el driver solo.
- **`unknown error: cannot find Chrome binary`**
  → Chrome no está instalado en esa máquina, o está en una ubicación no estándar. Instalarlo
  normalmente desde google.com/chrome, o correr los tests con `--browser=edge` mientras tanto.

## 9. Próximos pasos (Sprint 2)

- Sumar un caso de prueba con datos parametrizados (varios usuarios/contraseñas con `pytest.mark.parametrize`).
- Integrar el reporte HTML como evidencia estándar de cada corrida.
- Evaluar Page Object Model para separar localizadores de lógica de test a medida que crezca la suite.