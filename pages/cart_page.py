"""
Cart Page Object
"""

import allure
import re
from pages.base_page import BasePage
from config.settings import Config
from utils import allure_attach


class CartPage(BasePage):
    """Shopping cart page"""

    # Locators
    CART_CONTAINER = "#cartWidget"
    CART_ITEM = ".list-group-item"
    CART_ITEM_NAME = f"{CART_ITEM} a.font-weight-bold"
    CART_ITEM_PRICE = f"{CART_ITEM} .col-md-2.py-2"
    EMPTY_CART_MESSAGE = ".lead:has-text('Cart is empty')"
    TOTAL_PRICE = "h2:has-text('Total:')"

    def open_cart(self):
        """Open cart page"""
        with allure.step("Open cart"):
            self.safe_goto(Config.CART_URL, wait_until="domcontentloaded")
            self.page.wait_for_timeout(1000)

    def is_cart_not_empty(self) -> bool:
        """Check if cart is not empty"""
        try:
            self.page.wait_for_selector(self.CART_ITEM, timeout=5000)
            return True
        except:
            return False

    def get_first_item_name(self) -> str:
        """Get first item name in cart"""
        if self.is_cart_not_empty():
            name_element = self.page.locator(self.CART_ITEM_NAME).first
            if name_element.is_visible():
                name = name_element.text_content()
                allure_attach.attach_text(f"First item in cart: {name}", name="Info")
                return name or ""
        return ""

    def get_first_item_price(self) -> str:
        """Get first item price in cart"""
        if self.is_cart_not_empty():
            with allure.step("Get first item price in cart"):
                first_item = self.page.locator(self.CART_ITEM).first
                price_elements = first_item.locator(".col-md-2.py-2").all()

                allure_attach.attach_text(f"Found price elements: {len(price_elements)}", name="Debug")

                for i, elem in enumerate(price_elements):
                    if elem.is_visible():
                        text = elem.text_content() or ""
                        allure_attach.attach_text(f"Element {i}: '{text}'", name="Debug")

                        if '₽' in text:
                            price_clean = re.sub(r'[^\d]', '', text)
                            allure_attach.attach_text(f"Found price: {price_clean}", name="Info")
                            return price_clean

                item_text = first_item.text_content() or ""
                allure_attach.attach_text(f"Full item text: {item_text}", name="Debug")

                match = re.search(r'(\d[\d\s]*)₽', item_text)
                if match:
                    price_clean = re.sub(r'[^\d]', '', match.group(1))
                    allure_attach.attach_text(f"Price via regex: {price_clean}", name="Info")
                    return price_clean

                numbers = re.findall(r'(\d[\d\s]*)', item_text)
                if len(numbers) >= 2:
                    price_clean = re.sub(r'[^\d]', '', numbers[1])
                    allure_attach.attach_text(f"Assumed price: {price_clean}", name="Info")
                    return price_clean

                allure_attach.attach_text("Price not found", name="Error")
        return "0"

    def get_total_price(self) -> str:
        """Get total cart price"""
        with allure.step("Get total cart price"):
            total_element = self.page.locator(self.TOTAL_PRICE).first
            if total_element.is_visible():
                total_text = total_element.text_content() or ""
                match = re.search(r'([\d\s]+)₽', total_text)
                if match:
                    total_clean = re.sub(r'[^\d]', '', match.group(1))
                    allure_attach.attach_text(f"Total price: {total_clean}", name="Info")
                    return total_clean
            return "0"