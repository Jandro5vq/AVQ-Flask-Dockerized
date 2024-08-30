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
import time
import random

# Configuración de logging
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
date_str = datetime.now().strftime("%d-%m-%Y")
log_file = os.path.join(log_folder, f'app_{date_str}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
)

screenshot_counter = 1

def capture_screenshot(driver, step_name):
    """Captura una imagen de la pantalla y la guarda con un nombre basado en el paso actual."""
    global screenshot_counter
    folder = "screenshots"
    os.makedirs(folder, exist_ok=True)
    file_name = os.path.join(folder, f"{screenshot_counter:03d}_{step_name}.png")
    driver.save_screenshot(file_name)
    logging.info(f"Captura de pantalla guardada como {file_name}")
    screenshot_counter += 1

def wait_for_element(driver, by, value, timeout=20, clickable=False):
    """Espera a que un elemento sea visible o clickeable en la página."""
    if clickable:
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

def login_to_mister(driver, email, password):
    """Inicia sesión en la plataforma Mister usando las credenciales proporcionadas."""
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
            EC.url_contains("https://mister.mundodeportivo.com/feed")
        )
        capture_screenshot(driver, "home_page_after_login")
        logging.info("Inicio de sesión exitoso.")
    except Exception as e:
        capture_screenshot(driver, "login_error")
        logging.error(f"Error durante el inicio de sesión: {e}")

def select_general_standings(driver):
    """Accede a la página de standings y selecciona la clasificación general."""
    driver.get("https://mister.mundodeportivo.com/standings")
    WebDriverWait(driver, 20).until(
        EC.url_contains("https://mister.mundodeportivo.com/standings")
    )
    capture_screenshot(driver, "standings_page_loaded")
    logging.info(f"Página de standings cargada: {driver.current_url}")

    general_btn = driver.find_element(By.XPATH, '//*[@id="inner-content"]/div[1]/div[1]/div/button[1]')
    general_btn.click()
    time.sleep(1)
    capture_screenshot(driver, "general_standings_loaded")
    logging.info("Clasificación general seleccionada.")

def select_jornada_standings(driver):
    """Accede a la página de standings y selecciona la clasificación de jornadas."""
    driver.get("https://mister.mundodeportivo.com/standings")
    WebDriverWait(driver, 20).until(
        EC.url_contains("https://mister.mundodeportivo.com/standings")
    )
    capture_screenshot(driver, "standings_page_loaded")
    logging.info(f"Página de standings cargada: {driver.current_url}")

    jornada_btn = driver.find_element(By.XPATH, '//*[@id="inner-content"]/div[1]/div[1]/div/button[2]')
    jornada_btn.click()
    time.sleep(1)
    capture_screenshot(driver, "jornada_standings_loaded")
    logging.info("Clasificación de jornadas seleccionada.")

def get_user_list(driver):
    """Genera una lista de usuarios con sus imágenes de perfil."""
    name_mapping = {
        'Endika Arocena Cartagena': 'Endika',
        '20130': 'Yago',
        'Ander': 'Ander',
        'Patricia': 'Patricia',
        'Galdun': 'Aitor',
        'YOWNETA': 'Lander',
        'Al3eXx': 'Alex',
        'Odei J': 'Odei',
        'Jandro': 'Alejandro',
    }
    user_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.user-list li')

    users = []

    for user_element in user_elements:
        user_info = {}
        
        name = user_element.find_element(By.CSS_SELECTOR, 'div.name').text.strip()
        if name:
            user_info['name'] = name_mapping.get(name, name)
            user_info['username'] = name
            
            try:
                img_element = user_element.find_element(By.CSS_SELECTOR, 'div.pic img')
                img_url = img_element.get_attribute('src')
            except:
                img_url = None
                span_element = user_element.find_element(By.CSS_SELECTOR, 'div.pic span')
                color = random.randrange(0, 2**24)
                hex_color = hex(color)[2:].zfill(6)
                img_url = f'https://ui-avatars.com/api/?background={hex_color}&color=fff&name={span_element.text.strip()}'
            
            user_info['profile_image'] = img_url
            
            users.append(user_info)
        
    logging.info(json.dumps(users, indent=4))
    return users

def get_jornada_codes(driver):
    """Obtiene los códigos de las jornadas disponibles en el dropdown."""
    options = driver.find_elements(By.CSS_SELECTOR, "div.panel.panel-gameweek select option")

    jornada_codes = []

    for option in options:
        jornada_code = option.get_attribute("value")
        jornada_codes.append(jornada_code)
    
    logging.info(json.dumps(jornada_codes, indent=4))
    return jornada_codes

def get_jornada_points(driver):
    """Obtiene los puntos de los usuarios para la jornada actual."""
    user_elements = driver.find_elements(By.CSS_SELECTOR, "ul.user-list li")

    user_points = []

    for user_element in user_elements:
        name = user_element.find_element(By.CSS_SELECTOR, "div.info .name").text.strip()
        if name:
            position = user_element.find_element(By.CSS_SELECTOR, "div.position").text.strip()
            points = user_element.find_element(By.CSS_SELECTOR, "div.points").text.strip()
            
            user_points.append({"position": position, "username": name, "points": points})
    
    return user_points

def load_jornada(driver, code):
    """Carga una jornada específica y toma una captura de pantalla."""
    driver.get(f"https://mister.mundodeportivo.com/standings?gw={code}")
    time.sleep(1)
    jornada_btn = driver.find_element(By.XPATH, '//*[@id="inner-content"]/div[1]/div[1]/div/button[2]')
    jornada_btn.click()
    time.sleep(1)
    logging.info(f"Clasificación de jornada cargada para el código: {code}")
    logging.info(f'URL de la jornada: {driver.current_url}')
    capture_screenshot(driver, f"jornada_{code}_loaded")

# ==== FUNCIONES PRINCIPALES ====
def get_player_list():
    """Recoge la lista de jugadores y sus imágenes de perfil."""
    success = False
    load_dotenv()
    email = os.getenv("MISTER_USERNAME")
    password = os.getenv("MISTER_PASSWORD")

    if not email or not password:
        logging.error("Las variables de entorno MISTER_USERNAME y/o MISTER_PASSWORD no están definidas.")
        return success, []

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        login_to_mister(driver, email, password)
        select_general_standings(driver)
        user_list = get_user_list(driver)
        success = True if user_list else False
    except Exception as e:
        capture_screenshot(driver, "player_list_error")
        logging.error(f"Error al recoger la lista de jugadores: {e}")
    finally:
        driver.quit()
    
    return success, user_list

def get_all_jornada_points():
    """Recoge los puntos de todas las jornadas disponibles."""
    success = False
    load_dotenv()
    email = os.getenv("MISTER_USERNAME")
    password = os.getenv("MISTER_PASSWORD")

    if not email or not password:
        logging.error("Las variables de entorno MISTER_USERNAME y/o MISTER_PASSWORD no están definidas.")
        return success, []

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        login_to_mister(driver, email, password)
        select_jornada_standings(driver)
        
        jornada_codes = get_jornada_codes(driver)
        jornada_points = []
        
        for code in jornada_codes:
            load_jornada(driver, code)
            jornada_points.append(get_jornada_points(driver))
        
        logging.info(json.dumps(jornada_points, indent=4))
        success = True if jornada_points else False
    except Exception as e:
        capture_screenshot(driver, "jornada_points_error")
        logging.error(f"Error al recoger los puntos de las jornadas: {e}")
    finally:
        driver.quit()
    
    return success, jornada_points