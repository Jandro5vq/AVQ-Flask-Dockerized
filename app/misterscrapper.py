from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv
import json

# Contador global para numerar las capturas de pantalla
screenshot_counter = 1

def capture_screenshot(driver, step_name):
    """Captura una captura de pantalla y la guarda con el nombre del paso."""
    global screenshot_counter
    folder = "screenshots"
    os.makedirs(folder, exist_ok=True)
    file_name = os.path.join(folder, f"{screenshot_counter:03d}_{step_name}.png")
    driver.save_screenshot(file_name)
    print(f"Captura de pantalla guardada como {file_name}")
    screenshot_counter += 1

def MisterLogin(driver, email, password):
    login_url = f"https://mister.mundodeportivo.com/new-onboarding/auth/email/sign-in?email={email}"
    driver.get(login_url)
    capture_screenshot(driver, "login_page_loaded")

    try:
        # Esperar a que el campo de contraseña esté presente
        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
        )
        password_field.send_keys(password)
        capture_screenshot(driver, "password_field_filled")

        # Esperar a que el botón de inicio de sesión esté presente y luego hacer clic
        login_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        login_button.click()
        capture_screenshot(driver, "login_button_clicked")

        # Esperar a que la página de inicio se cargue después del login
        WebDriverWait(driver, 20).until(
            EC.url_contains("https://mister.mundodeportivo.com")
        )
        capture_screenshot(driver, "home_page_after_login")
    except Exception as e:
        capture_screenshot(driver, "login_error")
        print(f"Error en el login: {e}")

def get_all_jornadas(driver):
    try:
        select_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.panel-gameweek select"))
        )
        options = select_element.find_elements(By.TAG_NAME, "option")
        jornadas = [option.get_attribute("value") for option in options if option.get_attribute("value")]
        print(f"Jornadas encontradas: {jornadas}")
        capture_screenshot(driver, "jornadas_fetched")
        return jornadas
    except Exception as e:
        capture_screenshot(driver, "jornadas_error")
        print(f"Error al obtener las jornadas: {e}")
        return []

def MisterStandingsForJornada(driver, jornada):
    standings_data = {}
    try:
        # Cambiar la jornada
        select_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.panel-gameweek select"))
        )
        
        # Usar JavaScript para cambiar el valor del dropdown
        driver.execute_script(f"""
        var select = document.querySelector('div.panel-gameweek select');
        select.value = '{jornada}';
        var event = new Event('change', {{ bubbles: true }});
        select.dispatchEvent(event);
        """)

        # Esperar a que la selección de la jornada sea reflejada en la página
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.panel-gameweek ul.user-list li"))
        )

        # Confirmar que la jornada seleccionada es la correcta
        selected_jornada = driver.execute_script("return document.querySelector('div.panel-gameweek select').value")
        if selected_jornada != jornada:
            print(f"Advertencia: Se esperaba la jornada {jornada}, pero la jornada seleccionada es {selected_jornada}.")

        capture_screenshot(driver, f"jornada_selected_{jornada}")

        # Esperar a que la página se actualice después de seleccionar la jornada
        time.sleep(5)  # Ajusta el tiempo según sea necesario

        user_elements = driver.find_elements(By.CSS_SELECTOR, "div.panel-gameweek ul.user-list li")

        for element in user_elements:
            try:
                position = element.find_element(By.CSS_SELECTOR, "div.position").text.strip()
                name = element.find_element(By.CSS_SELECTOR, "div.info .name").text.strip()
                points = element.find_element(By.CSS_SELECTOR, "div.points").text.strip().split('\n')[0]

                if name not in standings_data:
                    standings_data[name] = {}
                    
                standings_data[name][jornada] = {
                    "position": position,
                    "points": points
                }
            except Exception as e:
                capture_screenshot(driver, f"user_element_error_{jornada}")
                print(f"Error al procesar un elemento de usuario: {e}")

    except Exception as e:
        capture_screenshot(driver, f"standings_error_{jornada}")
        print(f"Error al extraer los standings para la jornada {jornada}: {e}")

    return standings_data

def UpdateMisterData():
    success = False
    load_dotenv()
    email = os.getenv("MISTER_USERNAME")
    password = os.getenv("MISTER_PASSWORD")

    if not email or not password:
        print("Las variables de entorno USERNAME y/o PASSWORD no están definidas.")
        return success, {}

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    try:
        MisterLogin(driver, email, password)
        time.sleep(5)
        
        driver.get("https://mister.mundodeportivo.com/standings")
        capture_screenshot(driver, "standings_page_loaded")
        time.sleep(5)
        
        jornadas = get_all_jornadas(driver)

        all_standings = {}

        for jornada in jornadas:
            standings = MisterStandingsForJornada(driver, jornada)
            for player, jornada_data in standings.items():
                if player not in all_standings:
                    all_standings[player] = {}
                all_standings[player].update(jornada_data)

        print("Datos obtenidos:")
        print(json.dumps(all_standings, indent=4))
        success = True

    except Exception as e:
        capture_screenshot(driver, "update_error")
        print(f"Error durante la actualización de datos: {e}")

    finally:
        driver.quit()

    return success, all_standings

if __name__ == "__main__":
    success, standings = UpdateMisterData()
    print(f"Actualización completada. Éxito: {success}")
