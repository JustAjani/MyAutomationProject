from playwright.async_api import async_playwright
import asyncio
import pandas as pd

async def run(playwright):

    searchQuery = input("Enter search query: ").lower()
    if "tut" or "tutorial" in searchQuery:

        browser = await playwright.chromium.launch( 
            headless=False,
            slow_mo=200, 
            args=[
                f'--start-maximized'
            ]
        )

        context = await browser.new_context(
            record_video_dir='YTTutFinder/videos',
            record_video_size={'width': 1920, 'height': 1080},
            )

        page = await context.new_page()
        await page.goto("https://youtube.com", timeout=70000)

        try:
            searchBar = page.locator('//input[@id="search"]')
            await searchBar.fill(searchQuery)
            searchValue = await searchBar.input_value()

            if searchValue == searchQuery:
                print(f"Search input value: {searchValue}")
            else:
                print(f"Search input value mismatch: {searchValue}")
        except Exception as e:
            print(f"Error filling search input: {e}")

        try:
            searchBTN = page.locator('//button[@id="search-icon-legacy"]')
            await searchBTN.hover()
            await searchBTN.dblclick(force=True)  
            print("Search button clicked")
        except Exception as e:
            print(f"Error pressing Enter: {e}")

        try:
            scrollHight = await page.evaluate('document.body.scrollHeight')
            while True:
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(2000)
                newScrollHight = await page.evaluate('document.body.scrollHeight')
                if newScrollHight == scrollHight:
                    break
                scrollHight = newScrollHight
                print("Scrolled to the bottom of the page")

            titles = page.locator('//a[@id="video-title"]')  
            
            videoData = []
            count = await titles.count()
            if count == 0:
                print("No titles found")
            else:
                print(f"Total titles found: {count}")

            if not titles:
                print("No titles found")
            else:
                for i in range(count):
                    titleText = await titles.nth(i).inner_text()
                    titleHref = await titles.nth(i).get_attribute('href')
                    titleLink = f"https://youtube.com{titleHref}"
                    videoData.append(f'Title: {titleText} | Link: {titleLink}')
                    print(f"Title: {titleText} | Link: {titleLink}")
                    
                pd.DataFrame(videoData).to_csv("PlaywrightTut\\YoutubeVideos.csv", mode='a', header=True, index=False)
        except Exception as e:
            print(f"Error fetching video titles: {e}")
        
        await context.close()
        await browser.close()
    else:
        print("Search query is not related to Tutorials")

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())
