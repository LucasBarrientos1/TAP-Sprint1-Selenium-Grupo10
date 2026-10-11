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

Dos bugs reales que encontramos y corregimos durante el Sprint 2 (quedan
documentados tambien en la Bitacora y en el Documento_Sprint2):

1) SSN repetido: usar un SSN fijo ("123456789") funciona la PRIMERA vez que
   se corre el test, pero falla en corridas siguientes porque ParaBank es un
   sitio publico y persistente: ese SSN queda "gastado" para siempre. La
   solucion es generar un SSN unico por corrida, igual que ya haciamos con
   el username.

2) Problema de sincronizacion (timing): justo despues de hacer click en un
   boton que envia un formulario, el navegador todavia esta procesando la
   respuesta del servidor. Si Selenium chequea la pagina en ese instante
   (sin esperar), puede leer todavia la pagina VIEJA y el test falla con un
   resultado que parece incorrecto pero en realidad es solo una carrera
   contra el tiempo. La solucion es usar WebDriverWait para esperar
   explicitamente a que aparezca una condicion real (la URL cambio, o el
   mensaje de error ya esta en el HTML) antes de hacer cualquier assert.
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def _generar_username_unico():
    return f"grupo10qa{int(time.time() * 1000)}"


def _generar_ssn_unico():
    # Tomamos los ultimos 9 digitos del timestamp en milisegundos para que
    # nunca se repita entre corridas, ni siquiera corriendo dos veces seguidas.
    return str(int(time.time() * 1000))[-9:]


def _generar_telefono_unico():
    # Mismo problema que con el SSN: ParaBank tambien rechaza en silencio
    # un numero de telefono ya usado antes. Lo generamos unico por corrida.
    return "381" + str(int(time.time() * 1000))[-7:]


def test_registro_y_login_exitoso(driver, base_url):
    username = _generar_username_unico()
    password = "Passw0rd!2026"
    ssn = _generar_ssn_unico()

    driver.get(f"{base_url}/register.htm")

    driver.find_element(By.ID, "customer.firstName").send_keys("Alexis")
    driver.find_element(By.ID, "customer.lastName").send_keys("Zelaya")
    driver.find_element(By.ID, "customer.address.street").send_keys("Av. Siempre Viva 742")
    driver.find_element(By.ID, "customer.address.city").send_keys("San Miguel de Tucuman")
    driver.find_element(By.ID, "customer.address.state").send_keys("Tucuman")
    driver.find_element(By.ID, "customer.address.zipCode").send_keys("4000")
    driver.find_element(By.ID, "customer.phoneNumber").send_keys(_generar_telefono_unico())
    driver.find_element(By.ID, "customer.ssn").send_keys(ssn)
    driver.find_element(By.ID, "customer.username").send_keys(username)
    driver.find_element(By.ID, "customer.password").send_keys(password)
    driver.find_element(By.ID, "repeatedPassword").send_keys(password)

    driver.find_element(By.CSS_SELECTOR, "input[value='Register']").click()

    # Esperamos explicitamente a que la pagina termine de procesar el
    # registro, en vez de asumir que ya curso.
    WebDriverWait(driver, 10).until(
        lambda d: "/overview.htm" in d.current_url or "error" in d.page_source.lower()
    )

    # ParaBank, al registrar, loguea automaticamente y redirige a la pantalla
    # de resumen de cuentas.
    if "/overview.htm" not in driver.current_url:
        # Diagnostico: en vez de fallar a ciegas, juntamos los mensajes de
        # error reales que ParaBank muestra junto a cada campo del
        # formulario, para saber EXACTAMENTE cual esta rechazando.
        errores = driver.find_elements(By.CSS_SELECTOR, ".error, span.error, .errors")
        textos_error = [e.text for e in errores if e.text.strip()]
        raise AssertionError(
            f"El registro no redirigio a overview.htm. URL actual: {driver.current_url}\n"
            f"Mensajes de error encontrados en la pagina: {textos_error}\n"
            f"Si la lista esta vacia, revisar manualmente register.htm con el navegador abierto."
        )
    titulo = driver.find_element(By.CSS_SELECTOR, "h1.title").text
    assert "Accounts Overview" in titulo

    # Cerramos sesion para poder probar el login manual con el mismo usuario
    driver.find_element(By.LINK_TEXT, "Log Out").click()
    WebDriverWait(driver, 10).until(lambda d: "index.htm" in d.current_url)

    # Ahora probamos el login "de verdad" con el usuario recien creado
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "input[value='Log In']").click()

    WebDriverWait(driver, 10).until(
        lambda d: "/overview.htm" in d.current_url or "could not be verified" in d.page_source
    )

    assert "/overview.htm" in driver.current_url
    titulo_login = driver.find_element(By.CSS_SELECTOR, "h1.title").text
    assert "Accounts Overview" in titulo_login


