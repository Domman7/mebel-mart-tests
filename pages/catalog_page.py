"""
Catalog page Page Object for sofas listing
"""

import allure
import re
from typing import List, Optional
from pages.base_page import BasePage
from config.settings import Config
from utils import allure_attach


class CatalogPage(BasePage):
    """Sofas catalog page"""

    # Locators
    TITLE = "h1"

    # Product card locators
    PRODUCT_CARD = ".product-card"
    PRODUCT_LINK = f"{PRODUCT_CARD} .product-card__name a"
    PRODUCT_PRICE_NOW = f"{PRODUCT_CARD} .product-card__now_price span"
    PRODUCT_PRICE_OLD = f"{PRODUCT_CARD} .product-card__old_price span"
    PRODUCT_FAVORITE_ICON = f"{PRODUCT_CARD} .product-card__favorites .favorite-icon"
    PRODUCT_ADD_TO_CART_BTN = f"{PRODUCT_CARD} .btn-primary.btn-block"

    # Filter locators
    FILTER_APPLY_BTN = "a#filterLinkContainer, .filter__link"
    PRODUCTS_COUNT_TEXT = ".w-100.pl-3.pr-3"

    def open_catalog(self):
        """Open sofas catalog with wait for products"""
        with allure.step("Open sofas catalog"):
            self.open(Config.CATALOG_URL)
            self.page.wait_for_timeout(500)
            self.wait_for_selector(self.PRODUCT_CARD)
            self.take_screenshot("Catalog opened", force=True)
            self.page.wait_for_timeout(500)

    def get_page_title(self) -> str:
        """Get page title"""
        title_element = self.page.locator("h1").first
        if title_element.is_visible():
            title = title_element.text_content()
            allure_attach.attach_text(f"Page title: {title}", name="Info")
            return title or ""
        return ""

    def apply_price_filter(self, price_from: str, price_to: str):
        """
        Apply price filter via URL

        Args:
            price_from: Minimum price value
            price_to: Maximum price value
        """
        with allure.step(f"Apply price filter: from {price_from} to {price_to}"):
            # Screenshot before filter
            self.take_screenshot("Before filter application", force=True)

            current_url = self.page.url
            if '?' in current_url:
                base_url = current_url.split('?')[0]
            else:
                base_url = current_url

            filter_url = f"{base_url}?price={price_from}-{price_to}"

            allure_attach.attach_text(f"Filter URL: {filter_url}", name="Info")

            try:
                self.page.goto(filter_url, wait_until="domcontentloaded", timeout=30000)
                self.page.wait_for_timeout(2000)
                self.page.wait_for_selector(self.PRODUCT_CARD, timeout=10000)

                # Screenshot after filter
                self.take_screenshot("After filter application", force=True)

            except Exception as e:
                self.take_screenshot("Error during filter application", force=True)
                allure_attach.attach_text(f"Filter error: {str(e)}", name="Error")
                raise

            assert f"price={price_from}-{price_to}" in self.page.url, \
                f"Filter not applied. Current URL: {self.page.url}"

    def find_product_by_name(self, product_name: str) -> bool:
        """
        Find product by name (partial match)

        Args:
            product_name: Product name to search for

        Returns:
            True if product found, False otherwise
        """
        with allure.step(f"Find product with name '{product_name}'"):
            self.wait_for_selector(self.PRODUCT_CARD)

            product_links = self.page.locator(self.PRODUCT_LINK).all()
            found_products = []

            for i, link in enumerate(product_links, 1):
                if link.is_visible():
                    name = link.text_content()
                    if name:
                        found_products.append(f"{i}. {name}")
                        if product_name.lower() in name.lower():
                            link.scroll_into_view_if_needed()
                            self.page.wait_for_timeout(500)
                            self.take_screenshot(f"Found product: {name}", force=True)
                            allure_attach.attach_text(f"Found product #{i}: {name}", name="Info")
                            return True

            allure_attach.attach_text(
                f"Search '{product_name}'\n\nAll products on page:\n" + "\n".join(found_products),
                name="Detailed info"
            )
            return False

    def get_product_price_by_name(self, product_name: str) -> str:
        """
        Get product price by name

        Args:
            product_name: Product name to find

        Returns:
            Price string or empty string
        """
        with allure.step(f"Get price for product '{product_name}'"):
            product_cards = self.page.locator(self.PRODUCT_CARD).all()

            for card_index, card in enumerate(product_cards, 1):
                name_element = card.locator(self.PRODUCT_LINK).first
                if not name_element.is_visible():
                    continue

                name = name_element.text_content()
                if not name:
                    continue

                if product_name.lower() in name.lower():
                    allure_attach.attach_text(f"Found card #{card_index}: {name}", name="Info")
                    price = self._extract_price_from_card(card)

                    if price:
                        allure_attach.attach_text(f"Price for '{name}': {price}", name="Info")
                        return price

            raise AssertionError(f"Failed to find price for product '{product_name}'")

    def _extract_price_from_card(self, card) -> Optional[str]:
        """
        Extract price from product card using multiple methods

        Args:
            card: Product card locator

        Returns:
            Price string or None
        """
        # Method 1: current price
        price_now = card.locator(self.PRODUCT_PRICE_NOW).first
        if price_now.is_visible():
            price_text = price_now.text_content()
            if price_text:
                return price_text.strip()

        # Method 2: old price
        price_old = card.locator(self.PRODUCT_PRICE_OLD).first
        if price_old.is_visible():
            price_text = price_old.text_content()
            if price_text:
                return price_text.strip()

        # Method 3: any numbers with currency symbol
        all_text = card.text_content()
        if all_text:
            match = re.search(r'(\d[\d\s]*)\s*₽', all_text)
            if match:
                return match.group(1).strip()

        return None

    def clean_price(self, price_text: str) -> int:
        """
        Clean price from non-digit characters and convert to integer

        Args:
            price_text: Raw price text

        Returns:
            Integer price value
        """
        if not price_text:
            return 0

        cleaned = re.sub(r'[^\d]', '', price_text)
        try:
            return int(cleaned)
        except ValueError:
            return 0

    def get_all_prices_on_page(self) -> List[str]:
        """
        Get all product prices on current page

        Returns:
            List of price strings
        """
        prices = []
        product_cards = self.page.locator(self.PRODUCT_CARD).all()

        for card in product_cards:
            price = self._extract_price_from_card(card)
            if price:
                prices.append(price)

        return prices

    def get_total_products_count(self) -> int:
        """
        Get total number of products in results

        Returns:
            Total product count
        """
        try:
            count_element = self.page.locator(self.PRODUCTS_COUNT_TEXT).first
            if count_element.is_visible():
                count_text = count_element.text_content()
                if count_text:
                    match = re.search(r'из\s+(\d+)', count_text)
                    if match:
                        return int(match.group(1))
        except:
            pass

        # Fallback: count products on page
        return len(self.page.locator(self.PRODUCT_CARD).all())

    def verify_prices_in_range(self, price_from: int, price_to: int):
        """
        Verify all product prices are within specified range

        Args:
            price_from: Minimum price
            price_to: Maximum price
        """
        with allure.step(f"Verify prices in range {price_from}-{price_to}"):
            prices_in_range = []
            prices_out_of_range = []

            price_texts = self.get_all_prices_on_page()

            for i, price_text in enumerate(price_texts, 1):
                price_num = self.clean_price(price_text)
                if price_num > 0:
                    if price_from <= price_num <= price_to:
                        prices_in_range.append((i, price_text, price_num))
                    else:
                        prices_out_of_range.append((i, price_text, price_num))

            if prices_out_of_range:
                out_range_info = "\n".join([f"  Product #{i}: {text} ({num} rub.)"
                                            for i, text, num in prices_out_of_range])
                allure_attach.attach_text(f"Products out of range:\n{out_range_info}",
                                          name="⚠ Prices out of range")
                self.take_screenshot("Prices out of range detected", force=True)

            assert len(prices_out_of_range) == 0, \
                f"Found {len(prices_out_of_range)} products with price out of range {price_from}-{price_to}"

    def get_first_product_name(self) -> str:
        """Get first product name in catalog"""
        self.wait_for_selector(self.PRODUCT_CARD)
        first_product_link = self.page.locator(self.PRODUCT_LINK).first

        if first_product_link.is_visible():
            name = first_product_link.text_content()
            return name or ""
        return ""

    def get_first_product_price(self) -> str:
        """Get first product price in catalog"""
        self.wait_for_selector(self.PRODUCT_CARD)
        first_card = self.page.locator(self.PRODUCT_CARD).first
        price = self._extract_price_from_card(first_card)
        return price or "0"

    def get_first_product_href(self) -> str:
        """Get first product href in catalog"""
        self.wait_for_selector(self.PRODUCT_CARD)

        product_link = self.page.locator(self.PRODUCT_LINK).first
        if product_link.is_visible():
            href = product_link.get_attribute('href')
            return href or ""

        return ""

    def get_product_href_by_name(self, product_name: str) -> str:
        """
        Get product href by name

        Args:
            product_name: Product name to find

        Returns:
            Product href or empty string
        """
        with allure.step(f"Get href for product: '{product_name}'"):
            self.wait_for_selector(self.PRODUCT_CARD, timeout=10000)

            product_cards = self.page.locator(self.PRODUCT_CARD).all()

            for card in product_cards:
                name_link = card.locator(self.PRODUCT_LINK).first
                if not name_link.is_visible():
                    continue

                name_text = name_link.text_content()
                if not name_text:
                    continue

                if product_name.lower() in name_text.lower():
                    href = name_link.get_attribute('href')
                    return href or ""

            return ""

    def click_first_product_favorite(self):
        """Click favorite icon on first product"""
        with allure.step("Add first product to favorites"):
            # Wait for products to load
            self.page.wait_for_selector(self.PRODUCT_CARD, state="visible", timeout=10000)
            self.take_screenshot("Before adding to favorites", force=True)

            # Get first product card
            first_card = self.page.locator(self.PRODUCT_CARD).first
            first_card.scroll_into_view_if_needed()
            self.page.wait_for_timeout(1000)

            # Find favorite icon - using explicit selector for reliability
            favorite_icon = first_card.locator(".product-card__favorites .favorite-icon").first

            # Check if element exists
            if favorite_icon.count() == 0:
                allure_attach.attach_text(
                    "Favorite icon not found in DOM. Card HTML:",
                    name="Debug info"
                )
                allure_attach.attach_text(
                    first_card.inner_html(),
                    name="Product card HTML",
                    attachment_type=allure.attachment_type.HTML
                )
                raise AssertionError("Favorite icon element does not exist on first product")

            # Check if element is visible and click
            if favorite_icon.is_visible():
                favorite_icon.click()
                self.page.wait_for_timeout(1000)
                self.take_screenshot("After adding to favorites", force=True)
            else:
                raise AssertionError("Favorite icon is present but not visible on first product")

    def click_first_product_add_to_cart(self):
        """Click add to cart button on first product"""
        with allure.step("Add first product to cart"):
            self.wait_for_selector(self.PRODUCT_CARD)
            first_card = self.page.locator(self.PRODUCT_CARD).first
            buy_button = first_card.locator(self.PRODUCT_ADD_TO_CART_BTN).first

            if buy_button.is_visible():
                product_name = self.get_first_product_name()
                allure_attach.attach_text(f"Adding product: {product_name}", name="Info")

                buy_button.scroll_into_view_if_needed()
                self.page.wait_for_timeout(500)
                buy_button.click()
                self.page.wait_for_timeout(2000)
            else:
                raise AssertionError("Add to cart button not found on first product")

    def click_first_product(self):
        """Click first product to navigate to its page"""
        with allure.step("Navigate to first product page"):
            self.wait_for_selector(self.PRODUCT_CARD)

            product_name = self.get_first_product_name()
            allure_attach.attach_text(f"Navigating to product: {product_name}", name="Info")

            first_card = self.page.locator(self.PRODUCT_CARD).first
            buy_link = first_card.locator("a.btn-primary:has-text('Купить')").first

            if buy_link.is_visible():
                href = buy_link.get_attribute('href')
                allure_attach.attach_text(f"Product URL: {href}", name="Info")

                with self.page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
                    buy_link.click()

                self.page.wait_for_timeout(2000)
            else:
                product_link = first_card.locator(self.PRODUCT_LINK).first
                if product_link.is_visible():
                    with self.page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
                        product_link.click()
                    self.page.wait_for_timeout(2000)
                else:
                    raise AssertionError("No navigation method found for product")

    def click_product_by_name(self, product_name: str):
        """
        Click on product by name and navigate to its page

        Args:
            product_name: Product name to click
        """
        with allure.step(f"Click on product '{product_name}'"):
            self.page.wait_for_selector(self.PRODUCT_CARD, timeout=10000)

            product_links = self.page.locator(self.PRODUCT_LINK).all()

            found = False
            for link in product_links:
                if link.is_visible():
                    name = link.text_content()
                    if name and product_name.lower() in name.lower():
                        link.scroll_into_view_if_needed()
                        self.page.wait_for_timeout(500)

                        with self.page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
                            link.click()

                        self.page.wait_for_timeout(2000)
                        found = True
                        break

            if not found:
                raise AssertionError(f"Product with name '{product_name}' not found")

    def get_all_product_names(self) -> List[str]:
        """Get names of all products on current page"""
        names = []
        product_links = self.page.locator(self.PRODUCT_LINK).all()

        for link in product_links:
            if link.is_visible():
                name = link.text_content()
                if name:
                    names.append(name.strip())

        return names