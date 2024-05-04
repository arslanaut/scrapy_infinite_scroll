import scrapy
from scrapy_playwright.page import PageMethod
from scrapy.selector import Selector

class QuotesSpider(scrapy.Spider):
    name = 'quotes'

    def start_requests(self):
        yield scrapy.Request(
            url="http://quotes.toscrape.com/scroll",
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "div.quote")
                ],
                "playwright_include_page": True
            },
            errback=self.close_page
        )

    async def parse(self, response):
        try:
            page = response.meta['playwright_page']

            # READ CONTENT OF 10 SCROLLS
            for i in range(2, 11):  # 2 to 10
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                quotes_count = 10*i
                await page.wait_for_selector(f'.quote:nth-child({quotes_count})')

            # now the page content is update for each page
            quotes = Selector(text=await page.content())
            await page.close()

            for quote in quotes.css('.quote'):
                yield {
                    'author': quote.css('.author ::text').get(),
                    'quote': quote.css('.text ::text').get()
                }
        except Exception as e:
            print(e)

    async def close_page(self, on_fail):
        page = on_fail.request.meta["playwright_page"]
        await page.close()