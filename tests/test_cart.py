"""
Cart functionality tests
"""

import allure
from pages.product_page import ProductPage
from config.settings import Config


@allure.feature("Cart")
@allure.story("Add to Cart and Verify Price")
def test_add_to_cart(catalog_page, cart_page, page, header):
    """Test verifies adding product to cart and price consistency"""

    catalog_page.open_catalog()
    catalog_page.take_screenshot("Catalog opened", force=True)

    with allure.step("Remember first product name and price from catalog"):
        expected_name = catalog_page.get_first_product_name()
        expected_price_text = catalog_page.get_first_product_price()
        expected_price_clean = catalog_page.clean_price(expected_price_text)
        allure.attach(
            f"Name: {expected_name}\nPrice: {expected_price_clean}",
            name="Product info in catalog"
        )

    catalog_page.click_first_product()

    product_page = ProductPage(page)

    with allure.step("Verify correct product page opened"):
        product_title = product_page.get_product_title()
        product_price = product_page.get_product_price()
        allure.attach(f"Price on product page: {product_price}", name="Info")

    product_page.click_add_to_cart()
    product_page.take_screenshot("Product added to cart", force=True)

    with allure.step("Navigate to cart via header"):
        header.go_to_cart()
        cart_page.take_screenshot("Cart opened", force=True)

    with allure.step("Verify cart is not empty"):
        assert cart_page.is_cart_not_empty(), "Cart is empty"

    with allure.step("Verify product name in cart"):
        actual_name = cart_page.get_first_item_name()
        assert product_title.lower() in actual_name.lower() or \
               actual_name.lower() in product_title.lower(), \
            f"Cart item '{actual_name}', expected containing '{expected_name}'"

    with allure.step("Verify product price in cart"):
        actual_price_clean = cart_page.get_first_item_price()
        assert product_price == actual_price_clean, \
            f"Cart price {actual_price_clean} does not match catalog price {product_price}"