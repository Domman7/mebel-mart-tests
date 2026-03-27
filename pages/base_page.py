"""
Base Page Object class with common methods for all pages
"""

import allure
import time
import re
import threading
from playwright.sync_api import Page
from config.settings import Config
from utils import allure_attach
from utils.retry import retry


class BasePage:
    """Base class for all Page Object classes"""

    def __init__(self, page: Page):
        self.page = page
        self.timeout = Config.DEFAULT_TIMEOUT
        self._thread_local = threading.local()
        self._thread_local.last_screenshot_time = 0

    def safe_goto_with_retry(self, url: str, retries: int = 2):
        """
        Safe navigation with retry attempts

        Args:
            url: URL to navigate to
            retries: Number of retry attempts
        """
        for attempt in range(retries):
            try:
                with allure.step(f"Attempt {attempt + 1}: navigate to {url}"):
                    self.page.goto(url, wait_until="domcontentloaded", timeout=Config.NAVIGATION_TIMEOUT)
                    self.page.wait_for_timeout(1000)
                    return
            except Exception as e:
                if attempt == retries - 1:
                    raise
                allure.attach(f"Navigation error: {str(e)}. Retrying...",
                              name=f"Retry {attempt + 1}",
                              attachment_type=allure.attachment_type.TEXT)
                time.sleep(2)

    @retry(max_attempts=2, delay=1, exceptions=(Exception,))
    def take_screenshot(self, name: str = "Screenshot", force: bool = False):
        """
        Take screenshot and attach to report with retry on failure

        Args:
            name: Screenshot name in the report
            force: Force screenshot even if already taken recently
        """
        if force:
            try:
                screenshot = self.page.screenshot(
                    full_page=True,
                    timeout=Config.SCREENSHOT_TIMEOUT
                )
                allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
            except Exception as e:
                allure.attach(
                    f"Screenshot failed: {str(e)}",
                    name=f"{name} (error)",
                    attachment_type=allure.attachment_type.TEXT
                )
                raise

    def open(self, url: str = ""):
        """Open page with given URL or base URL"""
        with allure.step(f"Open page {url if url else Config.BASE_URL}"):
            self.page.goto(url if url else Config.BASE_URL)

    def wait_for_selector(self, selector: str, state: str = "visible", timeout: int = None):
        """
        Explicit wait for element

        Args:
            selector: CSS/XPath selector
            state: Expected state (visible, attached, hidden)
            timeout: Maximum wait time in milliseconds (uses config if None)
        """
        timeout_ms = timeout if timeout is not None else self.timeout
        self.page.locator(selector).first.wait_for(state=state, timeout=timeout_ms)

    def click(self, selector: str, description: str = ""):
        """
        Click on element with description for Allure step

        Args:
            selector: CSS/XPath selector
            description: Element description for the report
        """
        step_name = f"Click on element {description if description else selector}"
        with allure.step(step_name):
            self.wait_for_selector(selector)
            self.page.locator(selector).first.click()

    def fill(self, selector: str, value: str, description: str = ""):
        """
        Fill input field with text

        Args:
            selector: CSS/XPath selector
            value: Text to fill
            description: Field description for the report
        """
        step_name = f"Fill field {description if description else selector} with '{value}'"
        with allure.step(step_name):
            self.wait_for_selector(selector)
            self.page.locator(selector).first.fill(value)

    def get_text(self, selector: str) -> str:
        """
        Get element text

        Args:
            selector: CSS/XPath selector

        Returns:
            Element text content
        """
        self.wait_for_selector(selector)
        return self.page.locator(selector).first.text_content()

    def get_attribute(self, selector: str, attribute: str) -> str:
        """
        Get element attribute

        Args:
            selector: CSS/XPath selector
            attribute: Attribute name

        Returns:
            Attribute value
        """
        self.wait_for_selector(selector)
        return self.page.locator(selector).first.get_attribute(attribute)

    def is_visible(self, selector: str) -> bool:
        """
        Check if element is visible

        Args:
            selector: CSS/XPath selector

        Returns:
            True if element is visible, False otherwise
        """
        try:
            self.wait_for_selector(selector)
            return True
        except:
            return False

    def element_exists(self, selector: str) -> bool:
        """
        Check if element exists in DOM (not necessarily visible)

        Args:
            selector: CSS/XPath selector

        Returns:
            True if element exists, False otherwise
        """
        return self.page.locator(selector).count() > 0

    def wait_and_click(self, selector: str, description: str = "", timeout: int = 30000):
        """
        More reliable click with explicit waiting

        Args:
            selector: CSS/XPath selector
            description: Element description for the report
            timeout: Maximum wait time in milliseconds
        """
        with allure.step(f"Click on element {description if description else selector}"):
            try:
                element = self.page.locator(selector).first
                element.wait_for(state="visible", timeout=timeout)
                element.wait_for(state="attached", timeout=timeout)
                element.scroll_into_view_if_needed()
                element.click()
            except Exception as e:
                allure.attach(f"Click error: {str(e)}\nURL: {self.page.url}",
                              name="Click error",
                              attachment_type=allure.attachment_type.TEXT)
                raise

    def safe_goto(self, url: str, wait_until: str = "domcontentloaded", timeout: int = 30000):
        """
        Safe navigation with fallback to commit state

        Args:
            url: URL to navigate to
            wait_until: Wait condition (domcontentloaded, load, networkidle, commit)
            timeout: Navigation timeout in milliseconds
        """
        with allure.step(f"Navigate to page {url}"):
            try:
                self.page.goto(url, wait_until=wait_until, timeout=timeout)
                self.page.wait_for_timeout(1000)
            except Exception as e:
                allure.attach(f"Navigation error to {url}: {str(e)}",
                              name="Navigation error",
                              attachment_type=allure.attachment_type.TEXT)
                self.page.goto(url, wait_until="commit", timeout=timeout)
                self.page.wait_for_timeout(2000)