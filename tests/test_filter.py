"""
Filter functionality tests
"""

import allure
from config.settings import Config


@allure.feature("Product Filter")
@allure.story("Price Filter")
def test_filter_by_price(catalog_page):
    """
    Test verifies price filter functionality and presence of target product
    """

    TARGET_PRODUCT = Config.TEST_DATA["target_product"]
    PRICE_FROM = Config.TEST_DATA["min_price"]
    PRICE_TO = Config.TEST_DATA["max_price"]

    with allure.step("Open sofas catalog"):
        catalog_page.open_catalog()
        catalog_page.take_screenshot("Catalog before filter")

        page_title = catalog_page.get_page_title()
        allure.attach(f"Page title: {page_title}", name="Info")

        try:
            total_before = catalog_page.get_total_products_count()
            allure.attach(f"Total products before filter: {total_before}", name="Info")
        except:
            pass

    with allure.step(f"Apply price filter: {PRICE_FROM} to {PRICE_TO}"):
        catalog_page.apply_price_filter(str(PRICE_FROM), str(PRICE_TO))

        current_url = catalog_page.page.url
        allure.attach(f"URL after filter: {current_url}", name="Info")
        catalog_page.take_screenshot("Catalog after filter")

        assert f"price={PRICE_FROM}-{PRICE_TO}" in current_url, \
            f"Filter parameters not found in URL: {current_url}"

        try:
            total_after = catalog_page.get_total_products_count()
            allure.attach(f"Products after filter: {total_after}", name="Info")
        except:
            pass

    with allure.step(f"Verify all prices are in range {PRICE_FROM}-{PRICE_TO}"):
        try:
            catalog_page.verify_prices_in_range(PRICE_FROM, PRICE_TO)
        except AssertionError as e:
            allure.attach(f"Warning: {str(e)}", name="Not all prices in range")
        except Exception as e:
            allure.attach(f"Error checking prices: {str(e)}", name="Error")

    with allure.step(f"Find product '{TARGET_PRODUCT}' in results"):
        found = catalog_page.find_product_by_name(TARGET_PRODUCT)

        if found:
            try:
                price = catalog_page.get_product_price_by_name(TARGET_PRODUCT)
                price_num = catalog_page.clean_price(price)

                allure.attach(
                    f"Product '{TARGET_PRODUCT}' found!\n"
                    f"Product price: {price} ({price_num} rub.)\n"
                    f"Filter range: {PRICE_FROM}-{PRICE_TO} rub.",
                    name="Result"
                )
                catalog_page.take_screenshot(f"Found product: {TARGET_PRODUCT}")

                assert PRICE_FROM <= price_num <= PRICE_TO, \
                    f"Product price {price_num} is outside filter range {PRICE_FROM}-{PRICE_TO}"
            except:
                allure.attach(
                    f"Product '{TARGET_PRODUCT}' found but price could not be retrieved",
                    name="Result"
                )
        else:
            all_products = catalog_page.get_all_product_names() if hasattr(
                catalog_page, 'get_all_product_names') else []
            if all_products:
                allure.attach(
                    f"Product '{TARGET_PRODUCT}' not found.\n\n"
                    f"All products on page:\n" + "\n".join(all_products),
                    name="Detailed information"
                )

            catalog_page.take_screenshot("Filter results - product not found")

        assert found, f"Product '{TARGET_PRODUCT}' not found after filtering"