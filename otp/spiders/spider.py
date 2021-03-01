import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import OtpItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class OtpSpider(scrapy.Spider):
	name = 'otp'
	start_urls = ['https://www.otpbanka.hr/o-nama/priopcenja']

	def parse(self, response):
		post_links = response.xpath('//span[@class="field-content"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@title="Idi na sljedeću stranicu"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):

		date = response.xpath('//div[@class="submitted"]/text()').get()
		date = re.findall(r'\d+\.\d+\.\d+',date)
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="field-item even"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=OtpItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
