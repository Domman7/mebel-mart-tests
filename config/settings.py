"""
Configuration settings for the test framework
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration settings"""

    # Base URLs
    BASE_URL = "https://mebelmart-saratov.ru"
    CATALOG_URL = f"{BASE_URL}/myagkaya_mebel_v_saratove/divanyi_v_saratove"
    SEARCH_URL = f"{BASE_URL}/search/"
    FAVORITE_URL = f"{BASE_URL}/favorite"
    CART_URL = f"{BASE_URL}/cart"

    # Timeouts (in milliseconds)
    DEFAULT_TIMEOUT = 10000
    NAVIGATION_TIMEOUT = 20000
    SCREENSHOT_TIMEOUT = 15000

    # Browser settings
    BROWSERS = ["chromium", "firefox"]
    HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"
    SLOW_MO = int(os.getenv("SLOW_MO", "300"))

    # Test data
    TEST_DATA = {
        "min_price": 10000,
        "max_price": 15000,
        "target_product": "Диван ЧБ",
        "search_query": "Бостон",
        "product_width": "2200"
    }