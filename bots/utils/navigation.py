from typing import Any, Literal, Optional
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
import asyncio

async def safe_navigate_to(driver: WebDriver, url: str, log_func: Any, max_retries: int =3, wait_time: int =10) -> Literal[True]:
    retries = 0
    while retries < max_retries:
        try:
            driver.get(url)
            WebDriverWait(driver, wait_time).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            return True
        except TimeoutException:
            await log_func(f"Failed to load {url}. Retrying ({retries + 1}/{max_retries})...")
            retries += 1
            await asyncio.sleep(2 ** retries)
    raise Exception(f"Failed to navigate to {url} after {max_retries} retries.")

async def click_element(driver: WebDriver, locator: Any, timeout: int =10) -> bool:
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
        element.click()
        return True
    except TimeoutException:
        return False

async def input_text(driver: WebDriver, locator: Any, text: str, timeout: int=10) -> bool:
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        element.clear()
        element.send_keys(text)
        return True
    except TimeoutException:
        return False

async def wait_for_element(driver: WebDriver, locator: Any, timeout: int=10) -> Optional[Any]:
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
        return element
    except TimeoutException:
        return None

async def scroll_to_element(driver: WebDriver, element: Any) -> None:
    driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)

async def handle_modal(driver: WebDriver, accept: bool=True, timeout: int=5) -> bool:
    try:
        WebDriverWait(driver, timeout).until(EC.alert_is_present())
        alert: Alert = driver.switch_to.alert
        if accept:
            alert.accept()
        else:
            alert.dismiss()
        return True
    except TimeoutException:
        return False
