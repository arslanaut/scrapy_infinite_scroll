import scrapy
from scrapy_playwright.page import PageMethod


class QuotesSpider(scrapy.Spider):
    name = "quotes_pagination"

    allowed_domains = ["quotes.toscrape.com"]
    current_page = 1
    start_urls = [
        f"https://quotes.toscrape.com/page/{current_page}"]

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            meta={
                "playwright": True,
                "playwright_page_methods": [

                    PageMethod("wait_for_load_state", "domcontentloaded"),
                    PageMethod("wait_for_load_state", "networkidle"),
                ],

            },
            callback=self.parse,
        )

    def parse(self, response):
        products = response.css(".quote")
        try:
            for product in products:
                yield {
                    "title": product.css('span.text::text').get(),
                    "author": product.css('.author::text').get(),
                    "tag_link": product.css('a.tag::attr(href)').get(),
                    "tags": product.css('a.tag::text').getall(),
                }
        except Exception as e:
            print("===============Exception:", e)

        # NEXT PAGE LOGIC
        current_page = int(response.url.split('/')[-2])
        self.current_page = current_page + 1
        if self.current_page < 2:  # Adjust this condition based on the number of pages you want to scrape
            print(
                f'\n======SCRAPPING PAGE: {self.current_page}\n')
            next_page_url = f"https://quotes.toscrape.com/page/{self.current_page}"
            yield scrapy.Request(
                url=next_page_url,
                meta={"playwright": True},
                callback=self.parse
            )
        else:
            print('\n======NO PAGE LEFT\n')
