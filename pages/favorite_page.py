"""
Favorites Page Object
"""

import allure
import re
from pages.base_page import BasePage
from config.settings import Config
from utils import allure_attach


class FavoritePage(BasePage):
    """Favorites/Wishlist page"""

    # Locators
    PRODUCT_CARD = ".product-card"
    EMPTY_FAVORITE_MESSAGE = ".empty-message, .favorite-empty, .lead:has-text('empty')"
    FIRST_PRODUCT_NAME = f"{PRODUCT_CARD}:first-child .product-card__name a"
    FAVORITE_CONTAINER = ".page-favorite"

    def open_favorite(self):
        """Open favorites page with DOM load only"""
        with allure.step("Open favorites page"):
            self.safe_goto(Config.FAVORITE_URL, wait_until="domcontentloaded")

            assert "favorite" in self.page.url, \
                f"Failed to open favorites. Current URL: {self.page.url}"

            self.take_screenshot("Favorites page", force=True)

    def is_favorite_has_items(self) -> bool:
        """Check if favorites has items"""
        with allure.step("Check if favorites has items"):
            try:
                empty_message = self.page.locator(self.EMPTY_FAVORITE_MESSAGE).first
                if empty_message.is_visible():
                    allure_attach.attach_text("Favorites is empty", name="Info")
                    return False

                self.page.wait_for_selector(self.PRODUCT_CARD, timeout=10000)
                card_count = self.page.locator(self.PRODUCT_CARD).count()
                allure_attach.attach_text(f"Found product cards: {card_count}", name="Info")
                return card_count > 0
            except Exception as e:
                allure_attach.attach_text(f"No items in favorites: {str(e)}", name="Info")
                return False

    def get_first_product_name(self) -> str:
        """Get first product name in favorites"""
        with allure.step("Get first product name in favorites"):
            if not self.is_favorite_has_items():
                allure_attach.attach_text("No items in favorites", name="Error")
                return ""

            name_selectors = [
                self.FIRST_PRODUCT_NAME,
                f"{self.PRODUCT_CARD}:first-child a.font-weight-bold",
                f"{self.PRODUCT_CARD}:first-child .product-card__name a",
                f"{self.PRODUCT_CARD}:first-child a[href*='/id']"
            ]

            for selector in name_selectors:
                name_element = self.page.locator(selector).first
                if name_element.is_visible():
                    name = name_element.text_content()
                    if name and name.strip():
                        allure_attach.attach_text(f"First item in favorites: {name}", name="Info")
                        return name.strip()

            first_card = self.page.locator(self.PRODUCT_CARD).first
            card_html = first_card.inner_html()

            match = re.search(r'<a[^>]*>(.*?)</a>', card_html)
            if match:
                name = match.group(1).strip()
                allure_attach.attach_text(f"Name extracted from HTML: {name}", name="Info")
                return name

            allure_attach.attach_text("Failed to find product name", name="Error")
            return ""

    def get_first_product_price(self) -> str:
        """Get first product price in favorites"""
        with allure.step("Get first product price in favorites"):
            if not self.is_favorite_has_items():
                return ""

            first_card = self.page.locator(self.PRODUCT_CARD).first

            price_selectors = [
                ".product-card__now_price span",
                ".product-card__old_price span",
                ".product-card__price span"
            ]

            for selector in price_selectors:
                price_element = first_card.locator(selector).first
                if price_element.is_visible():
                    price = price_element.text_content()
                    if price:
                        allure_attach.attach_text(f"Product price: {price}", name="Info")
                        return price.strip()

            return ""

    def get_favorite_items_count(self) -> int:
        """Get number of items in favorites"""
        with allure.step("Get favorites items count"):
            count_selectors = [
                ".w-100.pl-3.pr-3",
                ".page-favorite .w-100",
                ".col-sm-12 .w-100"
            ]

            for selector in count_selectors:
                count_element = self.page.locator(selector).first
                if count_element.is_visible():
                    count_text = count_element.text_content()
                    match = re.search(r'из\s+(\d+)', count_text)
                    if match:
                        count = int(match.group(1))
                        allure_attach.attach_text(f"Total favorites count: {count}", name="Info")
                        return count

            cards = self.page.locator(self.PRODUCT_CARD).all()
            count = len(cards)
            allure_attach.attach_text(f"Items on page: {count}", name="Info")
            return count

    def get_first_product_href(self) -> str:
        """Get first product href in favorites"""
        with allure.step("Get first product href in favorites"):
            if not self.is_favorite_has_items():
                allure_attach.attach_text("No items in favorites", name="Error")
                return ""

            first_card = self.page.locator(self.PRODUCT_CARD).first

            name_link = first_card.locator(".product-card__name a").first
            if name_link.is_visible():
                href = name_link.get_attribute('href')
                allure_attach.attach_text(f"First product href: {href}", name="Info")
                return href or ""

            all_links = first_card.locator("a").all()
            for link in all_links:
                href = link.get_attribute('href')
                if href and ('/id' in href or '/product' in href or '/divan' in href):
                    allure_attach.attach_text(f"Found product href: {href}", name="Info")
                    return href

            any_link = first_card.locator("a").first
            if any_link.is_visible():
                href = any_link.get_attribute('href')
                allure_attach.attach_text(f"Any link href: {href}", name="Info")
                return href or ""

            allure_attach.attach_text("Failed to find product href", name="Error")
            return ""

    def get_product_id_from_href(self, href: str) -> str:
        """Extract product ID from href"""
        if not href:
            return ""

        match = re.search(r'/id(\d+)', href)
        if match:
            return match.group(1)

        match = re.search(r'/product/([^/]+)', href)
        if match:
            return match.group(1)

        parts = href.split('/')
        return parts[-1] if parts else ""