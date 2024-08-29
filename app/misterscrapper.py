import logging
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import json

# Configuración de logging
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)

# Obtén la fecha actual para el nombre del archivo de log
date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = os.path.join(log_folder, f'app_{date_str}.log')

# Configura el archivo de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(log_file),
    logging.StreamHandler()
])

# Contador global para numerar las capturas de pantalla
screenshot_counter = 1

def capture_screenshot(driver, step_name):
    """Hace una captura de pantalla y la guarda con el nombre del paso."""
    global screenshot_counter
    folder = "/screenshots"  # Ruta del volumen montado
    os.makedirs(folder, exist_ok=True)
    file_name = os.path.join(folder, f"{screenshot_counter:03d}_{step_name}.png")
    driver.save_screenshot(file_name)
    logging.info(f"Captura de pantalla guardada como {file_name}")
    screenshot_counter += 1

def wait_for_element(driver, by, value, timeout=20, clickable=False):
    """Esperar a que un elemento sea visible o clickeable."""
    if clickable:
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

def MisterLogin(driver, email, password):
    login_url = f"https://mister.mundodeportivo.com/new-onboarding/auth/email/sign-in?email={email}"
    driver.get(login_url)
    capture_screenshot(driver, "login_page_loaded")

    try:
        password_field = wait_for_element(driver, By.XPATH, "//input[@type='password']")
        password_field.send_keys(password)
        capture_screenshot(driver, "password_field_filled")

        login_button = wait_for_element(driver, By.XPATH, "//button[@type='submit']", clickable=True)
        login_button.click()
        capture_screenshot(driver, "login_button_clicked")

        WebDriverWait(driver, 20).until(
            EC.url_contains("https://mister.mundodeportivo.com")
        )
        capture_screenshot(driver, "home_page_after_login")
        logging.info("Inicio de sesión exitoso.")
    except Exception as e:
        capture_screenshot(driver, "login_error")
        logging.error(f"Error en el login: {e}")

def get_all_jornadas(driver):
    try:
        select_element = wait_for_element(driver, By.CSS_SELECTOR, "div.panel-gameweek select")
        options = select_element.find_elements(By.TAG_NAME, "option")
        jornadas = [option.get_attribute("value") for option in options if option.get_attribute("value")]
        logging.info(f"Jornadas encontradas: {jornadas}")
        capture_screenshot(driver, "jornadas_fetched")
        return jornadas
    except Exception as e:
        capture_screenshot(driver, "jornadas_error")
        logging.error(f"Error al obtener las jornadas: {e}")
        return []

def MisterStandingsForJornada(driver, jornada):
    standings_data = {}
    try:
        select_element = wait_for_element(driver, By.CSS_SELECTOR, "div.panel-gameweek select")

        driver.execute_script(f"""
        var select = document.querySelector('div.panel-gameweek select');
        select.value = '{jornada}';
        var event = new Event('change', {{ bubbles: true }});
        select.dispatchEvent(event);
        """)

        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.panel-gameweek ul.user-list li"))
        )

        selected_jornada = driver.execute_script("return document.querySelector('div.panel-gameweek select').value")
        if selected_jornada != jornada:
            logging.warning(f"Advertencia: Se esperaba la jornada {jornada}, pero la jornada seleccionada es {selected_jornada}.")

        capture_screenshot(driver, f"jornada_selected_{jornada}")

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
                logging.error(f"Error al procesar un elemento de usuario: {e}")

    except Exception as e:
        capture_screenshot(driver, f"standings_error_{jornada}")
        logging.error(f"Error al extraer los standings para la jornada {jornada}: {e}")

    return standings_data

def UpdateMisterData():
    success = False
    load_dotenv()
    email = os.getenv("MISTER_USERNAME")
    password = os.getenv("MISTER_PASSWORD")

    if not email or not password:
        logging.error("Las variables de entorno USERNAME y/o PASSWORD no están definidas.")
        return success, {}

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    
    # Configura el servicio de ChromeDriver con webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        MisterLogin(driver, email, password)
        
        driver.get("https://mister.mundodeportivo.com/standings")
        capture_screenshot(driver, "standings_page_loaded")
        
        jornadas = get_all_jornadas(driver)

        all_standings = {}

        for jornada in jornadas:
            standings = MisterStandingsForJornada(driver, jornada)
            for player, jornada_data in standings.items():
                if player not in all_standings:
                    all_standings[player] = {}
                all_standings[player].update(jornada_data)

        logging.info("Datos obtenidos:")
        logging.info(json.dumps(all_standings, indent=4))
        success = True

    except Exception as e:
        capture_screenshot(driver, "update_error")
        logging.error(f"Error durante la actualización de datos: {e}")

    finally:
        driver.quit()

    return success, all_standings

if __name__ == "__main__":
    success, standings = UpdateMisterData()
    logging.info(f"Actualización completada. Éxito: {success}")
