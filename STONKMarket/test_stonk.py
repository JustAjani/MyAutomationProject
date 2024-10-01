import pytest
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import time
import sys
import pandas as pd
import os
from playwright.sync_api import sync_playwright, Page, Route, Request, TimeoutError

sys.path.append('C:\\Users\\ajani\\Downloads\\webscrapping 101\\MyAutomationProject')
from Logs.Alogger import setupLogging

sys.path.append('C:\\Users\\ajani\\Downloads\\webscrapping 101\\MyAutomationProject\\STONKMarket')
from STONKMarket.dataFix import StockDataAnalyzer

os.environ['DEBUG'] = 'pw:api,pw:browser*'
logger = setupLogging('stonkError.log', 'stonkWarning.log', 'stonkInfo.log', 'stonkCritical.log')

@pytest.fixture(scope="session")
def context():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            slow_mo=200,
        )

        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 OPR/113.0.0.0',
            # record_video_dir='MyAutomationProject/STONKMarket/video',
            # record_video_size={'width': 1920, 'height': 1080}
        )

        def handRoute(route: Route, request: Request):
            headers = request.headers.copy()
            headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            headers["Pragma"] = "no-cache"
            headers["Expires"] = "0"
            route.continue_(headers=headers)
        
        context.route("**/*", handRoute)

        yield context
        context.close()
        browser.close()

@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    yield page
    page.close()

def test_scrape(page: Page):
    try:
        dir = 'MyAutomationProject/STONKMarket/stokedata'
        graphdir = 'MyAutomationProject/STONKMarket/graph'
        os.makedirs(dir, exist_ok=True)
        logger.info("Path created" if not os.path.exists(dir) else "Path already exists")
        route = os.path.join(dir, 'NVDA.csv')
        
        logger.info("Navigating to website")
        try:
            baseUrl = 'https://finance.yahoo.com/chart/NVDA'
            page.goto(baseUrl, wait_until='domcontentloaded', timeout=60000)
            logger.info(f"Navigated to {page.url}")
        except TimeoutError as e:
            logger.error(f"Timeout during page.goto: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during page.goto: {e}")
            raise
            
        # DOM Manipulation to remove unwanted elements
        page.evaluate(""" 
            const selectors = [
                'div.stx-subholder',
                'aside',
                'header[data-test="navbar"]',
                'footer[data-test="Footer-Region"]'
            ];
            for (const selector of selectors) {
                const element = document.querySelector(selector);
                if (element) {
                    element.style.display = 'none';
                }
            }
        """)

        page.wait_for_selector('fin-streamer[data-test="qsp-price"]', timeout=60000)
        page.wait_for_selector('fin-streamer[data-test="qsp-price-change"]', timeout=60000)
        page.wait_for_selector('fin-streamer[data-field="regularMarketChangePercent"]', timeout=60000)

        startTime = time.time()
        StockData = []
        
        marketClose = datetime.time(15,0,0)
        while datetime.datetime.now().time() <= marketClose:
            try: 
                logger.info(f"Starting loop, time elapsed: {time.time() - startTime:.2f}")
                stockPrices = page.locator('fin-streamer[data-test="qsp-price"] span').first 
                priceChange = page.locator('fin-streamer[data-test="qsp-price-change"] span').first
                percentageChange = page.locator('fin-streamer[data-field="regularMarketChangePercent"] span').first
                        
                stockPricesTxt = stockPrices.inner_text()
                priceChangeTxt = priceChange.inner_text()
                percentageChangeTxt = percentageChange.inner_text()
                
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
                
                time.sleep(1)
            except Exception as e:
                logger.exception(f"Error in scraping loop: {str(e)}")

        if StockData:
            pd.DataFrame(StockData).to_csv(route, mode='a', header=not os.path.exists(route), index=False)
            StockDataAnalyzer(csvRoute=route, graphRoute=graphdir).run()
            logger.info(f"Data saved to {route}")
        else:
            logger.warning("No data was collected during the scraping session")

        # Assertions to verify the scraping was successful
        assert len(StockData) > 0, "No data was scraped"
        assert all(key in StockData[0] for key in ['Stock Price', 'Price Change', 'Percentage Change', 'Timestamp']), "Missing expected data fields"
        
    except Exception as e:
        logger.exception(f"Error in test_scrape: {str(e)}")
        raise

if __name__ == "__main__":
    test_scrape()
