# Proyecto 3 — Automatización Cross-Browser con Selenium WebDriver
**Grupo 10** — Alexis Zelaya, Dario Exequiel Pereyra, Thiago Agustín Sandoval
Técnicas Avanzadas de Programación (TAP) — Sprint 3

## 1. Qué es esto

Este repositorio contiene el artefacto funcional del proyecto de especialización en
Selenium WebDriver. El objetivo del Sprint 3 es demostrar automatización cross-browser con
CI/CD: el mismo flujo de prueba corriendo sobre distintos navegadores (Chrome y Firefox)
en GitHub Actions, sin duplicar código.

## 2. Sistema bajo prueba

**ParaBank** (`https://parabank.parasoft.com`), un banco de práctica publicado por Parasoft
específicamente para entrenar herramientas de automatización de pruebas. No requiere
autorización adicional porque fue creado con ese propósito. Ver `Ficha_Sistema_Bajo_Prueba.docx`
para el detalle completo (qué es, por qué se eligió, cómo se verificó la autorización).

## 3. Estructura del repositorio

```
proyecto3-selenium/
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

| Archivo | Caso | Qué verifica | Estado |
|---|---|---|---|
| `test_login.py::test_registro_y_login_exitoso` | TC04 + TC01 | Registro de usuario nuevo y login posterior exitoso. | ✅ Ejecutado, PASSED |
| `test_login.py::test_login_credenciales_invalidas` | TC02 | Usuario inexistente no puede loguearse. | ✅ Ejecutado, PASSED |
| `test_login.py::test_login_password_vacio` | TC03 | Password vacío no permite loguear aunque el usuario exista. | ✅ Ejecutado (Sprint 2) |
| `test_login.py::test_registro_campos_vacios` | TC05 | Formulario de registro vacío no crea cuenta y muestra "required". | ✅ Ejecutado (Sprint 2) |
| `test_login.py::test_registro_usuario_duplicado` | TC06 | No se puede registrar dos veces el mismo username. | ✅ Ejecutado (Sprint 2) |
| `test_transfer_y_cuentas.py::test_transferencia_exitosa` | TC07 | Transferencia válida entre cuentas propias. | ⏸️ Diseñado, `skip` hasta verificar selectores |
| `test_transfer_y_cuentas.py::test_transferencia_monto_cero` | TC08 | Transferencia con monto 0. | ⏸️ Diseñado, `skip` |
| `test_transfer_y_cuentas.py::test_transferencia_supera_saldo` | TC09 | Transferencia mayor al saldo disponible. | ⏸️ Diseñado, `skip` |
| `test_transfer_y_cuentas.py::test_apertura_cuenta_nueva` | TC10 | Apertura de una cuenta nueva. | ⏸️ Diseñado, `skip` |

El detalle completo de cada caso (precondiciones, pasos, resultado esperado, criterio de
aceptación y técnica de diseño aplicada) está en `Documento_Sprint2.docx`.

## 8. Cómo activar los tests pendientes (TC07–TC10)

Los tests de `test_transfer_y_cuentas.py` están deliberadamente desactivados con
`@pytest.mark.skip` porque sus localizadores (ids de los campos de `transfer.htm` y
`openaccount.htm`) todavía no fueron verificados contra el sistema real con el navegador
abierto. Antes de activarlos:

1. Loguearse manualmente en ParaBank y abrir las herramientas de desarrollador (F12) en esas
   dos páginas.
2. Confirmar que los `id` usados en el código (`amount`, `fromAccountId`, `toAccountId`, `type`,
   `openAccountButton`) coinciden con el HTML real.
3. Ajustar lo que haga falta y sacar el decorador `@pytest.mark.skip` de cada función.

## 9. Generar el reporte de ejecución (para la carpeta de Evidencias)

```bash
pytest --html=Ejecucion_Pruebas.html --self-contained-html -v
```

Este archivo (o su versión `.log` con `pytest -v > Ejecucion_Pruebas.log`) es el que va dentro
de `Automatizacion/Ejecucion_Pruebas.log` en el zip de entrega del Sprint 2.

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

## 10. Sprint 3: ejecución automática (CI/CD)

La suite corre sola en GitHub Actions (`.github/workflows/tests.yml`):

| Cuándo | Qué hace |
|---|---|
| En cada `push` y cada pull request | Corre la suite en Chrome y en Firefox, sin ventana, en paralelo |
| Todos los días 12:00 UTC (09:00 de Argentina) | Corrida programada, para detectar cambios del sitio |
| A mano (pestaña Actions, "Run workflow") | Para volver a correr sin hacer un commit |

Cada ejecución guarda como artefactos, sin intervención manual: reporte HTML, resultados en XML
(JUnit) y capturas de pantalla de los tests que fallan. Se descargan desde la pestaña **Actions**,
dentro de la ejecución, sección *Artifacts*.

### Ejecución local equivalente

```bash
pip install -r requirements.txt
pytest --browser=chrome --headless -n 2          # sin ventana y en paralelo
pytest -m smoke                                  # solo los tests rápidos del flujo crítico
pytest --html=reportes/reporte.html --self-contained-html --junitxml=reportes/resultados.xml
```

### Medición antes/después de la optimización

```bash
# ANTES: un test por vez, con ventana
pytest -q
# DESPUÉS: sin ventana y en paralelo
pytest -q --headless -n 2
pytest -q --headless -n 4
```

Anotar el tiempo total que muestra pytest al final de cada comando (por ejemplo `in 69.29s`).
Línea base registrada del Sprint 2: 69,29 s para la suite completa, ejecutada en serie y con ventana.

### Datos de prueba y paralelismo

Todos los datos que se registran (usuario, SSN, teléfono) se generan con la hora en milisegundos
más dígitos al azar, para que dos tests en paralelo nunca usen el mismo dato.
