import os
import random
from datetime import datetime

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
            # Necesarios para correr en un runner de CI (Linux sin escritorio)
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
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
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
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

    marca = f"{int(time.time() * 1000)}{random.randint(100, 999)}"
    username = f"grupo10qa{marca}"
    password = "Passw0rd!2026"
    # El SSN tambien tiene que ser unico: ParaBank es un sitio publico y
    # persistente, y rechaza en silencio un SSN que ya fue usado antes
    # (incluso en una corrida de dias atras). Lo generamos a partir del
    # timestamp para que nunca se repita entre corridas.
    ssn_unico = marca[-9:]

    driver.get(f"{base_url}/register.htm")
    driver.find_element(By.ID, "customer.firstName").send_keys("Alexis")
    driver.find_element(By.ID, "customer.lastName").send_keys("Zelaya")
    driver.find_element(By.ID, "customer.address.street").send_keys("Av. Siempre Viva 742")
    driver.find_element(By.ID, "customer.address.city").send_keys("San Miguel de Tucuman")
    driver.find_element(By.ID, "customer.address.state").send_keys("Tucuman")
    driver.find_element(By.ID, "customer.address.zipCode").send_keys("4000")
    driver.find_element(By.ID, "customer.phoneNumber").send_keys("381" + marca[-7:])
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

    # Hallazgo del Sprint 2: ParaBank a veces CREA la cuenta pero igual
    # muestra "This username already exists." y no redirige a overview.htm
    # (confirmado: despues del error, el login con ese usuario funciona).
    # Para que el fixture siempre entregue una sesion iniciada, si no
    # llegamos a overview.htm iniciamos sesion manualmente con el usuario
    # que acabamos de crear.
    if "/overview.htm" not in driver.current_url:
        driver.get(f"{base_url}/index.htm")
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "input[value='Log In']").click()
        WebDriverWait(driver, 10).until(
            lambda d: "/overview.htm" in d.current_url or "could not be verified" in d.page_source
        )
        assert "/overview.htm" in driver.current_url, (
            f"No se pudo dejar una sesion iniciada con el usuario {username}"
        )

    return {"username": username, "password": password}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):

    outcome = yield
    reporte = outcome.get_result()
    if reporte.when in ("setup", "call") and reporte.failed:
        drv = item.funcargs.get("driver")
        if drv is not None:
            os.makedirs("reportes/capturas", exist_ok=True)
            marca_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta = f"reportes/capturas/{item.name}_{marca_hora}.png"
            try:
                drv.save_screenshot(ruta)
            except Exception:
                pass  # si el navegador ya se cerro, no ocultamos el fallo real
