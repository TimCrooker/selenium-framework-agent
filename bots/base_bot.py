import base64
import os
import time
import psutil

from abc import ABC, abstractmethod
from typing import Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.webdriver import WebDriver

from app.models import CreateRunEvent, CreateRunLog, LogLevel

from .utils.navigation import click_element, input_text, wait_for_element
from app.utils.run_communicator import RunCommunicator

class BaseBot(ABC):
    def __init__(self, run_id: str, communicator: RunCommunicator, selenium_remote_url: str) -> None:
        self.run_id = run_id
        self.start_time = time.time()

        self.communicator: RunCommunicator = communicator
        self.selenium_remote_url = selenium_remote_url
        self.logger = None
        self.driver: WebDriver = self._get_driver()

    def _get_driver(self) -> WebDriver:
        options = Options()
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

        driver = webdriver.Remote(
            command_executor=self.selenium_remote_url,
            desired_capabilities=DesiredCapabilities.CHROME.copy(),
            options=options
        )

        return driver

    @abstractmethod
    async def run(self) -> None:
        pass

    def _get_stack_trace(self) -> str:
        import traceback
        return traceback.format_exc()

    async def handle_error(self, error: Exception) -> None:
        payload = {
            "error": str(error),
            "stack_trace": self._get_stack_trace()
        }
        screenshot_base64 = await self.capture_screenshot()
        await self.send_run_event(
            event_type="error",
            message="An error occurred",
            payload=payload,
            screenshot=screenshot_base64
        )
        await self.teardown()

    async def teardown(self) -> None:
        if self.driver:
            self.driver.quit()

    async def capture_screenshot(self) -> Optional[str]:
        try:
            screenshot = self.driver.get_screenshot_as_png()
            return base64.b64encode(screenshot).decode('utf-8')
        except Exception as e:
            await self.send_run_log(
                message=f"Failed to capture screenshot: {str(e)}"
            )
            return None

    async def capture_system_metrics(self) -> Optional[dict]:
        try:
            process = psutil.Process(os.getpid())
            cpu_usage = psutil.cpu_percent()
            memory_info = process.memory_info()
            memory_usage = memory_info.rss / (1024 * 1024)
            return {'cpu_usage': cpu_usage, 'memory_usage_mb': memory_usage}
        except Exception as e:
            await self.send_run_log(
                message=f"Failed to capture system metrics: {str(e)}"
            )
            return None

    async def send_run_log(self, message: str, level: LogLevel = LogLevel.INFO, payload: Optional[dict] = None) -> None:
        await self.communicator.send_run_log(CreateRunLog(
            level=level,
            message=message,
            payload=payload
        ))

    async def send_run_event(self, event_type: str, message: str, payload: Optional[dict] = None, screenshot: Optional[str] = None) -> None:
        await self.communicator.send_run_event(CreateRunEvent(
            event_type=event_type,
            message=message,
            payload=payload,
            screenshot=screenshot
        ))

    async def wait_and_click(self, locator: Any, timeout: int = 10) -> None:
        result = await click_element(self.driver, locator, timeout)
        if not result:
            await self.send_run_log(message=f"Failed to click element: {locator}")

    async def wait_and_input_text(self, locator: Any, text: str, timeout: int = 10) -> None:
        result = await input_text(self.driver, locator, text, timeout)
        if not result:
            await self.send_run_log(message=f"Failed to input text into element: {locator}")

    async def wait_for_element_presence(self, locator: Any, timeout: int = 10) -> Optional[Any]:
        element = await wait_for_element(self.driver, locator, timeout)
        if not element:
            await self.send_run_log(message=f"Element not found: {locator}")
        return element

    async def capture_state(self) -> None:
        screenshot_base64 = await self.capture_screenshot()
        await self.send_run_event(message="Captured current state", event_type='state_capture', screenshot=screenshot_base64)
