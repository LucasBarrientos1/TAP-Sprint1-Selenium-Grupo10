"""
conftest.py
Este es el corazon de la automatizacion cross-browser: un unico fixture de pytest
que arma el WebDriver correcto (Chrome, Firefox o Edge) segun el parametro
--browser que se pase por linea de comandos. Los tests no saben ni les importa
en que navegador estan corriendo: solo reciben un "driver" ya listo para usar.

Esto es exactamente el problema que resuelve Selenium WebDriver: escribir el
test una sola vez y ejecutarlo contra motores de renderizado distintos
(Blink en Chrome/Edge, Gecko en Firefox) sin duplicar codigo.

Nota tecnica: el driver de cada navegador (chromedriver, geckodriver,
msedgedriver) lo resuelve automaticamente "Selenium Manager", una herramienta
que Selenium trae integrada desde la version 4.6 en adelante. Por eso NO
usamos la libreria externa webdriver-manager: esa libreria depende de un
endpoint de Microsoft (msedgedriver.azureedge.net) que fue dado de baja, lo
que hacia fallar la descarga del driver de Edge con un error de conexion
enganoso ("Are you offline?"). Selenium Manager no tiene ese problema.
"""
import pytest
from selenium import webdriver


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Navegador a usar: chrome | firefox | edge",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Correr sin abrir ventana grafica (util en CI o servidores sin entorno grafico)",
    )


@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser").lower()
    headless = request.config.getoption("--headless")

    if browser == "chrome":
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1400,900")
        drv = webdriver.Chrome(options=options)

    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        drv = webdriver.Firefox(options=options)

    elif browser == "edge":
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
        drv = webdriver.Edge(options=options)

    else:
        raise ValueError(
            f"Navegador '{browser}' no soportado. Usa: chrome, firefox o edge."
        )

    drv.implicitly_wait(5)
    yield drv
    drv.quit()


@pytest.fixture
def base_url():
    return "https://parabank.parasoft.com/parabank"
