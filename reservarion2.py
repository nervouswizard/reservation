import undetected_chromedriver as webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
import time
import test

####### variable #######
#燒肉中山 牛肆
adult_num="2" # 可以改人數0~10
kid_num="0" #可以改人數0~8
reservation_date="2023-09-06"
am_or_pm="中午"  #輸入 中午或晚上
name = "楊竣弼"
gender = "0" #女=1 男=0
phone = "0901178620"
#######################



def start_refresh():
    driver.maximize_window()
    # driver = webdriver.Chrome()
    #driver.get("https://inline.app/booking/-LzoSPyWXzTNSaE-I4QJ:inline-live-1/-LzoSQ1_si_q2njdnE5o") #燒肉中山
    driver.get("https://inline.app/booking/-MlIX9yWDwI6MUkexSdA:inline-live-2/-MlIXA7xzJCN7mVDVBjA?language=zh-tw")
    # driver.get("https://inline.app/booking/-MlIX9yWDwI6MUkexSdA:inline-live-2/-MlIXA7xzJCN7mVDVBjA?language=zh-tw")
    time.sleep(0.5)
    while 1:
        try:
            #driver.execute_script("window.scrollBy(0, 2200);")
            #time.sleep(0.8)
            # driver.execute_script("window.scrollBy(0, 10);")
            # confirm_button = WebDriverWait(driver, 0.3).until(
            #     EC.element_to_be_clickable((By.XPATH, "//*[@id='book-now-action-bar']"))
            # )
            # confirm_button.click()
            # time.sleep(1)

            # time.sleep(1)
            adult = WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located((By.XPATH, f"//select[@id='adult-picker']/option[@value={adult_num}]"))
                )
            driver.execute_script("window.scrollBy(0, 1500);")
            click_date = driver.find_element(By.ID, "date-picker")
            click_date.send_keys(Keys.PAGE_DOWN) 
            time.sleep(0.1)

            # time.sleep(5)
            # adult = driver.find_element(By.XPATH, f"//select[@id='adult-picker']/option[@value={adult_num}]")
            # driver.execute_script(
            #     "arguments[0].scrollIntoView({ behavior: 'instant', block: 'center', inline: 'center' });",
            #     adult)

            # adult = WebDriverWait(driver, 3).until(
            #         EC.visibility_of_element_located((By.XPATH, f"//select[@id='adult-picker']/option[@value={adult_num}]"))
            #     )
            adult.click()
            print("adult clicked")

            click_date.click()

            # kid = driver.find_element(By.XPATH, f"//select[@id='kid-picker']/option[@value={kid_num}]")
            # kid.click()

            #driver.execute_script("window.scrollBy(0, 380);") #牛四380 燒肉中山530
            # 取得要捲動到的按鈕元素，這裡使用 XPath 找到按鈕，請替換成你要找的按鈕元素的 XPath
            elements = driver.find_element(By.XPATH, f"//div[@data-date='{reservation_date}']") #選擇要定位日期
            # 捲動至按鈕元素的位置
            driver.execute_script("arguments[0].scrollIntoView(true);", elements)
            time.sleep(0.3)
            skip = driver.find_element(By.XPATH, "// *[ @ id = 'book-now-action-bar'] / div[1] / div[3] / button")

            if elements.get_attribute("disabled") == "true":
                if skip.text == "2023年9月5日":
                    print("同天")
                else:
                    print("日期尚未開放")
                    raise Exception
            else:
                elements.click()

                # wait until 最新可訂餐日期is available
            return

        except Exception as e:
            print("ERROR:", str(e))
            driver.refresh()
            time.sleep(0.5)
def start():

    try:
        global  driver
        start_refresh()

        #time.sleep(0.5)
        # booking_time = driver.find_element(By.XPATH,f"// *[ @ id = 'book-now-content'] / *[ @ aria-labelledby = '晚上'] / button[9]")

        scroll=driver.find_element(By.ID, am_or_pm)
        print(scroll.text)
        # driver.execute_script("arguments[0].scrollIntoView({ behavior: 'instant', block: 'center', inline: 'center' });", scroll)
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'instant', block: 'center', inline: 'center' });", scroll)

        booking_time = driver.find_element(By.XPATH,
                                           f"// *[ @ id = 'book-now-content'] / *[ @ aria-labelledby = '{am_or_pm}'] / button[1]")
        #
        # driver.execute_script("arguments[0].scrollIntoView(true);", booking_time)
        # for i in range(1, 10): #找非候補
        #
        #     booking_time = driver.find_element(By.XPATH, f"// *[ @ id = 'book-now-content'] / *[ @ aria-labelledby = '{am_or_pm}'] / button[{i}]")
        #     value = booking_time.get_attribute("aria-expanded")
        #
        #
        #     if value != "false":
        #         break
        #print(value)
        try:
            booking_time.click()
        except ElementClickInterceptedException:
            scroll = driver.find_element(By.ID, am_or_pm)
            print(scroll.text)
            driver.execute_script(
                "arguments[0].scrollIntoView({ behavior: 'instant', block: 'center', inline: 'center' });", scroll)
            #time.sleep(0.3)
            booking_time.click()
        confirm_button = driver.find_element(By.XPATH, "//*[@id='book-now-action-bar']/div[2]/button")
        confirm_button.click()
        booking_name = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id='name']"))
        )
        booking_name.send_keys(name)
        # booking_gender = driver.find_element(By.XPATH, f"// *[ @ value = {gender}]")
        # booking_gender.click()
        booking_phone = driver.find_element(By.XPATH, "// *[ @ id = 'phone']")
        booking_phone.send_keys(phone)
        ##############################訂金版本
        creditcard_name=driver.find_element(By.XPATH, "// *[ @ id = 'cardholder-name']")
        creditcard_name.send_keys("楊竣弼")
        ActionChains(driver).send_keys('\t').perform()
        ActionChains(driver).send_keys('a0922856575@gmail.com').perform()
        ActionChains(driver).send_keys('\t').perform()
        ActionChains(driver).send_keys('4705380433028723').perform()
        ActionChains(driver).send_keys('1229').perform()
        ActionChains(driver).send_keys('803').perform()


        finish_booking = driver.find_element(By.XPATH, "// *[ @ type = 'submit'] ")
        driver.execute_script("arguments[0].scrollIntoView(true);", finish_booking)
        time.sleep(0.5)

        confirm = driver.find_element(By.XPATH, "//*[@for='deposit-policy']")
        confirm.click()
        finish_booking.click()
    except Exception as e:
        print("ERROR:", str(e))
        while True:
            time.sleep(1)


# driver = webdriver.Chrome()
driver = test.driver
start()
while True:
    time.sleep(1)