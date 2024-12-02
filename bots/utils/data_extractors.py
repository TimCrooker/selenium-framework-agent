from typing import Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

def extract_text_from_element(element: WebElement) -> Any:
    return element.text if element else ""

def extract_list_items(element: WebElement) -> list[str]:
    items = element.find_elements(By.TAG_NAME, 'li')
    return [item.text for item in items if item]

def extract_table_data(element: WebElement) -> list[list[str]]:
    rows = element.find_elements(By.TAG_NAME, 'tr')
    table_data = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        row_data = [cell.text for cell in cells if cell]
        table_data.append(row_data)
    return table_data

def extract_attribute_from_element(element: WebElement, attribute: Any) -> Optional[Any]:
    if element:
        return element.get_attribute(attribute)
    return None

def extract_all_links(driver: WebDriver) -> list[str]:
    links = driver.find_elements(By.TAG_NAME, 'a')
    return [link.get_attribute('href') for link in links if link.get_attribute('href')]

def extract_images(driver: WebDriver) -> list[str]:
    images = driver.find_elements(By.TAG_NAME, 'img')
    return [img.get_attribute('src') for img in images if img.get_attribute('src')]

def extract_form_inputs(form_element: WebElement) -> dict[str, str]:
    inputs = form_element.find_elements(By.TAG_NAME, 'input')
    return {input_elem.get_attribute('name'): input_elem.get_attribute('value') for input_elem in inputs if input_elem.get_attribute('name')}
