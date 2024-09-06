from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import sys
from animeScrape import AnimeScrape
import logging

class AniMATION:
    def __init__(self,mode):
        logging.info("AniMATION initialized with mode: %s", mode)
        if mode == 'watch':
            self.animeName = input("Enter Anime Name: ")
            self.episodeNum = int(input("Enter Episode Number: "))
            self.command = input("Type 'enable' to enable auto skip intro and outro or 'disable' to disable features: ").lower()
        
        try:
            self.mode = mode
            self.animUrl = None
            self.episodeId = None
            service = Service(ChromeDriverManager().install())
            adblocker = Options()
            adblocker.add_extension(r'C:\\Users\\ajani\\Downloads\\MLOMIEJDFKOLICHCFLEJCLCBMPEANIIJ_10_4_3_0.crx')
            self.driver = webdriver.Chrome(service=service, options=adblocker)
            logging.info("WebDriver started successfully")
        except Exception as e:
            logging.critical("Failed to start WebDriver: %s", e)
            sys.exit(1)
        
        self.animeScrape = AnimeScrape(self.driver)
        self.driver.set_script_timeout(60)

    def searchAnime(self):
        self.driver.get('https://9animetv.to/home')
        try:
            search = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@name="keyword"]'))
            )
            search.send_keys(self.animeName + Keys.ENTER)
        except TimeoutException:
            print("Search bar not found on the page.")

    def clickAnimeFromList(self):
        self.driver.get(self.driver.current_url)
        try:
            categories = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//h3[@class="film-name"]/a'))
            )
            for category in categories:
                if self.animeName.lower() == category.text.lower():
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", category)
                    WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(category)
                    )
                    self.animUrl = category.get_attribute('href')  
                    print(f"Captured URL: {self.animUrl}")  
                    break
        except TimeoutException:
            print("Anime list not loaded or no matching anime found.")
    
    def watchAnime(self):
            if self.animUrl:
                try:
                    print(f"Navigating to URL: {self.animUrl}")
                    self.driver.get(self.animUrl)
                    episodes = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH, '//a[@data-id]'))
                    )
                    baseId = int(episodes[0].get_attribute('data-id'))
                    targetId = baseId + (self.episodeNum - 1)

                    foundEpisode = False
                    for episode in episodes:
                        self.episodeId = int(episode.get_attribute('data-id'))
                        if self.episodeId == targetId:
                            foundEpisode = True
                            episodeUrl = f"{self.animUrl}?ep={targetId}"
                            print(f"Navigating directly to episode URL: {episodeUrl}")
                            break

                    if not foundEpisode:
                        ranges = self.driver.find_elements(By.XPATH, '//ul[@class="ulclear ranges"]')
                        for range_ in ranges:
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", range_)
                            episodes = range_.find_elements(By.XPATH, './/a[@data-id]')
                            for episode in episodes:
                                if int(episode.get_attribute('data-id')) == targetId:
                                    foundEpisode = True
                                    episodeUrl = f"{self.animUrl}?ep={targetId}"
                                    print(f"Navigating directly to episode URL: {episodeUrl}")
                                    break
                    
                    if not foundEpisode:
                        firstEpisodeId = int(episodes[0].get_attribute('data-id'))
                        episodeUrl = f"{self.animUrl}?ep={firstEpisodeId}"
                        print(f"No episode found with ID {targetId}, loading episode 1 instead: {episodeUrl}")
    
                    self.driver.get(episodeUrl)
                    self.enableFeatures()

                except Exception as e:
                    print(f"An error occurred during episode navigation: {e}")
                finally:
                    self.quit()

    def handleIframe(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, 'iframe-embed'))
            )
        except TimeoutException:
            print("Failed to load iframe.")
    
    def enableFeatures(self): 
        if self.command == 'enable':
            try:
                self.skipIntro()
                self.nextEpisode()
                print("Features enabled.")
                return True
            except Exception as e:
                print(f"Failed to enable features: {e}")
        elif self.command == 'disable':
            print("Features disabled.")
            return False
        else:
            print("Invalid command.")
            return False

    def skipIntro(self):
        try:
            introSkipped = False
            start_time = time.time()

            while not introSkipped and (time.time() - start_time) < 300:
                try:
                    self.handleIframe()
                    SkipBTN = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.ID, 'skip-intro'))
                        )
                        
                    if SkipBTN.is_displayed() and SkipBTN.is_enabled():
                        SkipBTN.click()
                        print("Intro skipped successfully.")
                        introSkipped = True

                    self.driver.switch_to.default_content()
                    introSkipped = False
                except Exception as e:
                    print(f"Error checking time or clicking button: {e}")
                finally:
                    self.driver.switch_to.default_content()
            if not introSkipped:
                print("Intro skip period passed without skipping.")
        except Exception as e:
            print(f"General error during intro skipping: {e}")

    def nextEpisode(self):  
        try:
            nextEp = False
            startTime = time.time()
            while not nextEp and (time.time() - startTime) < 1380:
                try:
                    self.handleIframe()
        
                    nextEp = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="skip-outro"]'))
                    )

                    if nextEp.is_displayed() and nextEp.is_enabled():
                        self.driver.execute_script("arguments[0].click();", nextEp)
                        skippedEp = f"{self.animUrl}?ep={self.episodeNum + 1}"
                        self.driver.get(skippedEp)
                        print("Next episode loaded successfully.")
                        nextEp = True 

                except Exception as e:
                    print(f"Error checking time or clicking button: {e}")
                finally:
                    self.driver.switch_to.default_content() 

        except TimeoutException:
            print("Timeout occurred waiting for countdown timer.")
        except NoSuchElementException:
            print("Countdown timer element not found.")
        except ValueError:
            print("Error processing countdown timer value.")
        self.quit()

    def run(self):
        if self.mode == 'watch':
            self.searchAnime()
            self.clickAnimeFromList()
            self.watchAnime()
        elif self.mode == 'schedule':
            self.animeScrape.animeSchedule()
        return self.driver

    def quit(self):
        input("Press Enter To Exit... ")
        self.driver.quit()
        sys.exit()

if __name__ == '__main__':
    startingPrompt = input("Do You Want To Watch Anime or See Schedule? Type 'watch' or 'schedule': ").lower()
    AniMATION(startingPrompt).run()





