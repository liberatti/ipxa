import os

import pytest
from playwright.sync_api import Page

from tests.e2e.pages.dashboard_page import DashboardPage
from tests.e2e.pages.login_page import LoginPage


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("APP_BASE_URL", "http://localhost:5000")


@pytest.fixture
def login_page(page: Page, base_url: str) -> LoginPage:
    lp = LoginPage(page)
    lp.navigate(base_url)
    return lp


@pytest.fixture
def dashboard_page(page: Page) -> DashboardPage:
    return DashboardPage(page)


@pytest.fixture
def authenticated_dashboard(login_page: LoginPage, dashboard_page: DashboardPage) -> DashboardPage:
    email = os.getenv("APP_ADMIN_EMAIL", "admin@local")
    password = os.getenv("APP_ADMIN_PASSWORD", "admin")
    login_page.login(email, password)
    dashboard_page.assert_loaded()
    return dashboard_page
