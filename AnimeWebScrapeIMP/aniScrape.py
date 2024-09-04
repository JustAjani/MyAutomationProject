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
import time
import base64
from tqdm import tqdm  # tqdm is a library that provides a progress meter
import sys
import os

class AniScrape:
    def __init__(self, animeName):
        self.animeName = animeName
        self.animUrl = None 
        self.episodeId = None
        service = Service(ChromeDriverManager().install())
        adblocker = Options()
        adblocker.add_extension(f'C:\\Users\\ajani\Downloads\\MLOMIEJDFKOLICHCFLEJCLCBMPEANIIJ_10_4_3_0.crx')
        self.driver = webdriver.Chrome(service=service, options=adblocker)
        
    def saveAnimeList(self, category):
        AnimFound = []
        link = []
        AnimFound.append(category.text)
        link.append(category.get_attribute('href'))
        df = pd.DataFrame({'Anime Found': AnimFound, 'Link': link})
        df.to_csv('AnimeList.csv', index=False)

    def searchAnime(self):
        self.driver.get('https://9animetv.to/home')
        search = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="keyword"]'))
        )
        search.send_keys(self.animeName + Keys.ENTER)
    
    def clickAnimeFromList(self):
        self.driver.get(f'https://9animetv.to/search?keyword={self.animeName.replace(" ", "+")}')
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//h3[@class="film-name"]/a'))
        )
        categories = self.driver.find_elements(By.XPATH, '//h3[@class="film-name"]/a')
        for category in categories:
            if self.animeName.lower() == category.text.lower():
                self.driver.execute_script("arguments[0].scrollIntoView(true);", category)
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(category)
                )
                self.animUrl = category.get_attribute('href')  
                print(f"Captured URL: {self.animUrl}")  
                break
    
    def watchAnime(self, Epnum):
        if self.animUrl:
            try:
                print(f"Navigating to URL: {self.animUrl}")
                self.driver.get(self.animUrl)
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//a[@data-id]'))
                )
                episodes = self.driver.find_elements(By.XPATH, '//a[@data-id]')
                baseId = int(episodes[0].get_attribute('data-id'))
                targetId = baseId + (Epnum - 1)

                foundEpisode = False
                for episode in episodes:
                    self.episodeId = int(episode.get_attribute('data-id'))
                    if self.episodeId == targetId:
                        foundEpisode = True
                        episodeUrl = f"{self.animUrl}?ep={targetId}"
                        print(f"Navigating directly to episode URL: {episodeUrl}")
                        self.driver.get(episodeUrl)
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@class='video-player']"))
                        )
                        print("Episode loaded successfully.")
                        break

                if not foundEpisode:
                    ranges = self.driver.find_elements(By.XPATH, '//ul[@class="ulclear ranges"]')
                    for range_ in ranges:
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", range_)
                        episodes = range_.find_elements(By.XPATH, './/a[@data-id]')
                        for episode in episodes:
                            if self.episodeId == targetId:
                                foundEpisode = True
                                episodeUrl = f"{self.animUrl}?ep={targetId}"
                                print(f"Navigating directly to episode URL: {episodeUrl}")
                                self.driver.get(episodeUrl)
                                WebDriverWait(self.driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, "//div[@class='video-player']"))
                                )
                                print("Episode loaded successfully.")
                                break
                elif targetId != targetId:
                    print(f"No episode found with data-id {targetId}, loading episode 1 instead.")
                    firstEpisodeId = int(episodes[0].get_attribute('data-id'))
                    firstEpisodeUrl = f"{self.animUrl}?ep={firstEpisodeId}"
                    print(f"Navigating directly to episode URL: {firstEpisodeUrl}")
                    self.driver.get(firstEpisodeUrl)
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@class='video-player']"))
                    )
                    print("First episode loaded successfully.")
            except Exception as e:
                print(f"An error occurred during episode navigation: {e}")

              
            self.skipIntro()
            self.nextEpisode(self.episodeId)
            self.quit()
    
    def handleIframe(self):
        if 'iframe-embed' not in self.driver.current_url:
                        WebDriverWait(self.driver, 5).until(
                            EC.frame_to_be_available_and_switch_to_it((By.ID, 'iframe-embed'))
                        )

    def skipIntro(self):
        try:
            introSkipped = False
            start_time = time.time()

            while not introSkipped and (time.time() - start_time) < 300:
                try:
                    self.handleIframe()

                    timeText = self.driver.execute_script("""
                        var elem = document.querySelector('#vidcloud-player > div.jw-wrapper.jw-reset > div.jw-controls.jw-reset > div.jw-controlbar.jw-reset > div.jw-reset.jw-button-container > div.jw-icon.jw-icon-inline.jw-text.jw-reset.jw-text-elapsed');
                        return elem ? elem.textContent : 'not found';
                    """)


                    if timeText == 'not found':
                        print("Time element not found, retrying...")
                        time.sleep(1)
                        continue

                    if ':' in timeText:
                        minutes, seconds = timeText.split(':')
                        elapsedSeconds = int(minutes) * 60 + int(seconds)
                        print(f"Current video time: {elapsedSeconds} seconds")
                    else:
                        print("Time text not in expected format:", timeText)
                        continue

                    if elapsedSeconds <= 600:
                        self.driver.execute_script("var btn = document.querySelector('#skip-intro'); if (btn) btn.click();")
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

    def nextEpisode(self, Epnum):  
        try:
            nextEp = False
            startTime = time.time()
            while not nextEp and (time.time() - startTime) < 1380:
                try:
                    self.handleIframe()
                    timeText = self.driver.execute_script("""
                        var elem = document.querySelector('#vidcloud-player > div.jw-wrapper.jw-reset > div.jw-controls.jw-reset > div.jw-controlbar.jw-reset > div.jw-reset.jw-button-container > div.jw-icon.jw-icon-inline.jw-text.jw-reset.jw-text-countdown');
                        return elem ? elem.textContent : 'not found';
                    """)

                    if timeText == 'not found':
                        print("Time element not found, retrying...")
                        time.sleep(1)
                        continue

                    if ':' in timeText:
                        minutes, seconds = timeText.split(':')
                        countDownSeconds = int(minutes) * 60 + int(seconds)
                    else:
                        print("Time text not in expected format:", timeText)
                        continue

                    if countDownSeconds <= 120:
                        self.driver.execute_script("var btn = document.querySelector('#next-episode'); if (btn) btn.click();")
                        episodeUrl = f"{self.animUrl}?ep={Epnum + 1}"
                        self.driver.get(episodeUrl)
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
    
    def ensureDirectoryExists(self,path):
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def downLoadEpisode(self, destination):
        try:
            self.ensureDirectoryExists(destination)
            self.handleIframe()
            videoSrc = self.driver.execute_script("""
                    var video = document.querySelector('#vidcloud-player > div.jw-wrapper.jw-reset > div.jw-media.jw-reset > video')
                    return video ? video.src : 'not found'""")
            print(f"Video source URL: {videoSrc}")

            if videoSrc == 'not found':
                print("Video source not found.")
                return
            if videoSrc.startswith('blob:'):
                dataUrl = self.driver.execute_script("""
                    var blobUrl = arguments[0];
                    var xhr = new XMLHttpRequest();
                    xhr.open('GET', blobUrl, true);
                    xhr.responseType = 'blob';
                    xhr.onload = function() {
                        var reader = new FileReader();
                        reader.onload = function(e) {
                            window.dataURL = reader.result;
                        };
                        reader.readAsDataURL(xhr.response);
                    };
                    xhr.send();
                    return 'dataURL ready';
                """, videoSrc)
                time.sleep(10)
                dataUrl = self.driver.execute_script("return window.dataURL;")
            else:
                dataUrl = videoSrc
            
            if dataUrl.startswith('data:'):
                contentType,base64Data = dataUrl.split(';',1)
                videoData = base64.b64decode(base64Data)
                fileExtension =contentType.split('/')[1].split(';')[0]

            # Write video data to file
                filePath = os.path.join(destination, f"downloaded_video.{fileExtension}")
                with open(filePath, 'wb') as file:
                    file.write(videoData)
                print(f"Video successfully downloaded to {filePath}")
            else:
                print("Failed to convert Blob URL to Data URL.")
        except Exception as e:
            print(f"An error occurred while trying to download the episode: {e}")


    def run(self, Epnum):
        self.searchAnime()
        self.clickAnimeFromList()
        self.watchAnime(Epnum)
        self.skipIntro()
        self.nextEpisode(self.episodeId)
        return self.driver

    def quit(self):
        input("Press Enter To Exit... ")
        self.driver.quit()
        sys.exit()

animInput = input("Enter Anime Name: ")
episodeNum = int(input("Enter Episode Number: "))
Anime = AniScrape(animInput).run(episodeNum)
