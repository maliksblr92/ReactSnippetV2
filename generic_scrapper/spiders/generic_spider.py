from ..items import GenericScrapperItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import scrapy
import re
#-------------------------Data Cleaning-------------------------

def CleanTag(textToClean):
	finaltext = []
	for text in textToClean:
		cleanText = re.sub("(\n|\t)*","",text)
		cleanText = cleanText.strip()
		if(cleanText != ""):
			finaltext.append(cleanText)
	return finaltext

class GenericSpider(scrapy.Spider):
    name="generic"
    start_urls=["https://docs.scrapy.org/en/latest/topics/selectors.html"]
    rule = (Rule(LinkExtractor(canonicalize=True, unique=True), callback="parse", follow=True))
    def __init__(self, url=None, domain=None, links=True, headings=True, paragraphs=True, pictures=False,videos=False,  *args, **kwargs):
        super(GenericSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['%s' % url]
        self.allowed_domains = [domain]
        self.links=links
        self.headings=headings
        self.paragraphs=paragraphs
        self.pictures=pictures
        self.videos=videos
        print(domain, url)
    
    def parse(self, response):
        allLinks = []
        allLinks.append(response.request.url)
        links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)
        print(links[1])
        items = {}
        for link in links:
            is_allowed = False
            for allowed_domain in self.allowed_domains:
                if allowed_domain in link.url:
                    allLinks.append(link.url)
        for link in allLinks:
            yield scrapy.Request(link,callback=self.parse_items)
    def parse_items(self,response):
        item = GenericScrapperItem()
        title=response.xpath('//title/text()').extract()
        item['title'] = title

        if self.paragraphs:
            p_tags = response.xpath('//p/text()').extract()
            content = CleanTag(p_tags)
            item['content'] = content

        if self.headings:
            h1= response.xpath('//h1/text()').extract()
            h1=CleanTag(h1)
            h2= response.xpath('//h2/text()').extract()
            h2=CleanTag(h2)
            h3= response.xpath('//h3/text()').extract()
            h3=CleanTag(h3)
            h4= response.xpath('//h4/text()').extract()
            h4=CleanTag(h4)
            h5= response.xpath('//h5/text()').extract()
            h5=CleanTag(h5)
            h6= response.xpath('//h6/text()').extract()
            h6=CleanTag(h6)
            item['large_headings'] = h1+h2+h3
            item['small_headings'] = h3+h4+h5
        
        if self.pictures:
            image_url=response.css('img').xpath('@src').extract()
            item['image_urls']=image_url

        
        currentPage = response.request.url
        item['page'] = currentPage
        
        
      
    
        yield item
