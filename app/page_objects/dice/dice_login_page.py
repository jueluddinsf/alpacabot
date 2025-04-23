from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from app.page_objects.dice.base_dice_page import BaseDicePage
from app.page_objects.dice.dice_home_feed_page import DiceHomeFeedPage


class DiceLoginPage(BaseDicePage):

    # New selectors for the updated login page
    __EMAIL_INPUT = (By.NAME, "email")
    __CONTINUE_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    __PASSWORD_INPUT = (By.NAME, "password")
    __SIGN_IN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")

    def __init__(self, driver):
        super().__init__(driver)

    def enter_email(self, email):
        # Wait for email field to be visible
        try:
            email_el = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.__EMAIL_INPUT)
            )
            email_el.clear()
            email_el.send_keys(email)
            return self
        except TimeoutException:
            print("Email input field not found after 10 seconds")
            raise

    def click_continue_button(self):
        try:
            continue_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.__CONTINUE_BUTTON)
            )
            continue_button.click()
            return self
        except TimeoutException:
            print("Continue button not found after 10 seconds")
            raise

    def enter_password(self, password):
        try:
            password_el = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.__PASSWORD_INPUT)
            )
            password_el.clear()
            password_el.send_keys(password)
            return self
        except TimeoutException:
            print("Password input field not found after 10 seconds")
            raise

    def click_sign_in_button(self):
        try:
            sign_in_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.__SIGN_IN_BUTTON)
            )
            sign_in_button.click()
            return self
        except TimeoutException:
            print("Sign in button not found after 10 seconds")
            raise

    def login(self, email, password) -> DiceHomeFeedPage:
        self.enter_email(email)\
            .click_continue_button()\
            .enter_password(password)\
            .click_sign_in_button()
        
        # Wait for homepage to load
        WebDriverWait(self.driver, 20).until(
            lambda d: "dashboard" in d.current_url
        )
        
        return DiceHomeFeedPage(self.driver)
