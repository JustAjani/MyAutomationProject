from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import datetime
import time
import base64
import sys
import os

class AniScrape:
    def __init__(self,mode):
        if mode == 'watch':
            self.animeName = input("Enter Anime Name: ")
            self.episodeNum = int(input("Enter Episode Number: "))
            self.command = input("Type 'enable' to enable auto skip intro and outro or 'disable' to disable features: ").lower()

        self.animUrl = None 
        self.episodeId = None
        service = Service(ChromeDriverManager().install())
        adblocker = Options()
        adblocker.add_extension(r'C:\\Users\\ajani\\Downloads\\MLOMIEJDFKOLICHCFLEJCLCBMPEANIIJ_10_4_3_0.crx') 
        self.driver = webdriver.Chrome(service=service, options=adblocker)
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
                                Episode = scheduleEntry.find_element(By.XPATH, './/button[@class="btn btn-sm btn-play"]').text
                                print(f"Time: {timeElement} | Anime Name: {filmDetail} | Episode: {Episode}")
                                df = pd.DataFrame({'Time': [timeElement], 'Anime Name': [filmDetail], 'Episode': [Episode]})
                                df.to_csv('Schedule.csv', mode='a', header=False, index=False)
                            except NoSuchElementException:
                                print("Time or film detail or episode not found for this entry.")
                                continue
                    except NoSuchElementException:
                        print("No schedule list found for this day.")
        except TimeoutException:
            print("Schedule not found on the page.")
        self.quit()

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
                        EC.element_to_be_clickable((By.ID, 'skip-outro'))
                    )

                    if nextEp.is_displayed() and nextEp.is_enabled():
                        nextEp.click()
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

    def manageDownloads(self):
        pathFolder = r'C:\\Users\\ajani\\Downloads\\animeScrape'
        while True:  
            if self.isBTNClick():
                self.downloadEpisode(pathFolder)
            time.sleep(1)
    
    def ensureDirectoryExists(self, path):
        directory = os.path.dirname(path)
        print(f"Checking if directory exists: {directory}")  
        if not os.path.exists(directory):
            print(f"Directory does not exist, creating: {directory}")  
            os.makedirs(directory)
        else:
            print(f"Directory already exists: {directory}")  
        
    def downloadBTN(self):
        dlBTN = """
                var dlButton = document.createElement('button');
                dlButton.innerText = 'Download Episode';
                dlButton.style.position = 'fixed';
                dlButton.style.top = '10px';
                dlButton.style.right = '10px';
                dlButton.onclick = function() { localStorage.setItem('downloadClicked', 'true'); };
                document.body.appendChild(dlButton);
                """
        self.driver.execute_script(dlBTN)
    
    def isBTNClick(self):
        downloadClicked = self.driver.execute_script("return localStorage.getItem('downloadClicked') === 'true';")
        if downloadClicked:
            self.driver.execute_script("localStorage.removeItem('downloadClicked');")  
            return True
        return False

    def downloadEpisode(self, destination):
        try:
            self.ensureDirectoryExists(destination)
            self.handleIframe()
            
            timeout = time.time() + 60 * 5  # Wait for up to 5 minutes.
            videoSrc = None

            while time.time() < timeout:
                videoSrc = self.driver.execute_script("""
                    var video = document.querySelector('#vidcloud-player > div.jw-wrapper.jw-reset > div.jw-media.jw-reset > video');
                    return video ? video.src : null;
                """)
                if videoSrc and videoSrc.startswith('blob:'):
                    print(f"Blob URL found: {videoSrc}")
                    break
                print("Waiting for video source...")
                time.sleep(5)  

            if not videoSrc:
                print("Video source URL not found or not valid.")
                return

            print("Handling blob URL for video.")
            dataUrl = self.driver.execute_async_script("""
                var blobUrl = arguments[0], callback = arguments[arguments.length - 1];
                var xhr = new XMLHttpRequest();
                xhr.open('GET', blobUrl, true);
                xhr.responseType = 'blob';
                xhr.onload = function() {
                    var reader = new FileReader();
                    reader.onload = function(e) {
                        callback(reader.result);  
                    };
                    reader.onerror = function() {
                        callback(null);
                    };
                    reader.readAsDataURL(xhr.response);
                };
                xhr.onerror = xhr.onabort = function() {
                    callback(null);  
                };
                xhr.send();
            """, videoSrc)

            if dataUrl and dataUrl.startswith('data:'):
                contentType, base64Data = dataUrl.split(';', 1)
                videoData = base64.b64decode(base64Data.split(',')[1])
                fileExtension = contentType.split('/')[1].split(';')[0]

                filePath = os.path.join(destination, f"downloaded_video.{fileExtension}")
                with open(filePath, 'wb') as file:
                    file.write(videoData)
                print(f"Video successfully downloaded to {filePath}")
            else:
                print("Failed to convert Blob URL to Data URL.")
        except Exception as e:
            print(f"An error occurred while trying to download the episode: {e}")

    def run(self):
        self.searchAnime()
        self.clickAnimeFromList()
        self.watchAnime()
        return self.driver

    def quit(self):
        input("Press Enter To Exit... ")
        self.driver.quit()
        sys.exit()

if __name__ == '__main__':
    startingPrompt = input("Do You Want To Watch Anime or See Schedule? Type 'watch' or 'schedule': ").lower()
    if startingPrompt == 'watch':
        AniScrape(startingPrompt).run()
    elif startingPrompt == 'schedule':
        AniScrape(startingPrompt).animeSchedule()





