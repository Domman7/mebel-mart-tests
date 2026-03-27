"""
Utilities for attaching screenshots and HTML to Allure reports
"""

import allure
from playwright.sync_api import Page
from config.settings import Config


def attach_screenshot(page: Page, name: str = "Screenshot"):
    """
    Takes a screenshot and attaches it to the Allure report

    Args:
        page: Playwright page object
        name: Screenshot name in the report
    """
    try:
        screenshot = page.screenshot(full_page=True, timeout=Config.SCREENSHOT_TIMEOUT)
        allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        attach_text(f"Screenshot failed: {str(e)}", name=f"{name} (error)")


def attach_page_source(page: Page, name: str = "HTML page source"):
    """
    Attaches HTML page source to the Allure report

    Args:
        page: Playwright page object
        name: Attachment name in the report
    """
    try:
        allure.attach(page.content(), name=name, attachment_type=allure.attachment_type.HTML)
    except Exception as e:
        attach_text(f"Failed to get page source: {str(e)}", name=f"{name} (error)")


def attach_url(page: Page, name: str = "Page URL"):
    """
    Attaches current page URL to the Allure report

    Args:
        page: Playwright page object
        name: Attachment name in the report
    """
    allure.attach(page.url, name=name, attachment_type=allure.attachment_type.TEXT)


def attach_text(text: str, name: str = "Information", attachment_type: str = None):
    """
    Attaches text information to the Allure report

    Args:
        text: Text content to attach
        name: Attachment name in the report
        attachment_type: Allure attachment type (defaults to TEXT)
    """
    if attachment_type is None:
        attachment_type = allure.attachment_type.TEXT
    allure.attach(text, name=name, attachment_type=attachment_type)