import pytest_asyncio
import pytest
import asyncio
import re
from playwright.async_api import async_playwright
import logging
import time
import sys
import pandas as pd
import os
sys.path.append('C:\\Users\\ajani\\Downloads\\webscrapping 101\\MyAutomationProject')
from Logs.Alogger import setupLogging

logger = setupLogging('stonkError.log', 'stonkWarning.log', 'stonkInfo.log', 'stonkCritical.log', async_mode=True)
pytest_asyncio.plugin.DEFAULT_FIXTURE_SCOPE = "function" 

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
        user_agent='Mozilla/5.0 ...',
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
async def test_scrape(page):
    try:
        dir = 'MyAutomationProject/STONKMarket/stokedata'
        if not os.path.exists(dir):
            os.mkdir(dir)
            logger.info("Path created")
        else:
            logger.info("Path already exists")
        route = os.path.join(dir, 'NVDA.csv')
        
        await page.goto('https://finance.yahoo.com/chart/NVDA', timeout=30000, wait_until='domcontentloaded')
        page.on('response', lambda response: print(f"Received response with status {response.status} from {response.url}"))

        await page.wait_for_load_state("domcontentloaded", timeout=30000)
        stockPrices = page.locator('fin-streamer[data-test="qsp-price"]/span')
        priceChange = page.locator('fin-streamer[data-test="qsp-price-change"]/span')
        percentageChange = page.locator('fin-streamer[data-field="regularMarketChangePercent"]/span')

        startTime = time.time()
        StockData = []
        while (time.time() - startTime) < 300:
            try: 
                logger.info(f"Starting loop, time elapsed: {time.time() - startTime}")
                count = await stockPrices.count()
                countPriceChange = await priceChange.count()
                countPercentChange = await percentageChange.count()
                logger.info(f"Count: {count}, Count Change: {countPriceChange}, Count Percent Change: {countPercentChange}", flush=True)
                
                if count != 0 and countPriceChange != 0 and countPercentChange != 0:
                    stockPricesTxt = await stockPrices.text_content()
                    priceChangeTxt = await priceChange.text_content()
                    percentageChangeTxt = await percentageChange.text_content()
                    StockData.append({
                        'Stock Price': stockPricesTxt,
                        'Price Change': priceChangeTxt,
                        'Percentage Change': percentageChangeTxt,
                        'Timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    logger.info(f"Stock Prices: ${stockPricesTxt} Price Change by: ${priceChangeTxt} Percentage Change: %{percentageChangeTxt}" )
                    page.on('console', lambda msg: print(f"Console message: {msg.type}: {msg.text}"))
                else:
                    logger.info("Data not found, retrying...")
                await asyncio.sleep(1) 
            except Exception as e:
                logger.exception(f"Error Found: {str(e)}")
                break
        pd.DataFrame(StockData).to_csv(route, mode='a', header=False, index=False)
    except Exception as e:
        logger.exception(f"Error Found: {str(e)}")
        raise
