import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.config.settings import ERP_LOGIN_URL

load_dotenv()


class ERPTaskExtractor:
    def __init__(self, user_email: str, user_password: str):
        self.driver = None
        self.wait = None
        self.EMAIL = user_email
        self.PASSWORD = user_password
        self.LOGIN_URL = ERP_LOGIN_URL

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.maximize_window()
        print("Chrome driver setup complete")

    def login(self):
        print("Starting login process...")

        # Navigate to login
        self.driver.get(self.LOGIN_URL)
        self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "form-login")))

        # Enter credentials
        email_field = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div/div/main/div[2]/div/section[1]/div/form/div[1]/div[1]/div/input")))
        email_field.clear()
        email_field.send_keys(self.EMAIL)

        password_field = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div/div/main/div[2]/div/section[1]/div/form/div[1]/div[2]/div/input")))
        password_field.clear()
        password_field.send_keys(self.PASSWORD)

        # Click login
        login_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-login")))
        login_button.click()

        # Wait for redirect
        time.sleep(1)
        current_url = self.driver.current_url
        if "/login" not in current_url:
            print(f"Login successful: {current_url}")
            return True
        return False

    def navigate_to_tasks(self):
        task_url = "https://erp.softsuave.in/app/task/view/list"
        self.driver.get(task_url)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)
        print(f"Navigated to tasks page")

    def extract_content(self, task_id):
        selectors = ["div.ql-editor", "div.ql-container", "[contenteditable='true']"]

        for selector in selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                for element in elements:
                    # Try list items first
                    list_items = element.find_elements(By.XPATH, ".//ol/li | .//ul/li")
                    if list_items:
                        content = [item.get_attribute('textContent').strip() for item in list_items if
                                   item.get_attribute('textContent').strip()]
                        if content:
                            return content

                    # Try paragraphs
                    paragraphs = element.find_elements(By.XPATH, ".//p")
                    if paragraphs:
                        content = [p.get_attribute('textContent').strip() for p in paragraphs if
                                   p.get_attribute('textContent').strip()]
                        if content:
                            return content

                    # Try direct text
                    if "ql-blank" in element.get_attribute("class"):
                        return ["[No content]"]

                    text = element.get_attribute('textContent').strip()
                    if text and len(text) > 10:
                        lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 2]
                        if lines:
                            return lines

        return ["[No content found]"]

    def extract_all_tasks_parallel(self):
        print("Starting parallel extraction...")

        # Get task URLs
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "list-row-container")))
        time.sleep(1)

        task_rows = self.driver.find_elements(By.CLASS_NAME, "list-row-container")
        task_urls = []

        for index, row in enumerate(task_rows):
            try:
                clickable_elements = row.find_elements(By.XPATH, ".//a[contains(@href, '/app/task/')]")
                if clickable_elements:
                    task_url = clickable_elements[0].get_attribute('href')
                    task_id = task_url.split('/')[-1]
                    task_urls.append((task_id, task_url))
                else:
                    task_id_element = row.find_element(By.XPATH, ".//td[contains(text(), 'TASK-')]")
                    task_id = task_id_element.text.strip()
                    task_url = f"https://erp.softsuave.in/app/task/{task_id}"
                    task_urls.append((task_id, task_url))
            except:
                continue

        print(f"Found {len(task_urls)} tasks")

        # Store original window
        original_window = self.driver.current_window_handle
        tab_handles = []

        # Open all tabs
        print("Opening tabs...")
        for task_id, task_url in task_urls:
            self.driver.execute_script("window.open('');")
            new_tab = [h for h in self.driver.window_handles if h not in [original_window] + tab_handles][-1]
            tab_handles.append(new_tab)
            self.driver.switch_to.window(new_tab)
            self.driver.get(task_url)
            time.sleep(0.5)

        print(f"Opened {len(tab_handles)} tabs")

        # Wait for loading
        time.sleep(1)

        # Extract from each tab
        extracted_data = {}
        for i, (tab_handle, (task_id, task_url)) in enumerate(zip(tab_handles, task_urls)):
            try:
                self.driver.switch_to.window(tab_handle)
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                content = self.extract_content(task_id)
                extracted_data[f"{i + 1}_task"] = content
            except:
                extracted_data[f"{i + 1}_task"] = ["[Error]"]

        # Clean up tabs
        for tab_handle in tab_handles:
            try:
                self.driver.switch_to.window(tab_handle)
                self.driver.close()
            except:
                pass

        self.driver.switch_to.window(original_window)
        return extracted_data

    def run(self):
        try:
            self.setup_driver()

            if not self.login():
                print("Login failed")
                return None

            self.navigate_to_tasks()
            extracted_data = self.extract_all_tasks_parallel()

            tasks = ""
            tasks_arr = []

            for key, content in extracted_data.items():
                # print(f"\n{key.upper()}:")
                for i, item in enumerate(content, 1):
                    # print(f"  {i}. {item}")
                    if item == "[No content]":
                        continue
                    tasks_arr.append(item)
                    tasks += f"\n{item}"
            return tasks

        except Exception as e:
            print(f"Error: {e}")
            return None

        finally:
            if self.driver:
                self.driver.quit()

