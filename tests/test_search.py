"""
Search functionality tests
"""

import allure
from config.settings import Config


@allure.feature("Search")
@allure.story("Product Search by Name")
def test_search_product(search_page):
    """Test verifies product search by name"""

    search_query = Config.TEST_DATA["search_query"]

    search_page.open_search_page()
    search_page.take_screenshot("Main page opened")

    search_page.search(search_query)
    search_page.take_screenshot(f"Search results: {search_query}")

    with allure.step("Verify first result contains search query"):
        first_result_title = search_page.get_first_result_title()
        search_page.take_screenshot(f"First result: {first_result_title}")
        assert search_query.lower() in first_result_title.lower(), \
            f"First result title '{first_result_title}' does not contain '{search_query}'"