def test_login_credenciales_invalidas(driver, base_url):
    driver.get(f"{base_url}/index.htm")

    driver.find_element(By.NAME, "username").send_keys("usuario_que_no_existe")
    driver.find_element(By.NAME, "password").send_keys("password-incorrecto")
    driver.find_element(By.CSS_SELECTOR, "input[value='Log In']").click()

    # Esperamos a que el servidor responda, en vez de chequear al instante
    # (esto fue justamente un bug real que encontramos: sin esta espera, el
    # test leia la pagina de login todavia sin procesar).
    WebDriverWait(driver, 10).until(
        lambda d: "/overview.htm" in d.current_url or "could not be verified" in d.page_source
    )

    # No debe haber logueado: se queda fuera de /overview.htm
    assert "/overview.htm" not in driver.current_url

    # ParaBank muestra un mensaje de error visible en el panel de login
    assert "could not be verified" in driver.page_source


def test_login_password_vacio(driver, base_url, usuario_registrado):
    """
    TC03 (Sprint 2) - Analisis de valores limite: la contrasena vacia es el
    borde inferior del rango de longitud valida (0 caracteres).
    """
    driver.find_element(By.LINK_TEXT, "Log Out").click()
    WebDriverWait(driver, 10).until(lambda d: "index.htm" in d.current_url)

    driver.find_element(By.NAME, "username").send_keys(usuario_registrado["username"])
    # A proposito NO completamos el campo password
    driver.find_element(By.CSS_SELECTOR, "input[value='Log In']").click()

    WebDriverWait(driver, 10).until(
        lambda d: "/overview.htm" in d.current_url or "could not be verified" in d.page_source
    )

    assert "/overview.htm" not in driver.current_url


def test_registro_campos_vacios(driver, base_url):
    """
    TC05 (Sprint 2) - Particion de equivalencia: clase invalida por datos
    faltantes.
    """
    driver.get(f"{base_url}/register.htm")

    driver.find_element(By.CSS_SELECTOR, "input[value='Register']").click()

    WebDriverWait(driver, 10).until(
        lambda d: "/overview.htm" in d.current_url or "required" in d.page_source.lower()
    )

    assert "/overview.htm" not in driver.current_url
    assert "required" in driver.page_source.lower()


def test_registro_usuario_duplicado(driver, base_url, usuario_registrado):
    """
    TC06 (Sprint 2) - Analisis de valores limite: la colision EXACTA de un
    username que ya existe es el caso borde de la regla de unicidad.
    """
    driver.find_element(By.LINK_TEXT, "Log Out").click()
    WebDriverWait(driver, 10).until(lambda d: "index.htm" in d.current_url)

    driver.get(f"{base_url}/register.htm")
    driver.find_element(By.ID, "customer.firstName").send_keys("Otro")
    driver.find_element(By.ID, "customer.lastName").send_keys("Usuario")
    driver.find_element(By.ID, "customer.address.street").send_keys("Otra Calle 123")
    driver.find_element(By.ID, "customer.address.city").send_keys("San Miguel de Tucuman")
    driver.find_element(By.ID, "customer.address.state").send_keys("Tucuman")
    driver.find_element(By.ID, "customer.address.zipCode").send_keys("4000")
    driver.find_element(By.ID, "customer.phoneNumber").send_keys(_generar_telefono_unico())
    # SSN distinto al del usuario original (y unico), para que la UNICA
    # variable que coincide sea el username: asi probamos exactamente la
    # regla que queremos (unicidad de username), sin mezclar con la de SSN.
    driver.find_element(By.ID, "customer.ssn").send_keys(_generar_ssn_unico())
    # A proposito usamos el MISMO username que ya registro el fixture
    driver.find_element(By.ID, "customer.username").send_keys(usuario_registrado["username"])
    driver.find_element(By.ID, "customer.password").send_keys("OtraPassword!123")
    driver.find_element(By.ID, "repeatedPassword").send_keys("OtraPassword!123")
    driver.find_element(By.CSS_SELECTOR, "input[value='Register']").click()

    WebDriverWait(driver, 10).until(
        lambda d: "/overview.htm" in d.current_url or "already exists" in d.page_source.lower()
    )

    # No debe haber creado una segunda cuenta con el mismo username
    assert "/overview.htm" not in driver.current_url
    assert "already exists" in driver.page_source.lower()
