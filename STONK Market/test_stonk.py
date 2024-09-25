import pytest_asyncio
import pytest
import asyncio
import re
from playwright.async_api import async_playwright
import logging
import time

logging.basicConfig(level=logging.INFO)
pytest_asyncio.plugin.DEFAULT_FIXTURE_SCOPE = "session" 

@pytest_asyncio.fixture(scope="session")
async def playwrightInstance():
    async with async_playwright() as playwright:
        yield playwright

@pytest_asyncio.fixture(scope="session")
async def context (playwrightInstance):
    browser = await playwrightInstance.chromium.launch(
        headless= False,
        slow_mo = 200,
        )
    
    context = await browser.new_context(
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 OPR/113.0.0.0',
        viewport = {'width': 1920, 'height': 1080},
        record_video_dir = 'STONK Market/video',
        record_video_size = {'width': 1920, 'height': 1080}
    )

    yield context 
    await context.close()
    await browser.close()
    
@pytest_asyncio.fixture
async def page(context):
    page = await context.new_page()
    page.on("console", lambda msg: print(f"Console message: {msg.type}: {msg.text}"))
    yield page
    await page.close()
    
@pytest.mark.asyncio
async def test_scrape(page):
    try:
        await page.goto('https://www.marketwatch.com/investing/stock/nvda?mod=search_symbol', timeout=70000)
        assert page.url == 'https://www.marketwatch.com/investing/stock/nvda?mod=search_symbol'
        stockPrices = page.locator('bg-quote.value')
        
        startTime = time.time()
        while (time.time() - startTime) < 300:
            if await stockPrices.count() == 0:
                logging.info("Stock Prcies Not Found")
            else:
                stockPricesTxt = await stockPrices.text_content()
                logging.info(f"Stock Prices ${stockPricesTxt}")
            await asyncio.sleep(1)
            
    except Exception as e:
        logging.exception("Error Found:", str(e))
        raise

