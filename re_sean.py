from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from config import Config_reader
from datetime import datetime
import time

import json, sys, zipfile
import undetected_chromedriver as uc                    # pyright: ignore
from undetected_chromedriver.patcher import Patcher     # pyright: ignore
from typing import Any
from urllib.request import urlopen, urlretrieve
from pathlib import Path
class UrlNotFound(Exception):
    pass

class driver_for_chromev116():
    def __init__(self):
        self.suppress_exception_in_del(uc)
        self.driver = uc.Chrome(driver_executable_path=self.get_chromedriver_fp())

    def suppress_exception_in_del(self, uc: Any):
        """It suppresses an exception in uc's __del__ method, which is raised when
        selenium shuts down."""
        old_del = uc.Chrome.__del__

        def new_del(self: Any) -> None:
            try:
                old_del(self)
            except:
                pass
        
        setattr(uc.Chrome, '__del__', new_del)

    def get_platform(self):
        platform = sys.platform
        if platform.endswith("win32"):
            # TODO: additional check needed to choose correct version
            return 'win64'          # or 'win32'
        if platform.endswith(("linux", "linux2")):
            return 'linux64'
        if platform.endswith("darwin"):
            # TODO: additional check needed to choose correct version
            return 'mac-x64'        # or 'mac-arm64'
        raise NotImplementedError("Unsupported platform: " + platform)

    def get_chromedriver_fp(self):
        patcher = Patcher()
        driver_fp = Path(patcher.executable_path)
        driver_fp.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        driver_ver_fp = driver_fp.with_suffix('.ver')

        with urlopen("https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json") as f:
            data = json.loads(f.read().decode('utf-8'))
        stable_ch = data['channels']['Stable']
        latest_ver = stable_ch['version']

        cur_ver = None
        if driver_fp.exists() and driver_ver_fp.exists():
            cur_ver = driver_ver_fp.read_text(encoding='utf-8')
            if cur_ver == latest_ver:
                return str(driver_fp)       # doesn't need updating

        platforms = stable_ch['downloads']['chromedriver']
        this_platform = self.get_platform()
        url = None
        for p in platforms:
            if p['platform'] == this_platform:
                url = p['url']
        if url is None:
            raise UrlNotFound(f"url not found for platform `{this_platform}`")
        
        with zipfile.ZipFile(urlretrieve(url)[0]) as zf:
            for fp in zf.filelist:
                if Path(fp.filename).name.startswith('chromedriver'):
                    driver_fp.unlink(missing_ok=True)
                    driver_fp.write_bytes(zf.read(fp.filename))
                    driver_fp.chmod(0o755)
                    driver_ver_fp.write_text(latest_ver, encoding='utf-8')
                    driver_ver_fp.chmod(0o755)
                    return str(driver_fp)
        raise FileNotFoundError("chromedriver not found in zip file")

