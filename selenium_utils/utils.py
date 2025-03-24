from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time

class WaitAndClickException(Exception):
    pass

class WaitException(Exception):
    pass

class SeleniumUtils:
    def _wait_and_click(self, xpath, timeout=5, webelement=""):
        try:
            button = WebDriverWait(self.driver if webelement == "" else webelement, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            button.click()
            return "clicked"
        except Exception as e:
            raise WaitAndClickException(f"Stopping execution due to failure to click on element: {xpath}") from e

    def _wait(self, xpath, timeout=5, webelement=""):
        try:
            return WebDriverWait(self.driver if webelement == "" else webelement, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except Exception as e:
            raise WaitException(f"Stopping execution due to failure in waiting for element: {xpath}") from e
    
    def _wait_for_all(self, xpath, timeout=5):
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        except Exception as e:
            raise WaitException(f"Stopping execution due to failure in waiting for element: {xpath}") from e
    
    def _paste_text(self, xpath, text, press_enter=False, timeout=0):
        action = ActionChains(self.driver)
        element = self._wait(xpath, timeout)
        action.move_to_element(element)
        action.click()
        action.send_keys(text)

        action.pause(0.5)

        if press_enter:
            action.send_keys(Keys.ENTER)

        action.perform()

    def _is_element_present(self, xpath, timeout=0):
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except:
            return False

    def _wait_for_first_element_or_url(self, elements, timeout=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            for index, element in enumerate(elements):
                try:
                    if element.startswith('http'):
                        if element in self.driver.current_url:
                            return index
                        time.sleep(0.05)
                    else:
                        WebDriverWait(self.driver, timeout=0.05).until(EC.presence_of_element_located((By.XPATH, element)))
                        return index
                except TimeoutException:
                    pass
        return -1
