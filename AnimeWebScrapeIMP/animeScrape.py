from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
import datetime

class AnimeScrape:
    def __init__(self, driver):
        self.driver = driver

    def animeSchedule(self):
        self.driver.get('https://9animetv.to/home')
        try:
            seeMoreDetails = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="scl-more"]'))
            )
            self.driver.execute_script("arguments[0].click();", seeMoreDetails)
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'swiper-wrapper'))
            )
            scheduleItems = self.driver.find_elements(By.CLASS_NAME, 'swiper-slide')

            for item in scheduleItems:
                scheduleDate = item.get_attribute('data-date')
                if scheduleDate == datetime.date.today().strftime('%Y-%m-%d'):
                    print(f"Schedule for {scheduleDate}:")

                    try:
                        scheduledTime = item.find_element(By.XPATH, '//*[@id="schedule-block"]/section/div[2]/div/ul')
                        for scheduleEntry in scheduledTime.find_elements(By.XPATH, './/a[@class="tsl-link"]'):
                            try:
                                timeElement = scheduleEntry.find_element(By.XPATH, './/div[@class="time"]').text
                                filmDetail = scheduleEntry.find_element(By.XPATH, './/h3[@class="film-name dynamic-name"]').text
                                episode = scheduleEntry.find_element(By.XPATH, './/button[@class="btn btn-sm btn-play"]').text
                                print(f"Time: {timeElement} | Anime Name: {filmDetail} | Episode: {episode}")
                                
                                # Save the data to a CSV file
                                df = pd.DataFrame({'Time': [timeElement], 'Anime Name': [filmDetail], 'Episode': [episode]})
                                df.to_csv('Schedule.csv', mode='a', header=True, index=False)
                            except NoSuchElementException:
                                print("Time or film detail or episode not found for this entry.")
                                continue
                    except NoSuchElementException:
                        print("No schedule list found for this day.")
        except TimeoutException:
            print("Schedule not found on the page.")
        
        self.driver.close()
        self.driver.quit()
