"""
test_transfer_y_cuentas.py

Borrador de automatizacion para TC07, TC08, TC09 (transferencias) y TC10
(apertura de cuenta), documentados en el Documento_Sprint2. Estos tests
estan marcados con @pytest.mark.skip porque los localizadores (los By.ID /
By.NAME de los campos de transfer.htm y openaccount.htm) todavia NO fueron
verificados contra el sistema real con el navegador abierto, a diferencia
de los tests de login/registro que si corrieron de verdad.

Para activarlos en el Sprint 3:
1. Loguearse manualmente en ParaBank y abrir DevTools (F12) en /transfer.htm
   y /openaccount.htm.
2. Confirmar el id/name real de cada campo contra lo que aca se asume.
3. Sacar el decorador @pytest.mark.skip de cada funcion.
4. Correr "pytest tests/test_transfer_y_cuentas.py -v" de forma aislada
   las primeras veces, para no mezclar fallos reales con fallos de selector.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


@pytest.mark.skip(reason="TC07: localizadores de transfer.htm pendientes de verificar contra el sistema real")
def test_transferencia_exitosa(driver, base_url, usuario_registrado):
    driver.get(f"{base_url}/transfer.htm")

    monto = driver.find_element(By.ID, "amount")
    monto.send_keys("50")

    cuentas_origen = Select(driver.find_element(By.ID, "fromAccountId"))
    cuentas_destino = Select(driver.find_element(By.ID, "toAccountId"))
    # Asume que el usuario recien registrado tiene al menos 2 cuentas;
    # si ParaBank solo da una cuenta por defecto, este caso requiere
    # primero ejecutar TC10 (abrir una segunda cuenta) antes de transferir.
    cuentas_destino.select_by_index(1)

    driver.find_element(By.CSS_SELECTOR, "input[value='Transfer']").click()

    assert "Transfer Complete" in driver.page_source


@pytest.mark.skip(reason="TC08: localizadores de transfer.htm pendientes de verificar contra el sistema real")
def test_transferencia_monto_cero(driver, base_url, usuario_registrado):
    driver.get(f"{base_url}/transfer.htm")

    driver.find_element(By.ID, "amount").send_keys("0")
    driver.find_element(By.CSS_SELECTOR, "input[value='Transfer']").click()

    # Resultado esperado a confirmar: el sistema deberia rechazar un
    # monto de 0, o como minimo no reflejar un movimiento real.
    # Este assert es un punto de partida, no una verdad confirmada todavia.
    assert "Transfer Complete" not in driver.page_source


@pytest.mark.skip(reason="TC09: localizadores de transfer.htm pendientes de verificar contra el sistema real")
def test_transferencia_supera_saldo(driver, base_url, usuario_registrado):
    driver.get(f"{base_url}/transfer.htm")

    # Monto deliberadamente alto, mayor a cualquier saldo inicial tipico
    driver.find_element(By.ID, "amount").send_keys("999999999")
    driver.find_element(By.CSS_SELECTOR, "input[value='Transfer']").click()

    # Hallazgo documentado en el Documento_Sprint2: la comunidad de QA
    # reporta que ParaBank permite sobregirar la cuenta sin validar esto.
    # Este test deberia CONFIRMAR o DESMENTIR ese hallazgo una vez activado.
    assert "Transfer Complete" not in driver.page_source


@pytest.mark.skip(reason="TC10: localizadores de openaccount.htm pendientes de verificar contra el sistema real")
def test_apertura_cuenta_nueva(driver, base_url, usuario_registrado):
    driver.get(f"{base_url}/openaccount.htm")

    tipo_cuenta = Select(driver.find_element(By.ID, "type"))
    tipo_cuenta.select_by_visible_text("SAVINGS")

    driver.find_element(By.ID, "openAccountButton").click()

    assert "Account Opened" in driver.page_source
