"""
Header component Page Object for navigation elements
"""

import allure
from pages.base_page import BasePage
from config.settings import Config
from utils import allure_attach


class HeaderComponent(BasePage):
    """Header component with navigation elements"""

    # Locators
    CART_LINK = ".header-laptop__link_cart a[href='/cart']"
    FAVORITE_LINK = ".header-laptop__link_favorite a[href='/favorite']"
    CART_LINK_MOBILE = ".mobile-header__cart a[href='/cart']"
    FAVORITE_LINK_MOBILE = ".mobile-header__favorite a[href='/favorite']"
    FAVORITE_COUNTER = ".favorite-informer b small, .favorite-informer b"

    def go_to_cart(self):
        """Navigate to cart via header"""
        with allure.step("Go to cart via header"):
            if self.is_visible(self.CART_LINK):
                self.click(self.CART_LINK, "Cart icon")
            elif self.is_visible(self.CART_LINK_MOBILE):
                self.click(self.CART_LINK_MOBILE, "Cart icon (mobile)")
            else:
                self.safe_goto(Config.CART_URL)

            self.page.wait_for_load_state("domcontentloaded")
            self.page.wait_for_timeout(1000)

    def go_to_favorite(self):
        """Navigate to favorites via header"""
        with allure.step("Go to favorites via header"):
            favorite_found = False

            desktop_link = self.page.locator(self.FAVORITE_LINK).first
            if desktop_link.is_visible():
                desktop_link.click()
                favorite_found = True
                allure_attach.attach_text("Clicked favorite link (desktop)", name="Success")

            if not favorite_found:
                self.safe_goto(Config.FAVORITE_URL)
                allure_attach.attach_text("Navigated via direct URL", name="Info")

            self.page.wait_for_load_state("domcontentloaded")
            self.page.wait_for_timeout(2000)

            # Verify we are on favorites page
            assert "favorite" in self.page.url, \
                f"Failed to navigate to favorites. Current URL: {self.page.url}"

            self.take_screenshot("Favorites page after navigation", force=True)

    def get_favorite_count(self) -> int:
        """
        Get favorite items count from header counter

        Returns:
            Number of items in favorites
        """
        with allure.step("Get favorite count from header"):
            counter_element = self.page.locator(self.FAVORITE_COUNTER).first
            if counter_element.is_visible():
                count_text = counter_element.text_content()
                if count_text:
                    import re
                    digits = re.sub(r'[^\d]', '', count_text)
                    if digits:
                        count = int(digits)
                        allure_attach.attach_text(f"Favorite count: {count}", name="Info")
                        return count

            allure_attach.attach_text("Favorite counter not found or empty", name="Info")
            return 0