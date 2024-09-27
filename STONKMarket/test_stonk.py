import pytest_asyncio
import pytest
import asyncio
import logging
import time
import sys
import pandas as pd
import os
from playwright.async_api import async_playwright, Page

sys.path.append('C:\\Users\\ajani\\Downloads\\webscrapping 101\\MyAutomationProject')
from Logs.Alogger import setupLogging

logger = setupLogging('stonkError.log', 'stonkWarning.log', 'stonkInfo.log', 'stonkCritical.log')



@pytest_asyncio.fixture(scope="session")
async def playwrightInstance():
    async with async_playwright() as playwright:
        yield playwright

@pytest_asyncio.fixture(scope="session")
async def context(playwrightInstance):
    browser = await playwrightInstance.chromium.launch(
        headless=False,
        slow_mo=200,
    )

    context = await browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 OPR/113.0.0.0',
        record_video_dir='MyAutomationProject/STONKMarket/video',
        record_video_size={'width': 1920, 'height': 1080}
    )

    yield context
    await context.close()
    await browser.close()

@pytest_asyncio.fixture(scope="function")
async def page(context):
    page = await context.new_page()
    yield page
    await page.close()

@pytest.mark.asyncio
async def test_scrape(page: Page):
    try:
        baseUrl = 'https://finance.yahoo.com/chart/NVDA#eyJsYXlvdXQiOnsiaW50ZXJ2YWwiOjEsInBlcmlvZGljaXR5IjoxLCJ0aW1lVW5pdCI6Im1pbnV0ZSIsImNhbmRsZVdpZHRoIjoyLjgyMzIzNDEwNzAxMDE2MjMsImZsaXBwZWQiOmZhbHNlLCJ2b2x1bWVVbmRlcmxheSI6dHJ1ZSwiYWRqIjp0cnVlLCJjcm9zc2hhaXIiOnRydWUsImNoYXJ0VHlwZSI6Im1vdW50YWluIiwiZXh0ZW5kZWQiOmZhbHNlLCJtYXJrZXRTZXNzaW9ucyI6e30sImFnZ3JlZ2F0aW9uVHlwZSI6Im9obGMiLCJjaGFydFNjYWxlIjoibGluZWFyIiwicGFuZWxzIjp7ImNoYXJ0Ijp7InBlcmNlbnQiOjEsImRpc3BsYXkiOiJOVkRBIiwiY2hhcnROYW1lIjoiY2hhcnQiLCJpbmRleCI6MCwieUF4aXMiOnsibmFtZSI6ImNoYXJ0IiwicG9zaXRpb24iOm51bGx9LCJ5YXhpc0xIUyI6W10sInlheGlzUkhTIjpbImNoYXJ0Iiwi4oCMdm9sIHVuZHLigIwiXX19LCJzZXRTcGFuIjp7Im11bHRpcGxpZXIiOjEsImJhc2UiOiJ0b2RheSIsInBlcmlvZGljaXR5Ijp7ImludGVydmFsIjoxLCJwZXJpb2QiOjEsInRpbWVVbml0IjoibWludXRlIn0sInNob3dFdmVudHNRdW90ZSI6dHJ1ZSwiZm9yY2VMb2FkIjp0cnVlLCJ1c2VFeGlzdGluZ0RhdGEiOnRydWV9LCJvdXRsaWVycyI6ZmFsc2UsImFuaW1hdGlvbiI6dHJ1ZSwiaGVhZHNVcCI6eyJzdGF0aWMiOnRydWUsImR5bmFtaWMiOmZhbHNlLCJmbG9hdGluZyI6ZmFsc2V9LCJsaW5lV2lkdGgiOjIsImZ1bGxTY3JlZW4iOnRydWUsInN0cmlwZWRCYWNrZ3JvdW5kIjp0cnVlLCJjb2xvciI6IiMwMDgxZjIiLCJzeW1ib2xzIjpbeyJzeW1ib2wiOiJOVkRBIiwic3ltYm9sT2JqZWN0Ijp7InN5bWJvbCI6Ik5WREEiLCJxdW90ZVR5cGUiOiJFUVVJVFkiLCJleGNoYW5nZVRpbWVab25lIjoiQW1lcmljYS9OZXdfWW9yayIsInBlcmlvZDEiOjE3MjcyNzI4MDAsInBlcmlvZDIiOjE3Mjc0NDU2MDB9LCJwZXJpb2RpY2l0eSI6MSwiaW50ZXJ2YWwiOjEsInRpbWVVbml0IjoibWludXRlIiwic2V0U3BhbiI6eyJtdWx0aXBsaWVyIjoxLCJiYXNlIjoidG9kYXkiLCJwZXJpb2RpY2l0eSI6eyJpbnRlcnZhbCI6MSwicGVyaW9kIjoxLCJ0aW1lVW5pdCI6Im1pbnV0ZSJ9LCJzaG93RXZlbnRzUXVvdGUiOnRydWUsImZvcmNlTG9hZCI6dHJ1ZSwidXNlRXhpc3RpbmdEYXRhIjp0cnVlfX1dLCJzdHVkaWVzIjp7IuKAjHZvbCB1bmRy4oCMIjp7InR5cGUiOiJ2b2wgdW5kciIsImlucHV0cyI6eyJTZXJpZXMiOiJzZXJpZXMiLCJpZCI6IuKAjHZvbCB1bmRy4oCMIiwiZGlzcGxheSI6IuKAjHZvbCB1bmRy4oCMIn0sIm91dHB1dHMiOnsiVXAgVm9sdW1lIjoiIzBkYmQ2ZWVlIiwiRG93biBWb2x1bWUiOiIjZmY1NTQ3ZWUifSwicGFuZWwiOiJjaGFydCIsInBhcmFtZXRlcnMiOnsiY2hhcnROYW1lIjoiY2hhcnQiLCJlZGl0TW9kZSI6dHJ1ZSwicGFuZWxOYW1lIjoiY2hhcnQifSwiZGlzYWJsZWQiOmZhbHNlfX19LCJldmVudHMiOnsiZGl2cyI6dHJ1ZSwic3BsaXRzIjp0cnVlLCJ0cmFkaW5nSG9yaXpvbiI6Im5vbmUiLCJzaWdEZXZFdmVudHMiOltdfSwicHJlZmVyZW5jZXMiOnsiY3VycmVudFByaWNlTGluZSI6dHJ1ZSwiZGlzcGxheUNyb3NzaGFpcnNXaXRoRHJhd2luZ1Rvb2wiOmZhbHNlLCJkcmF3aW5ncyI6bnVsbCwiaGlnaGxpZ2h0c1JhZGl1cyI6MTAsImhpZ2hsaWdodHNUYXBSYWRpdXMiOjMwLCJtYWduZXQiOmZhbHNlLCJob3Jpem9udGFsQ3Jvc3NoYWlyRmllbGQiOm51bGwsImxhYmVscyI6dHJ1ZSwibGFuZ3VhZ2UiOm51bGwsInRpbWVab25lIjoiQW1lcmljYS9OZXdfWW9yayIsIndoaXRlc3BhY2UiOjUwLCJ6b29tSW5TcGVlZCI6bnVsbCwiem9vbU91dFNwZWVkIjpudWxsLCJ6b29tQXRDdXJyZW50TW91c2VQb3NpdGlvbiI6ZmFsc2V9fQ--'
        dir = 'MyAutomationProject/STONKMarket/stokedata'
        os.makedirs(dir, exist_ok=True)
        logger.info("Path created" if not os.path.exists(dir) else "Path already exists")
        route = os.path.join(dir, 'NVDA.csv')
        
        logger.info("Navigating to website")
        try:
            await page.goto(baseUrl, wait_until='domcontentloaded',timeout=30)
            logger.info(f"Navigated to {page.url}")
        except Exception as e:
            logger.error(f"Error during page.goto: {e}")
            raise
        
        page.on('console', lambda msg: logger.info(f"Console {msg.type}: {msg.text}"))

        await page.wait_for_selector('fin-streamer[data-test="qsp-price"] span', state='visible', timeout=30000)
        await page.wait_for_selector('fin-streamer[data-test="qsp-price-change"] span', state='visible', timeout=30000)
        await page.wait_for_selector('fin-streamer[data-field="regularMarketChangePercent"] span', state='visible', timeout=30000)

        startTime = time.time()
        StockData = []
        while (time.time() - startTime) < 300:
            try: 
                logger.info(f"Starting loop, time elapsed: {time.time() - startTime:.2f}")
                
                stockPrices = page.locator('fin-streamer[data-test="qsp-price"] span')
                priceChange = page.locator('fin-streamer[data-test="qsp-price-change"] span')
                percentageChange = page.locator('fin-streamer[data-field="regularMarketChangePercent"] span')
                
                stockPricesTxt = await stockPrices.inner_text()
                priceChangeTxt = await priceChange.inner_text()
                percentageChangeTxt = await percentageChange.inner_text()
                
                if stockPricesTxt and priceChangeTxt and percentageChangeTxt:
                    StockData.append({
                        'Stock Price': stockPricesTxt,
                        'Price Change': priceChangeTxt,
                        'Percentage Change': percentageChangeTxt,
                        'Timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    logger.info(f"Stock Price: ${stockPricesTxt} Price Change: ${priceChangeTxt} Percentage Change: {percentageChangeTxt}")
                else:
                    logger.warning("Some data not found, retrying...")
                
                await asyncio.sleep(1)
            except Exception as e:
                logger.exception(f"Error in scraping loop: {str(e)}")
        
        if StockData:
            pd.DataFrame(StockData).to_csv(route, mode='a', header=not os.path.exists(route), index=False)
            logger.info(f"Data saved to {route}")
        else:
            logger.warning("No data was collected during the scraping session")

        # assertions to verify the scraping was successful
        assert len(StockData) > 0, "No data was scraped"
        assert all(key in StockData[0] for key in ['Stock Price', 'Price Change', 'Percentage Change', 'Timestamp']), "Missing expected data fields"
        
    except Exception as e:
        logger.exception(f"Error in test_scrape: {str(e)}")
        raise
