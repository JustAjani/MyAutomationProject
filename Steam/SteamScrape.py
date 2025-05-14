from playwright.async_api import async_playwright
import asyncio
import pandas as pd
import os
import logging
import smtplib
from email.message import EmailMessage
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import requests
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

class ScrapeSteam:
    def __init__(self, playwright):
        self.playwright = playwright
        self.url = 'https://store.steampowered.com/login/'
        self.steamURl = 'https://store.steampowered.com'
        Screenshot = r'MyAutomationProject/Steam/Screenshot'
        os.makedirs(Screenshot, exist_ok=True)
        DebugIncrement = len(os.listdir(Screenshot)) + 1
        self.screenshot = os.path.join(Screenshot, f'Error{DebugIncrement}.png') 
        logging.info("ScreenShot Debug Folder Created" if os.path.exists(self.screenshot) else "Debug Folder Doesn't Exist")

    
    async def SetUp(self):
        video = r'MyAutomationProject/Steam/Video'
        os.makedirs(video, exist_ok=True)
        logging.info("Video Debugging Folder Created" if os.path.exists(video) else "Video Debugging Folder Doesn't Exist")
        
        try:
            self.Browser = await self.playwright.chromium.launch(
                headless = False,
                slow_mo = 200
            )

            self.Context = await self.Browser.new_context(
                record_video_size = {"width": 1280, "height": 720},
                record_video_dir = video
            )
        except Exception as e:
            logging.exception(f'Context and Broswer Error is {e}')

    async def SteamPageLoad(self):
        try:
            self.page = await self.Context.new_page()
            await self.page.goto(self.url, wait_until = "domcontentloaded", timeout=30000)
            if self.page.url == self.url:
                logging.info("Page Loaded Successfully")
            elif self.page.url != self.url:
                self.page.bring_to_front()
        except Exception as e:
            logging.exception(f'Page Failure is {e}')
            await self.page.screenshot(self.screenshot)

    def Elements(self):
        return {
            'SignInBar': '(//input[@type="text"])[1]',
            'PasswordBar': '//input[@type="password"]',
            'LoginButton': '//button[@type="submit"]',
            'WishListButton': '//a[@id="wishlist_link"]',
            'WishListProfile': '//div[@class="wishlist_header"]',
            'WishListContent': '//div[@class="wishlist_row"]',
            'DiscountIndicator': '//div[@class="discount_pct"]'
        }
    
    async def GetElements(self, locator, attribute=None):
        Elements = self.Elements()
        try:
            FoundElement = self.page.locator(Elements[locator])
            count = await FoundElement.count()
            if count > 0:
                for i in range(count):
                    MultiElement = FoundElement.nth(i)
                    logging.info(f"Element {i + 1}/{count} Found: {locator}")
                    await MultiElement.scroll_into_view_if_needed()
            if await FoundElement.is_visible():
                logging.info(f"Element Found: {locator}")
            else:
                logging.info(f"Element Not Found: {locator}")
            if attribute:
                return await FoundElement.get_attribute(attribute)
            return FoundElement
        except Exception as e:
            logging.exception(f'Element Failure: {e}')
            await self.page.screenshot(self.screenshot)

    async def SignIn(self):
        try:
            User = os.getenv("STEAM_USER")
            PassWord = os.getenv("STEAM_PASS")
            SignInBar = await self.GetElements('SignInBar')
            PasswordBar = await self.GetElements('PasswordBar')
            LoginButton = await self.GetElements('LoginButton')
            
            if SignInBar and PasswordBar and LoginButton:
                await asyncio.sleep(2)
                await SignInBar.fill(User)
                await asyncio.sleep(2)
                await PasswordBar.fill(PassWord)
                await LoginButton.click()
                
                logging.info("Waiting For Manual SMS or Email Verification")

                await self.page.wait_for_selector(self.Elements['WishListButton'], timeout=10000)
                await self.SaveCookies()
                return True
            else:
                logging.info("Elements Not Found")
                await self.page.screenshot(path = self.screenshot)
        except Exception as e:
            logging.exception(f'SignIn Failure is {e}')
            await self.page.screenshot(path = self.screenshot)
    
    async def SaveCookies(self):
        try:
            Dir = 'MyAutomationProject/Steam/Cookies'
            os.makedirs(Dir, exist_ok=True)
            logging.info("Cookies Debugging Folder Created" if os.path.exists(Dir) else "Cookies Debugging Folder Doesn't Exist")

            self.CookiesDir = os.path.join(Dir, 'Cookies.csv')
            Cookies = await self.page.context.cookies()
            pd.DataFrame(Cookies).to_csv(self.CookiesDir, index=False)

            logging.info(f'Cookies after Save: {Cookies}')
        except Exception as e:
            logging.exception(f'Cookies Failure is {e}')
            await self.page.screenshot(path = self.screenshot)
    
    async def LoadCookies(self):    
        try:
            df = pd.read_csv(self.CookiesDir)
            for cookie in df.to_dict(orient='records'):
                await self.page.context.add_cookies([cookie])
        
        except Exception as e:
            logging.exception(f'Load Cookies Failure is {e}')
            await self.page.screenshot(path = self.screenshot)
            
    async def SteamScrape(self):
        try:
            self.GameInfo = []
            CsvPath = r'MyAutomationProject/Steam/'
            os.makedirs(CsvPath, exist_ok=True)
            CsvFile = os.path.join(CsvPath, 'SteamGames.csv')

            WishListButton = await self.GetElements('WishListButton')
            await WishListButton.click()
            
            WishListProfile = await self.GetElements('WishListProfile')
            WishListProfile.inner_text()
            WishListContent = await self.GetElements('WishListContent')
            DiscountIndicator = await self.GetElements('DiscountIndicator')

            if DiscountIndicator in await WishListContent.all_inner_texts():
                GamePicture = await WishListContent.locator('/a').get_attribute('src')
                GameName = await WishListContent.locator('/div[@class="content"]/a').inner_text()
                GamePrice = await WishListContent.locator('/div[@class="content"]/div/div[@class="purchase_container"]').inner_text()
                GameLink = await WishListContent.locator('/div[@class="content"]/a').get_attribute('href')
    
                self.GameInfo.append({
                    'GamePicture': GamePicture,
                    'GameName': GameName,
                    'GamePrice': GamePrice,
                    'GameLink': GameLink
                })

                logging.info(f'GameInfo: {self.GameInfo}')
                self.EmailGameInfo()
            else :
                logging.info("No Discount")
            
            if self.GameInfo:
                pd.DataFrame(self.GameInfo).to_csv(CsvFile, index=False)
                logging.info(f'GameInfo after Save: {self.GameInfo}')
            else:
                logging.info("GameInfo Not Found")
                await self.page.screenshot(path =self.screenshot)
                
        except Exception as e:
            logging.exception(f'SteamScrape Failure is {e}')
            await self.page.screenshot(path = self.screenshot)
    
    def EmailGameInfo(self):
        MyEmail = os.getenv("MY_EMAIL")
        MyPassword = os.getenv("MY_EMAIL_PASS")

        msg = EmailMessage()
        msg['Subject'] = 'Steam WishList Sale!!'
        msg['From'] = MyEmail
        msg['to'] = MyEmail
        html_content = f"""
        <html>
            <body>
                <h1>Steam WishList Sale!!</h1>
                <img src="cid:myimage">
                <p>{f"Name: {self.GameInfo['GameName']} <br> Price: {self.GameInfo['GamePrice']} <br> Link: {self.GameInfo['GameLink']}"}</p>
            </body>
        </html>
        """
        msg.set_content(html_content)

        try:
            Request = requests.get(self.GameInfo['GamePicture'])
            Request.raise_for_status()

            GameImage = MIMEImage(Request.content)
            GameImage.add_header('Content-ID', '<myimage>')
            msg.attach(GameImage)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(MyEmail, MyPassword)
                smtp.send_message(msg)
                logging.info("Email Sent")
        except Exception as e:
            logging.exception(f'EmailGameInfo Failure is {e}')
            self.page.screenshot(path = self.screenshot)

    async def TearDown(self):
        try:
            input("Press any key to exit...")
            await self.page.close()
            await self.Browser.close()
            await self.Context.close()
        except Exception as e:
            logging.exception(f'TearDown Failure is {e}')
            await self.page.screenshot(path = self.screenshot)
    
async def main():
    async with async_playwright() as playwright:
        steam = ScrapeSteam(playwright)
        await steam.SetUp()
        await steam.SteamPageLoad()
        await steam.SignIn()
        await steam.TearDown()

asyncio.run(main())
    
