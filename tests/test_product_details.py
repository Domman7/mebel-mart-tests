"""
Product details tests
"""

import allure
from config.settings import Config


@allure.feature("Product Details")
@allure.story("Product Characteristics Verification")
def test_product_details(catalog_page, product_page):
    """Test verifies product details and characteristics"""

    TARGET_PRODUCT = Config.TEST_DATA["target_product"]

    catalog_page.open_catalog()
    catalog_page.take_screenshot("Catalog opened")

    with allure.step(f"Find and click on product '{TARGET_PRODUCT}'"):
        assert catalog_page.find_product_by_name(TARGET_PRODUCT), \
            f"Product '{TARGET_PRODUCT}' not found in catalog"
        catalog_page.take_screenshot(f"Product '{TARGET_PRODUCT}' found in catalog")
        actual_href = catalog_page.get_product_href_by_name(TARGET_PRODUCT)
        catalog_page.click_product_by_name(TARGET_PRODUCT)
        catalog_page.take_screenshot("After navigating to product page")

    with allure.step("Verify correct product page opened"):
        product_title = product_page.get_product_title()
        product_page.take_screenshot("Product title")
        assert actual_href in product_page.page.url, \
            f"Opened '{product_title}' instead of '{actual_href}'"

    with allure.step("Navigate to specifications tab"):
        product_page.click_specifications_tab()
        product_page.take_screenshot("Specifications tab")

    with allure.step("Get all product specifications"):
        specs = product_page.get_specifications_from_table()
        product_page.take_screenshot("Product specifications")

        if specs:
            specs_text = "\n".join([f"  • {k}: {v}" for k, v in specs.items()])
            allure.attach(f"Found specifications:\n{specs_text}", name="Product specifications")
        else:
            allure.attach("No specifications found", name="Warning")

    with allure.step("Verify width specification exists and is correct"):
        width_value = product_page.get_specification_value("Width")

        if width_value:
            product_page.take_screenshot(f"Found width: {width_value}")
            allure.attach(f"Found width: {width_value}", name="Info")

            expected_width = Config.TEST_DATA.get("product_width", "2200")
            assert expected_width in width_value, \
                f"Expected width {expected_width} mm, got '{width_value}'"

            numeric_width = product_page.extract_numeric_value(width_value)
            allure.attach(f"Numeric width value: {numeric_width} mm", name="Info")
        else:
            product_page.take_screenshot("Width specification not found")
            allure.attach("Width specification not found, checking alternatives", name="Warning")

            alt_names = ["Dimensions", "Size", "Length"]
            found = False

            for alt_name in alt_names:
                alt_value = product_page.get_specification_value(alt_name)
                if alt_value:
                    product_page.take_screenshot(f"Found alternative: {alt_name} = {alt_value}")
                    allure.attach(f"Found alternative '{alt_name}': {alt_value}", name="Info")
                    found = True
                    break

            if not found:
                product_page.take_screenshot("No dimension information found")
                allure.attach("Could not find product dimension information", name="Warning")

    with allure.step("Check additional specifications"):
        mechanism = product_page.get_specification_value("Mechanism")
        if mechanism:
            product_page.take_screenshot(f"Mechanism: {mechanism}")
            allure.attach(f"Transformation mechanism: {mechanism}", name="Info")

        material = product_page.get_specification_value("Material")
        if material:
            product_page.take_screenshot(f"Material: {material}")
            allure.attach(f"Material: {material}", name="Info")

        color = product_page.get_specification_value("Color")
        if color:
            product_page.take_screenshot(f"Color: {color}")
            allure.attach(f"Color: {color}", name="Info")

    product_page.take_screenshot("Final product page state")