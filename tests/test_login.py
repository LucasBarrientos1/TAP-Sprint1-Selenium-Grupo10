"""
test_login.py
Sistema bajo prueba: ParaBank (https://parabank.parasoft.com), un banco de
practica publicado por Parasoft especificamente para testing de automatizacion.

Por que registramos un usuario nuevo en lugar de usar uno fijo:
ParaBank es un sitio publico compartido por estudiantes y equipos de QA de
todo el mundo. Un usuario "fijo" documentado en un tutorial puede tener la
contrasena cambiada por otra persona, o directamente no existir mas. Registrar
un usuario nuevo con datos generados en cada corrida hace el test reproducible
y no depende de que nadie mas haya tocado esa cuenta antes que nosotros.
"""
import time
from selenium.webdriver.common.by import By


def _generar_username_unico():
    # Usamos el timestamp para que cada corrida registre un usuario distinto
    # y el test se pueda ejecutar las veces que haga falta sin chocar con
    # un usuario que ya existe de una corrida anterior.
    return f"grupo10qa{int(time.time())}"


def test_registro_y_login_exitoso(driver, base_url):
    username = _generar_username_unico()
    password = "Passw0rd!2026"

    driver.get(f"{base_url}/register.htm")

    driver.find_element(By.ID, "customer.firstName").send_keys("Alexis")
    driver.find_element(By.ID, "customer.lastName").send_keys("Zelaya")
    driver.find_element(By.ID, "customer.address.street").send_keys("Av. Siempre Viva 742")
    driver.find_element(By.ID, "customer.address.city").send_keys("San Miguel de Tucuman")
    driver.find_element(By.ID, "customer.address.state").send_keys("Tucuman")
    driver.find_element(By.ID, "customer.address.zipCode").send_keys("4000")
    driver.find_element(By.ID, "customer.phoneNumber").send_keys("3813000000")
    driver.find_element(By.ID, "customer.ssn").send_keys("123456789")
    driver.find_element(By.ID, "customer.username").send_keys(username)
    driver.find_element(By.ID, "customer.password").send_keys(password)
    driver.find_element(By.ID, "repeatedPassword").send_keys(password)

    driver.find_element(By.CSS_SELECTOR, "input[value='Register']").click()

    # ParaBank, al registrar, loguea automaticamente y redirige a la pantalla
    # de resumen de cuentas.
    assert "/overview.htm" in driver.current_url
    titulo = driver.find_element(By.CSS_SELECTOR, "h1.title").text
    assert "Accounts Overview" in titulo

    # Cerramos sesion para poder probar el login manual con el mismo usuario
    driver.find_element(By.LINK_TEXT, "Log Out").click()

    # Ahora probamos el login "de verdad" con el usuario recien creado
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "input[value='Log In']").click()

    assert "/overview.htm" in driver.current_url
    titulo_login = driver.find_element(By.CSS_SELECTOR, "h1.title").text
    assert "Accounts Overview" in titulo_login


def test_login_credenciales_invalidas(driver, base_url):
    driver.get(f"{base_url}/index.htm")

    driver.find_element(By.NAME, "username").send_keys("usuario_que_no_existe")
    driver.find_element(By.NAME, "password").send_keys("password-incorrecto")
    driver.find_element(By.CSS_SELECTOR, "input[value='Log In']").click()

    # No debe haber logueado: se queda fuera de /overview.htm
    assert "/overview.htm" not in driver.current_url

    # ParaBank muestra un mensaje de error visible en el panel de login
    assert "could not be verified" in driver.page_source
