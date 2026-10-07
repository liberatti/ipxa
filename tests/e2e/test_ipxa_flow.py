import pytest

from tests.e2e.pages.dashboard_page import DashboardPage
from tests.e2e.pages.login_page import LoginPage


@pytest.mark.e2e
def test_invalid_ip_ui_validation(authenticated_dashboard: DashboardPage):
    """Smoke test E2E: valida que a interface reage e bloqueia ação com IP inválido."""
    authenticated_dashboard.open_ip_lookup()

    # Preenche IP inválido
    authenticated_dashboard.fill_ip("999.999.999.999")

    # Validações visuais/de estado da UI
    authenticated_dashboard.assert_invalid_badge_visible()
    authenticated_dashboard.assert_search_disabled()
    authenticated_dashboard.assert_details_not_visible()


@pytest.mark.e2e
def test_valid_ip_lookup_and_logout(authenticated_dashboard: DashboardPage, login_page: LoginPage):
    """Fluxo feliz E2E: pesquisa de IP válido e encerramento de sessão."""
    authenticated_dashboard.open_ip_lookup()

    # Busca IP válido e valida detalhes
    authenticated_dashboard.search_ip("8.8.8.8")
    authenticated_dashboard.assert_ip_details_visible("8.8.8.8")
    authenticated_dashboard.close_details_dialog()

    # Logout
    authenticated_dashboard.logout()
    login_page.assert_on_login_page()
