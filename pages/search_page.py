"""
Search Page Object
"""

import allure
from pages.base_page import BasePage
from config.settings import Config
from utils import allure_attach


class SearchPage(BasePage):
    """Search results page"""

    # Locators
    SEARCH_RESULTS_GRID = ".product-card"
    FIRST_SEARCH_RESULT_TITLE = f"{SEARCH_RESULTS_GRID}:first-child .product-card__name a"
    SEARCH_RESULTS_COUNT = ".w-100.pl-3.pr-3"

    def open_search_page(self):
        """Open main page for search"""
        with allure.step("Open main page"):
            self.open(Config.BASE_URL)
            self.page.wait_for_load_state("domcontentloaded")

    def search(self, query: str):
        """
        Perform search by query

        Args:
            query: Search query string
        """
        with allure.step(f"Perform search with query: '{query}'"):
            search_url = f"{Config.BASE_URL}/search/{query}"
            allure_attach.attach_text(f"Search URL: {search_url}", name="Info")

            self.page.goto(search_url, wait_until="domcontentloaded")
            self.page.wait_for_timeout(2000)

            try:
                self.wait_for_selector(self.SEARCH_RESULTS_GRID)
                results_count = self.page.locator(self.SEARCH_RESULTS_GRID).count()
                allure_attach.attach_text(f"Found results: {results_count}", name="Info")

                titles = []
                for card in self.page.locator(self.SEARCH_RESULTS_GRID).all()[:5]:
                    title_elem = card.locator(".product-card__name a").first
                    if title_elem.is_visible():
                        titles.append(title_elem.text_content())

                if titles:
                    allure_attach.attach_text("First results:\n" + "\n".join(titles),
                                              name="Search results")

            except Exception as e:
                allure_attach.attach_text(f"No results found: {str(e)}", name="Warning")

    def get_first_result_title(self) -> str:
        """Get first search result title"""
        with allure.step("Get first search result title"):
            try:
                self.page.wait_for_selector(self.SEARCH_RESULTS_GRID, timeout=5000)
                first_result = self.page.locator(self.FIRST_SEARCH_RESULT_TITLE).first

                if first_result.is_visible():
                    title = first_result.text_content()
                    allure_attach.attach_text(f"First result: {title}", name="Info")
                    return title.strip() if title else ""
            except Exception as e:
                allure_attach.attach_text(f"Error: {str(e)}", name="Error")

            return ""