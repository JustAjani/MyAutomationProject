from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
import datetime

class AnimeScrape:
    def __init__(self, driver):
        self.driver = driver
        self.BaseUrl = 'https://9animetv.to/'
        self.driver.get(self.BaseUrl)

    def animeSchedule(self):
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
                    try:
                        scheduledTime = item.find_element(By.XPATH, '//*[@id="schedule-block"]/section/div[2]/div/ul')
                        for scheduleEntry in scheduledTime.find_elements(By.XPATH, './/a[@class="tsl-link"]'):
                            try:
                                timeElement = scheduleEntry.find_element(By.XPATH, './/div[@class="time"]').text
                                filmDetail = scheduleEntry.find_element(By.XPATH, './/h3[@class="film-name dynamic-name"]').text
                                episode = scheduleEntry.find_element(By.XPATH, './/button[@class="btn btn-sm btn-play"]').text
                                df = pd.DataFrame({'Time': [timeElement], 'Anime Name': [filmDetail], 'Episode': [episode]}, columns=['Time', 'Anime Name', 'Episode'])
                                df.to_csv('MyAutomationProject\\AnimeWebScrapeIMP\\scrapeData\\schedule.csv', mode='a', header=False, index=False)
                            except NoSuchElementException:
                                print("Time or film detail or episode not found for this entry.")
                                continue
                    except NoSuchElementException:
                        print("No schedule list found for this day.")

        except TimeoutException:
            print("Schedule not found on the page.")

        self.driver.close()
        self.driver.quit()
    
    def recentAnime(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="film_list-wrap"]'))
            )
            animeList = self.driver.find_elements(By.XPATH, '//div[@class="flw-item item-qtip"]')

            for item in animeList:
                try:
                    animeName = item.find_element(By.XPATH, './/h3[@class="film-name"]/a').text 
                    animeLink = item.find_element(By.XPATH, './/h3[@class="film-name"]/a').get_attribute('href')
                    print(f'Name: {animeName}, Link: {animeLink}')
                    df = pd.DataFrame({'Name': [animeName], 'Link': [animeLink]})
                    df.to_csv('MyAutomationProject\\AnimeWebScrapeIMP\\scrapeData\\recentupdate.csv', mode='a', header=False, index=False)
                except NoSuchElementException:
                    print("Name or link not found for this entry.")
                    continue
        
        except TimeoutException:
            print("Anime list not loaded on the page.")
        except Exception as e:
            print(f"Error occurred: {e}")
        
        self.driver.close()
        self.driver.quit()
    
    def filterBasedOnIntrestBased(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, ''))
            )

        except TimeoutException:
            print("Anime list not loaded on the page.")
        except Exception as e:
            print(f"Error occurred: {e}")
        
        self.driver.close()
        self.driver.quit()

