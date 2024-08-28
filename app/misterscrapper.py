from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from dotenv import load_dotenv
import os

def UpdateMisterData():
    success = False
    load_dotenv()
    username_str = os.getenv('USERNAME')
    password_str = os.getenv('PASSWORD')

    # Configurar Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    try:
        # LOGIN
        driver.get('https://example.com/login')
        time.sleep(3)

        username = driver.find_element(By.NAME, 'username')
        password = driver.find_element(By.NAME, 'password')
        username.send_keys(username_str)
        password.send_keys(password_str)
        password.send_keys(Keys.RETURN)

        time.sleep(5)

        # JORNADAS
        driver.get('https://example.com/datos')

        datos = driver.find_element(By.XPATH, '//div[@id="datos"]')
        print(datos.text)
        success = True

    except:
        success = False

    finally:
        driver.quit()

    return success
