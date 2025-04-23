from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time

from app.page_objects.base_page_object import BasePageObject
from app.page_objects.dice.job_search.dice_job_search_result_page import DiceJobSearchResultPage


class DiceJobSearchBar(BasePageObject):

    # Try multiple selector options for search fields
    __SEARCH_TERM_OPTIONS = [
        (By.ID, 'typeaheadInput'),
        (By.NAME, 'q'),
        (By.CSS_SELECTOR, 'input[placeholder*="job title"]'),
        (By.CSS_SELECTOR, 'input[placeholder*="skill"]')
    ]
    
    __LOCATION_OPTIONS = [
        (By.ID, 'google-location-search'),
        (By.NAME, 'location'),
        (By.CSS_SELECTOR, 'input[placeholder*="location"]'),
        (By.CSS_SELECTOR, 'input[placeholder="Location"]')
    ]
    
    __SEARCH_BUTTON_OPTIONS = [
        (By.ID, 'submitSearch-button'),
        (By.CSS_SELECTOR, 'button[type="submit"]'),
        (By.XPATH, '//button[contains(text(), "Search")]'),
        (By.XPATH, '//button[contains(text(), "search")]'),
        (By.CSS_SELECTOR, '.btn-primary')
    ]

    def __init__(self, driver):
        super().__init__(driver)

    def _find_element_from_options(self, locator_options, timeout=10):
        """Try to find element using multiple possible locators"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            for locator in locator_options:
                try:
                    element = WebDriverWait(self.driver, 2).until(
                        EC.visibility_of_element_located(locator)
                    )
                    print(f"Found element using locator: {locator}")
                    return element
                except (TimeoutException, StaleElementReferenceException):
                    continue
            time.sleep(0.5)
        
        # If we get here, none of the locators worked
        print(f"Could not find element with any of these locators: {locator_options}")
        raise TimeoutException(f"Element not found with any locators: {locator_options}")

    def set_search_term(self, text):
        print("Trying to find and set search term field...")
        search_term_el = self._find_element_from_options(self.__SEARCH_TERM_OPTIONS)
        search_term_el.clear()
        search_term_el.send_keys(text)
        return self

    def set_location(self, location):
        print("Trying to find and set location field...")
        location_el = self._find_element_from_options(self.__LOCATION_OPTIONS)
        location_el.clear()
        location_el.send_keys(location)
        return self

    def click_search(self) -> DiceJobSearchResultPage:
        print("Trying to find and click search button...")
        search_button_el = self._find_element_from_options(self.__SEARCH_BUTTON_OPTIONS)
        search_button_el.click()
        
        # Wait for search results to load
        WebDriverWait(self.driver, 20).until(
            lambda d: "jobs" in d.current_url
        )
        
        return DiceJobSearchResultPage(self.driver)
