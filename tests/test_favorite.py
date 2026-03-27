"""
Favorites functionality tests
"""

import allure
from pages.header_component import HeaderComponent


@allure.feature("Favorites")
@allure.story("Add to Favorites and Verify")
def test_add_to_favorite(catalog_page, favorite_page, page):
    """Test verifies adding product to favorites"""

    header = HeaderComponent(page)
    catalog_page.open_catalog()
    catalog_page.take_screenshot("Catalog opened", force=True)

    with allure.step("Get first product info and add to favorites"):
        expected_href = catalog_page.get_first_product_href()
        expected_name = catalog_page.get_first_product_name()

        allure.attach(
            f"First product in catalog:\nName: {expected_name}\nhref: {expected_href}",
            name="Product info"
        )

        catalog_page.click_first_product_favorite()

    with allure.step("Navigate to favorites via header"):
        header.go_to_favorite()
        favorite_page.take_screenshot("Favorites page", force=True)

    with allure.step("Verify favorites has items"):
        has_items = favorite_page.is_favorite_has_items()
        assert has_items, "Favorites list is empty"

    with allure.step("Verify added product appears in favorites"):
        actual_href = favorite_page.get_first_product_href()

        assert expected_href, "Could not get product href from catalog"
        assert actual_href, "Could not get product href from favorites"

        expected_href_norm = expected_href.split('/')[-1]
        actual_href_norm = actual_href.split('/')[-1]

        assert (expected_href_norm in actual_href_norm) or (actual_href_norm in expected_href_norm), \
            f"href mismatch: expected '{expected_href}', got '{actual_href}'"

        allure.attach("Product successfully found in favorites", name="Success")