import random
import time

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

PASSWORD = "Passw0rd!2026"


def _marca():
    return f"{int(time.time() * 1000)}{random.randint(100, 999)}"


def _username_unico():
    return f"grupo10qa{_marca()}"


def _ssn_unico():
    return _marca()[-9:]


def _telefono_unico():
    return "381" + _marca()[-7:]


def _enviar_registro(driver, base_url, username, password=PASSWORD):
    driver.get(f"{base_url}/register.htm")
    driver.find_element(By.ID, "customer.firstName").send_keys("Alexis")
    driver.find_element(By.ID, "customer.lastName").send_keys("Zelaya")
    driver.find_element(By.ID, "customer.address.street").send_keys("Av. Siempre Viva 742")
    driver.find_element(By.ID, "customer.address.city").send_keys("San Miguel de Tucuman")
    driver.find_element(By.ID, "customer.address.state").send_keys("Tucuman")
    driver.find_element(By.ID, "customer.address.zipCode").send_keys("4000")
    driver.find_element(By.ID, "customer.phoneNumber").send_keys(_telefono_unico())
    driver.find_element(By.ID, "customer.ssn").send_keys(_ssn_unico())
    driver.find_element(By.ID, "customer.username").send_keys(username)
    driver.find_element(By.ID, "customer.password").send_keys(password)
    driver.find_element(By.ID, "repeatedPassword").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "input[value='Register']").click()
    WebDriverWait(driver, 10).until(
        lambda d: "/overview.htm" in d.current_url or "error" in d.page_source.lower()
    )


def _iniciar_sesion(driver, base_url, username, password):
    driver.delete_all_cookies()
    driver.get(f"{base_url}/index.htm")
    driver.find_element(By.NAME, "username").send_keys(username)
    if password:
        driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "input[value='Log In']").click()
    try:
        WebDriverWait(driver, 5).until(
            lambda d: "/overview.htm" in d.current_url or 'class="error"' in d.page_source
        )
    except TimeoutException:
        pass
    return "/overview.htm" in driver.current_url


@pytest.mark.smoke
def test_registro_y_login_exitoso(driver, base_url):
    username = _username_unico()
    _enviar_registro(driver, base_url, username)

    assert _iniciar_sesion(driver, base_url, username, PASSWORD), (
        f"No se pudo iniciar sesion con el usuario recien registrado ({username})"
    )
    assert "Accounts Overview" in driver.find_element(By.CSS_SELECTOR, "h1.title").text


@pytest.mark.xfail(
    strict=False,
    reason="Hallazgo: ParaBank crea la cuenta pero muestra 'This username already exists.' "
           "y no redirige a overview.htm (posible doble envio del formulario).",
)
def test_registro_redirige_a_overview(driver, base_url):
    _enviar_registro(driver, base_url, _username_unico())
    assert "/overview.htm" in driver.current_url


@pytest.mark.smoke
def test_login_credenciales_invalidas(driver, base_url):
    usuario_inexistente = f"noexiste{_marca()}"
    assert not _iniciar_sesion(driver, base_url, usuario_inexistente, "password-incorrecto")
    assert "could not be verified" in driver.page_source


@pytest.mark.smoke
def test_login_password_vacio(driver, base_url, usuario_registrado):
    assert not _iniciar_sesion(driver, base_url, usuario_registrado["username"], "")


def test_registro_campos_vacios(driver, base_url):
    driver.get(f"{base_url}/register.htm")
    driver.find_element(By.CSS_SELECTOR, "input[value='Register']").click()
    WebDriverWait(driver, 10).until(
        lambda d: "/overview.htm" in d.current_url or "required" in d.page_source.lower()
    )
    assert "/overview.htm" not in driver.current_url
    assert "required" in driver.page_source.lower()


def test_registro_usuario_duplicado(driver, base_url, usuario_registrado):
    username = usuario_registrado["username"]
    _enviar_registro(driver, base_url, username, password="OtraPassword!123")

    assert "/overview.htm" not in driver.current_url
    assert "already exists" in driver.page_source.lower()
    assert _iniciar_sesion(driver, base_url, username, usuario_registrado["password"])
