from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.options import Options
from typing import Optional
import time
import os


class WaitAndClickException(Exception):
    pass

class WaitException(Exception):
    pass

class SeleniumUtils:
    """Handles Selenium-specific configurations."""
    
    def configure_browser_options(
        self,
        options: Options,
        browser_executable_path: Optional[str],
        profile_name: Optional[str],
        headless: bool
    ) -> None:
        """Configure all browser options."""
        if browser_executable_path:
            options.binary_location = browser_executable_path

        self._configure_basic_options(options)
        self._configure_profile(options, profile_name)
        self._configure_headless(options, headless)

    def _configure_basic_options(self, options: Options) -> None:
        """Configure basic Chrome options."""
        options.add_argument("--lang=en_US")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument('--disable-infobars')
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-notifications")
        options.add_argument('log-level=3')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-webrtc')

        # WebRTC leak prevention
        options.add_experimental_option("prefs", {
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",
            "webrtc.multiple_routes_enabled": False,
            "webrtc.nonproxied_udp_enabled": False
        })

    def _configure_profile(self, options: Options, profile_name: Optional[str]) -> None:
        """Configure user profile if specified."""
        if not profile_name:
            return

        profiles_dir = os.path.join(os.getcwd(), "profiles")
        if not os.path.exists(profiles_dir):
            os.makedirs(profiles_dir)

        data_dir = os.path.join(profiles_dir, profile_name)
        options.add_argument(f"--user-data-dir={data_dir}")

    def _configure_headless(self, options: Options, headless: bool) -> None:
        """Configure headless mode if specified."""
        if headless:
            options.add_argument('--headless=new')

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
