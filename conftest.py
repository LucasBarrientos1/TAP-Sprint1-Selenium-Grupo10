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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time


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


@pytest.fixture
def usuario_registrado(driver, base_url):
    """
    Registra un usuario nuevo con datos unicos y lo deja YA logueado en
    /overview.htm. Lo usan los tests que necesitan partir de una sesion
    autenticada (por ejemplo, el caso de username duplicado en TC06, que
    necesita que un usuario ya exista antes de intentar repetirlo).

    Devuelve un diccionario con el username y password usados, por si el
    test necesita loguearse de nuevo mas adelante.
    """
    username = f"grupo10qa{int(time.time() * 1000)}"
    password = "Passw0rd!2026"
    # El SSN tambien tiene que ser unico: ParaBank es un sitio publico y
    # persistente, y rechaza en silencio un SSN que ya fue usado antes
    # (incluso en una corrida de dias atras). Lo generamos a partir del
    # timestamp para que nunca se repita entre corridas.
    ssn_unico = str(int(time.time() * 1000))[-9:]

    driver.get(f"{base_url}/register.htm")
    driver.find_element(By.ID, "customer.firstName").send_keys("Alexis")
    driver.find_element(By.ID, "customer.lastName").send_keys("Zelaya")
    driver.find_element(By.ID, "customer.address.street").send_keys("Av. Siempre Viva 742")
    driver.find_element(By.ID, "customer.address.city").send_keys("San Miguel de Tucuman")
    driver.find_element(By.ID, "customer.address.state").send_keys("Tucuman")
    driver.find_element(By.ID, "customer.address.zipCode").send_keys("4000")
    driver.find_element(By.ID, "customer.phoneNumber").send_keys("381" + str(int(time.time() * 1000))[-7:])
    driver.find_element(By.ID, "customer.ssn").send_keys(ssn_unico)
    driver.find_element(By.ID, "customer.username").send_keys(username)
    driver.find_element(By.ID, "customer.password").send_keys(password)
    driver.find_element(By.ID, "repeatedPassword").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "input[value='Register']").click()

    # Esperamos explicitamente a que la pagina termine de procesar el
    # registro, en vez de asumir que ya curso (problema de sincronizacion
    # real que detectamos en la primera corrida del Sprint 2).
    WebDriverWait(driver, 10).until(
        lambda d: "/overview.htm" in d.current_url or "error" in d.page_source.lower()
    )

    return {"username": username, "password": password}
