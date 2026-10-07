from playwright.sync_api import Page, expect


class DashboardPage:
    def __init__(self, page: Page):
        self.page = page
        self.ip_lookup_btn = page.locator(".ip-lookup-nav-btn")
        self.logout_btn = page.locator(".logout-btn")
        self.ip_search_input = page.locator("#ip-search-input")
        self.ip_search_btn = page.locator("#ip-search-btn")
        self.dialog_close_btn = page.locator(".modal-close-btn")
        self.details_close_btn = page.locator(".dialog-container .close-btn")
        self.ip_details_dialog = page.locator(".dialog-container")

    def open_ip_lookup(self) -> None:
        self.ip_lookup_btn.click()
        expect(self.ip_search_input).to_be_visible()

    def fill_ip(self, ip_address: str) -> None:
        self.ip_search_input.fill(ip_address)

    def search_ip(self, ip_address: str) -> None:
        self.fill_ip(ip_address)
        self.ip_search_btn.click()

    def close_lookup_dialog(self) -> None:
        self.dialog_close_btn.click()

    def close_details_dialog(self) -> None:
        if self.details_close_btn.is_visible():
            self.details_close_btn.click()
        else:
            self.dialog_close_btn.click()

    def logout(self) -> None:
        self.logout_btn.click()

    def assert_loaded(self) -> None:
        expect(self.ip_lookup_btn).to_be_visible()
        expect(self.logout_btn).to_be_visible()

    def assert_ip_details_visible(self, ip_address: str) -> None:
        expect(self.ip_details_dialog).to_be_visible()
        expect(self.ip_details_dialog).to_contain_text(ip_address)

    def assert_search_disabled(self) -> None:
        expect(self.ip_search_btn).to_be_disabled()

    def assert_invalid_badge_visible(self) -> None:
        expect(self.page.locator(".ip-status.invalid")).to_be_visible()

    def assert_details_not_visible(self) -> None:
        expect(self.ip_details_dialog).not_to_be_visible()
