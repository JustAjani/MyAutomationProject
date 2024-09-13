from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import logging
from logging.handlers import RotatingFileHandler
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
import sys
import time
import re
sys.path.append('C:\\Users\\ajani\\Downloads\\webscrapping 101\\MyAutomationProject')
from Logs.Alogger import setupLogging

print("Import successful!")

class MangaScrape:
    def __init__(self):
        self.mangaName = input("Enter manga name: ").lower()
        self.mangaNum = int(input("Enter manga chapter number: "))
        self.mangaChapter = f'chapter {self.mangaNum}'
        self.logger = setupLogging(ERROR="MANGAERROR.log", WARNING="MANGAWARNING.log", INFO="MANGAINFO.log")
        service = Service(ChromeDriverManager().install())
        self.adblocker = Options()
        self.adblockerPath =  r'C:\\Users\\ajani\\Downloads\\MLOMIEJDFKOLICHCFLEJCLCBMPEANIIJ_10_4_3_0.crx'
        self.adblocker.page_load_strategy = 'eager'
        # self.adblocker.add_extension(self.adblockerPath)
        self.driver = webdriver.Chrome(service=service, options=self.adblocker)
        self.baseUrl = "https://mangakakalot.com/?order=reply_count"
        logging.info("WebDriver started successfully")
    
    def searchManga(self):
        try:
            logging.info("Searching for manga: ", self.mangaName)
            self.driver.maximize_window()
            self.driver.get(self.baseUrl)

            search = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@id="search_story"]'))
            )
            search.send_keys(self.mangaName + Keys.ENTER)
            self.logger.info("Manga searched successfully")
        except Exception as e:
            self.logger.error("Failed to search manga: %s", e)
        
        return self.logger.info("Manga searched: ", self.mangaName)

    def clickMangaFromList(self):
        self.driver.get(self.driver.current_url)
        try:
            logging.info("Clicking on manga: ", self.mangaName)
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="panel_story_list"]'))
            )
            mangaList = self.driver.find_elements(By.XPATH, './/h3[@class="story_name"]/a',)
    
            for manga in mangaList:
                try:
                    if manga.text.lower() == self.mangaName:
                        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(manga))
                        manga.click()
                        logging.info("Clicked on manga: %s", manga.text)
                        break
                except StaleElementReferenceException:
                    self.logger.error("Stale element reference exception: %s", manga.text)
                    mangaList = self.driver.find_elements(By.XPATH, './/h3[@class="story_name"]/a')
                    return self.clickMangaFromList()
        
        except StaleElementReferenceException:
            self.logger.error("Stale element reference exception: %s", self.mangaName)
        except NoSuchElementException:
            self.logger.error("Manga not found for clicking")
        except TimeoutException:
            self.logger.error("Element not found for clicking")
        except Exception as e:
            self.logger.error("Failed to click manga: %s", str(e))
        
        return self.logger.info("clicked on manga: ", self.mangaName)
    
    def loadMangaNFindChapters(self):
        self.driver.get(self.driver.current_url)
        try:
            self.logger.info("Loading manga: ", self.mangaName)
            chapters = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//ul[@class="row-content-chapter"]'))
            )
            found = False
            retries = 0
            maxRetries = 5

            while not found and retries < maxRetries:
                chapterList = chapters.find_elements(By.XPATH, './li/a')
                for chapter in chapterList:
                    try:
                        chapterTXT = chapter.text.lower()
                        match = re.search(r"chapter\s(\d+)", chapterTXT)
                        if match:
                            self.mangaNum = f'chapter {int(match.group(1))}'
                        if self.mangaChapter.lower() == self.mangaNum.lower():
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", chapter)
                            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(chapter))
                            chapter.click()
                            self.logger.info("Clicked on chapter: ", chapter.text)
                            found = True
                            break 
                    except NoSuchElementException:
                        self.logger.error("Chapter not found")
                    except StaleElementReferenceException:
                        chapter = chapters.find_elements(By.XPATH, './li/a')
                        self.logger.info("Chapter list refreshed")
                        break
            
                if not found:
                    try:
                        retries += 1
                        self.driver.execute_script("arguments[0].scrollTop += arguments[1];", chapterList, 1000)
                    except StaleElementReferenceException:
                        chapter = chapters.find_elements(By.XPATH, './li/a')
                        continue
                    except Exception as e:
                        logging.error("Failed to scroll: %s", e)
            
            if not found:
                self.logger.error(f"Chapter {self.mangaNum} not found after scrolling.")

        except TimeoutException:
            self.logger.error("Element not found for loading chapters")
        except NoSuchElementException:
            self.logger.error("Manga not found")
        except Exception as e:
            self.logger.error("Failed to load manga: %s", e)

        return logging.info("Manga Chapter Clikced on: ", self.mangaChapter)
    
    def nextChapter(self):
        nextChap = False
        startTime = time.time()

        while not nextChap and (time.time() - startTime) < 1380:
            try:
                nextChapterBTN = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, '(//a[@class="navi-change-chapter-btn-next a-h"])[last()]'))
                )
                
                input("Press Enter to proceed to the next chapter or type 'n' to cancel: ")

                if nextChapterBTN.is_enabled() and nextChapterBTN.is_displayed():
                    nextChapterBTN.click()
                    self.logger.info("Clicked on next chapter")
                    nextChap = True
                else:
                    self.logger.info("Next chapter button not found, attempting to find again...")
                nextChap = False

            except StaleElementReferenceException:
                self.logger.error("StaleElementReferenceException encountered, retrying...")
                time.sleep(1) 
            except TimeoutException:
                self.logger.error("TimeoutException: Element not found for next chapter")
                break  
            except NoSuchElementException:
                self.logger.error("NoSuchElementException: Manga not found")
                break  
            except Exception as e:
                self.logger.error("Failed to load manga: %s", str(e))
                break 

        if not nextChap:
            self.logger.info("Failed to proceed to next chapter after several attempts.")

    def closeBrowser(self):
        if input("Press Enter to exit or type 'x' to keep session open: ").lower() == "x":
            self.logger.info("Session remains open for manual control.")
        else:
            self.driver.quit()
            self.logger.info("WebDriver closed successfully")
            self.driver.close()
            self.logger.info("Browser closed successfully")
            sys.exit()

    def run(self):
        self.searchManga()
        self.clickMangaFromList()
        self.loadMangaNFindChapters()
        self.nextChapter()
        self.closeBrowser()

MangaScrape().run()