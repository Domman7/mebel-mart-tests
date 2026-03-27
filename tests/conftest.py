"""
Pytest fixtures and hooks for the test framework
"""

import allure
import pytest
import os
import multiprocessing
from playwright.sync_api import sync_playwright
from config.settings import Config
from utils import allure_attach


# Parse command line
def pytest_addoption(parser):
    parser.addoption(
        "--test-browser",
        action="store",
        default="chromium",
        choices=Config.BROWSERS,
        help="Choose browser: chromium or firefox"
    )
    parser.addoption(
        "--num-threads",
        action="store",
        default="4",  # Changed from "auto" to "4" for better stability
        help="Number of threads for parallel execution (1, 2, 4, etc.)"
    )


# Configure markers
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "filter_test: Filter functionality tests")
    config.addinivalue_line("markers", "cart_test: Cart functionality tests")
    config.addinivalue_line("markers", "favorite_test: Favorites functionality tests")
    config.addinivalue_line("markers", "search_test: Search functionality tests")
    config.addinivalue_line("markers", "product_test: Product details tests")

    # Parallel execution setup
    if not hasattr(config, 'workerinput'):
        num_threads = config.getoption("--num-threads")
        os.environ['PYTEST_XDIST_NUM_THREADS'] = num_threads

        if num_threads == "auto":
            threads = multiprocessing.cpu_count()
            print(f"\nRunning tests in {threads} threads (auto-detected)")
        else:
            print(f"\nRunning tests in {num_threads} threads")


@pytest.fixture(scope="function")
def browser(request):
    """Browser fixture with parallel execution support"""
    browser_name = request.config.getoption("--test-browser")
    worker_id = getattr(request.config, 'workerinput', {}).get('workerid', 'master')

    with sync_playwright() as p:
        launch_options = {
            "headless": Config.HEADLESS,
            "slow_mo": Config.SLOW_MO,
        }

        if browser_name == "chromium":
            browser = p.chromium.launch(**launch_options)
        elif browser_name == "firefox":
            browser = p.firefox.launch(**launch_options)
        else:
            browser = p.chromium.launch(**launch_options)

        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser, request):
    """Page fixture with isolated context for each test"""
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (test-{request.node.name})"
    )

    context.set_default_timeout(10000)
    page = context.new_page()

    yield page

    context.close()


# Page object fixtures
@pytest.fixture(scope="function")
def catalog_page(page):
    from pages.catalog_page import CatalogPage
    return CatalogPage(page)


@pytest.fixture(scope="function")
def product_page(page):
    from pages.product_page import ProductPage
    return ProductPage(page)


@pytest.fixture(scope="function")
def favorite_page(page):
    from pages.favorite_page import FavoritePage
    return FavoritePage(page)


@pytest.fixture(scope="function")
def search_page(page):
    from pages.search_page import SearchPage
    return SearchPage(page)


@pytest.fixture(scope="function")
def cart_page(page):
    from pages.cart_page import CartPage
    return CartPage(page)


@pytest.fixture(scope="function")
def header(page):
    from pages.header_component import HeaderComponent
    return HeaderComponent(page)


# Hook for screenshot on test failure
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call":
        setattr(item, "rep_call", rep)

    if rep.when == "call" and rep.failed:
        if "page" in item.funcargs:
            page = item.funcargs["page"]
            worker_id = getattr(item.config, 'workerinput', {}).get('workerid', 'master')

            allure_attach.attach_screenshot(
                page,
                name=f"Screenshot on failure (worker: {worker_id})"
            )
            allure_attach.attach_page_source(
                page,
                name=f"HTML source on failure (worker: {worker_id})"
            )
            allure_attach.attach_url(
                page,
                name=f"URL on failure (worker: {worker_id})"
            )


# Hook for logging test start in parallel mode
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    worker_id = getattr(item.config, 'workerinput', {}).get('workerid', 'master')
    print(f"\n[Worker {worker_id}] Starting test: {item.name}")


# Group tests by categories for parallel execution
def pytest_collection_modifyitems(items):
    """Group tests by feature for more efficient parallel execution"""
    for item in items:
        if "test_filter" in item.nodeid:
            item.add_marker(pytest.mark.filter_test)
        elif "test_cart" in item.nodeid:
            item.add_marker(pytest.mark.cart_test)
        elif "test_favorite" in item.nodeid or "test_favorites" in item.nodeid:
            item.add_marker(pytest.mark.favorite_test)
        elif "test_search" in item.nodeid:
            item.add_marker(pytest.mark.search_test)
        elif "test_product_details" in item.nodeid:
            item.add_marker(pytest.mark.product_test)