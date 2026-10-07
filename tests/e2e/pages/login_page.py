from playwright.sync_api import Page, expect


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.email_input = page.locator("#login-email")
        self.password_input = page.locator("#login-password")
        self.submit_btn = page.locator(".btn-login")
        self.error_box = page.locator(".error-box")

    def navigate(self, base_url: str) -> None:
        self.page.goto(f"{base_url.rstrip('/')}/ipxa/login")

    def login(self, email: str, password: str) -> None:
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_btn.click()

    def assert_error_message(self, text: str) -> None:
        expect(self.error_box).to_contain_text(text)

    def assert_on_login_page(self) -> None:
        expect(self.submit_btn).to_be_visible()
