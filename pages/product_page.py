"""
Product details Page Object
"""

import allure
import re
from pages.base_page import BasePage
from utils import allure_attach


class ProductPage(BasePage):
    """Product details page"""

    # Locators
    TITLE = "h1"
    PRICE = ".productPrice"
    FAVORITE_ICON = ".favorite-icon"
    ADD_TO_CART_BTN = ".btnToCart"

    # Notification locators
    NOTIFICATION = ".notification, .alert, .toast"
    NOTIFICATION_GO_TO_CART = "a:has-text('Перейти в корзину'), button:has-text('Перейти в корзину')"

    # Specifications tab locators
    SPEC_TAB = "a[href='#singleProdParam'], a:has-text('Specifications')"
    SPEC_TABLE = "div.tab-pane#singleProdParam table.table"

    def get_product_title(self) -> str:
        """Get product title"""
        title = self.get_text(self.TITLE)
        allure_attach.attach_text(f"Product title: {title}", name="Info")
        return title

    def get_product_price(self) -> str:
        """Get product price"""
        price = self.get_text(self.PRICE)
        allure_attach.attach_text(f"Product price: {price}", name="Info")
        return price.replace(' ', '')

    def click_add_to_cart(self):
        """Click add to cart button"""
        with allure.step("Click 'Add to cart' button"):
            self.page.wait_for_selector(self.ADD_TO_CART_BTN, timeout=5000)

            add_btn = self.page.locator("a.btnToCart.btn-primary:has-text('Add to cart')").first

            if not add_btn.is_visible():
                add_btn = self.page.locator(self.ADD_TO_CART_BTN).first

            if add_btn.is_visible():
                add_btn.scroll_into_view_if_needed()
                self.page.wait_for_timeout(500)
                add_btn.click()
                self.page.wait_for_timeout(2000)
            else:
                raise AssertionError("Add to cart button not found on page")

    def click_specifications_tab(self):
        """Click on specifications tab"""
        with allure.step("Navigate to 'Specifications' tab"):
            try:
                spec_tab = self.page.locator(self.SPEC_TAB).first

                if spec_tab.is_visible():
                    spec_tab.scroll_into_view_if_needed()
                    self.page.wait_for_timeout(1000)

                    is_active = spec_tab.get_attribute('aria-selected') == 'true' or \
                                'active' in (spec_tab.get_attribute('class') or '')

                    if not is_active:
                        spec_tab.click()
                        self.page.wait_for_timeout(1000)

                    try:
                        self.page.wait_for_selector(self.SPEC_TABLE, timeout=5000)
                    except:
                        allure_attach.attach_text("Specifications table not found after clicking tab", name="Warning")
                else:
                    allure_attach.attach_text("Specifications tab not found", name="Warning")
            except Exception as e:
                allure_attach.attach_text(f"Error accessing specifications: {str(e)}", name="Warning")

    def get_specifications_from_table(self) -> dict:
        """Get all specifications from table"""
        with allure.step("Get specifications from table"):
            specs = {}

            try:
                self.click_specifications_tab()
            except:
                allure_attach.attach_text("Could not activate specifications tab", name="Warning")

            table = self.page.locator(self.SPEC_TABLE).first

            if table.is_visible():
                rows = table.locator("tbody tr").all()

                for row in rows:
                    cells = row.locator("td").all()
                    if len(cells) >= 2:
                        spec_name = cells[0].text_content()
                        spec_value = cells[1].text_content()
                        if spec_name and spec_value:
                            spec_name = spec_name.strip().rstrip(':').strip()
                            spec_value = spec_value.strip()
                            specs[spec_name] = spec_value

                allure_attach.attach_text(f"Found specifications: {len(specs)}", name="Info")
            else:
                allure_attach.attach_text("Specifications table not found", name="Error")

            return specs

    def get_specification_value(self, spec_name: str) -> str:
        """
        Get specific specification value

        Args:
            spec_name: Specification name to find

        Returns:
            Specification value or empty string
        """
        specs = self.get_specifications_from_table()

        if spec_name in specs:
            return specs[spec_name]

        for key, value in specs.items():
            if spec_name.lower() in key.lower():
                return value

        return ""

    def extract_numeric_value(self, text: str) -> int:
        """
        Extract numeric value from text

        Args:
            text: Text containing numbers

        Returns:
            Extracted integer value
        """
        match = re.search(r'(\d+)', text)
        if match:
            return int(match.group(1))
        return 0