class reservation():
    def __init__(self):
        # 資料設定
        self.config = Config_reader('reservation')
        self.adult_num = self.config.get('adult_num')
        self.kid_num = self.config.get('kid_num')
        self.reservation_date = self.config.get('reservation_date')
        self.default_day = self.config.get('default_day')
        self.am_or_pm = self.config.get('am_or_pm')
        self.name = self.config.get('name')
        self.gender = self.config.get('gender')
        self.phone = self.config.get('phone')
        # Will’s Teppanyaki
        self.url = "https://inline.app/booking/-MlIX9yWDwI6MUkexSdA:inline-live-2/-MlIXA7xzJCN7mVDVBjA?language=zh-tw"
        # 燒肉中山
        # self.url = "https://inline.app/booking/-LzoSPyWXzTNSaE-I4QJ:inline-live-1/-LzoSQ1_si_q2njdnE5o"
        

        # chrome driver
        self.driver = driver_for_chromev116().driver
        # self.driver.implicitly_wait(1)
        self.timeout = WebDriverWait(self.driver, 10)
        self.driver.maximize_window()
        self.driver.get(self.url)

    def start_refresh(self):
        while True:
            try:
                self.driver.refresh()
                # 用餐人數-大人
                adult_picker = self.timeout.until(
                    EC.visibility_of_element_located(
                        (By.XPATH, f"//select[@id='adult-picker']/option[@value={self.adult_num}]"))
                )
                # adult_picker = self.driver.find_element(
                #     By.XPATH, f"//select[@id='adult-picker']/option[@value={self.adult_num}]")
                # 用餐日期
                date_picker = self.driver.find_element(By.ID, "date-picker")
                # 滾動頁面
                for i in range(2):
                    # ActionChains(self.driver).send_keys(Keys.PAGE_DOWN).perform()
                    date_picker.send_keys(Keys.PAGE_DOWN)
                # 偵測滾動停止
                last_scroll_position = self.driver.execute_script("return document.documentElement.scrollTop || document.body.scrollTop")
                time.sleep(0.02)
                while last_scroll_position != self.driver.execute_script("return document.documentElement.scrollTop || document.body.scrollTop"):
                    last_scroll_position = self.driver.execute_script("return document.documentElement.scrollTop || document.body.scrollTop")
                    time.sleep(0.02)
                # 按page down
                time.sleep(0.02)
                date_picker.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.02)
                # 點擊date picker、adult picker
                adult_picker.click()
                date_picker.click()
                time.sleep(0.01)
                # 選擇要定位日期
                data_date = self.driver.find_element(By.XPATH, f"//div[@data-date='{self.reservation_date}']") 
                # 若選擇時段的bar沒有出現
                book_now_content = self.driver.find_element(By.XPATH, f"// *[ @ id = 'book-now-content'] / div[1] ")
                if book_now_content.text != self.am_or_pm:
                    raise Exception
                
                skip = self.driver.find_element(By.XPATH, "// *[ @ id = 'book-now-action-bar'] / div[1] / div[3] / button")
                if data_date.get_attribute("disabled") == "true":
                    if skip.text == self.default_day:
                        print("同天")
                    else:
                        print("日期尚未開放")
                        raise Exception
                else:
                    data_date.click()
                
                return

            except Exception as e: 
                print("ERROR:", str(e))

    def start(self):
        try:
            taiwan_time = datetime(2023, 8, 26, 0, 0, 0, 0)
            while datetime.now() < taiwan_time:
                print(datetime.now())
            self.start_refresh()

            print('sucess1')
            booking_time = self.driver.find_element(
                By.XPATH, f"// *[ @ id = 'book-now-content'] / *[ @ aria-labelledby = '{self.am_or_pm}'] / button[1]")
            try:
                booking_time.click()
            except ElementClickInterceptedException:
                print('can not click booking_time')
                scroll = self.driver.find_element(By.ID, self.am_or_pm)
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({ behavior: 'instant', block: 'center', inline: 'center' });", scroll)
                booking_time.click()
            self.driver.find_element(By.XPATH, "//*[@id='book-now-action-bar']/div[2]/button").click()

            # 頁面跳轉後
            booking_name = WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located((By.XPATH, "//*[@id='name']"))
            )
            booking_name.send_keys(self.name)
            booking_phone = self.driver.find_element(By.XPATH, "// *[ @ id = 'phone']")
            booking_phone.send_keys(self.phone)

            ##############################訂金版本
            creditcard_name=self.driver.find_element(By.XPATH, "// *[ @ id = 'cardholder-name']")
            creditcard_name.send_keys("楊竣弼")
            ActionChains(self.driver).send_keys('\t').perform()
            ActionChains(self.driver).send_keys('a0922856575@gmail.com').perform()
            card_number = self.driver.find_element(By.XPATH, "// *[ @ id = 'card-number']")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", card_number)
            time.sleep(0.01)
            card_number.click()
            ActionChains(self.driver).send_keys("4705380433028723").perform()
            ActionChains(self.driver).send_keys('1229').perform()
            ActionChains(self.driver).send_keys('803').perform()

            finish_booking = self.driver.find_element(By.XPATH, "// *[ @ type = 'submit'] ")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", finish_booking)
            time.sleep(0.01)
            confirm = self.driver.find_element(By.XPATH, "//*[@for='deposit-policy']")
            confirm.click()
            print('sucess2')
            finish_booking.click()
            while True:
                time.sleep(1)
        except Exception as e:
            print("ERROR:", str(e))
            while True:
                time.sleep(1)

if __name__ == '__main__':
    reservation().start()