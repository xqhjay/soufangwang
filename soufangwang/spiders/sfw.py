# -*- coding: utf-8 -*-
import scrapy
import re
from urllib.parse import urlsplit
from soufangwang.items import NewHouseItem, ESFItem


class SfwSpider(scrapy.Spider):
    name = 'sfw'
    allowed_domains = ['fang.com']
    start_urls = ['http://www.fang.com/SoufunFamily.htm']

    def parse(self, response):
        trs = response.xpath("//table[@id='senfe']//tr")
        # 所属省份
        province = None
        for tr in trs:
            tds = tr.xpath("./td[not(@class)]")
            province_td = tds[0]
            province_text = re.sub(r'\s', '', province_td.xpath(".//text()").get())
            if province_text:
                province = province_text

            if province == '其它':  # 过滤掉海外城市
                continue

            city_links = tds[1].xpath("./a")
            for city_link in city_links:
                city = city_link.xpath("./text()").get()
                city_url = city_link.xpath("./@href").get()
                city_urlresult = urlsplit(city_url)
                schem = city_urlresult.scheme  # 网络协议
                netloc = city_urlresult.netloc  # 服务器位置
                if 'bj' in netloc:
                    # 北京特例
                    newhouse_url = 'http://newhouse.fang.com/house/s'
                    esf_url = 'http://esf.fang.com'
                else:
                    # 构建新房url
                    newhouse_url = f"{schem}://newhouse.{netloc}/house/s"
                    # 构建二手房url
                    esf_url = f"{schem}://esf.{netloc}"
                yield scrapy.Request(newhouse_url, callback=self.pare_newhouse, meta={'city': (province, city)})
                yield scrapy.Request(esf_url, callback=self.pare_esf, meta={'city': (province, city)})

    def pare_newhouse(self, response):
        province, city = response.meta['city']
        lis = response.xpath("//div[@id='newhouse_loupai_list']//li")
        for li in lis:
            li_text = li.xpath(".//div[@class='nlcd_name']/a[@target='_blank']/text()").get()
            if li_text:
                name = re.sub(r'\s', '', li_text)
            else:
                continue
            house_type_list = li.xpath(".//div[contains(@class,'house_type')]/a/text()").getall()
            # 过滤掉不含居室信息的项
            rooms = list(filter(lambda x: '居' in x, house_type_list))
            area = re.sub(r'\s|－|/', '', ''.join(li.xpath(".//div[contains(@class,'house_type')]/text()").getall()))
            address = li.xpath(".//div[@class='address']/a/@title").get()
            district_text = ''.join(li.xpath(".//div[@class='address']/a//text()").getall())
            district = re.search(r'.*\[(.+)\].*', district_text).group(1)
            sale = li.xpath(".//div[contains(@class,'fangyuan')]/span/text()").get()
            tags = re.sub(r'\s', '', ','.join(li.xpath(".//div[contains(@class,'fangyuan')]/a/text()").getall()))
            price = re.sub(r'\s|广告', '', ''.join(li.xpath(".//div[@class='nhouse_price']//text()").getall()))
            origin_url = li.xpath(".//div[@class='nlcd_name']/a/@href").get()
            item = NewHouseItem(province=province, city=city, name=name, price=price, rooms=rooms, area=area,
                                address=address, district=district, sale=sale, tags=tags, origin_url=origin_url)
            yield item
        next_url = response.xpath("//div[@class='page']//a[@class='next']/@href").get()
        if next_url:
            yield scrapy.Request(next_url, callback=self.pare_newhouse, meta={'city': (province, city)})

    def pare_esf(self, response):
        province, city = response.meta['city']
        print(province, city)
        dls = response.xpath("//div[contains(@class,'shop_list')]/dl")
        for dl in dls:
            item = ESFItem(province=province, city=city)
            name = dl.xpath(".//p[@class='add_shop']/a/@title").get()
            # 过滤广告
            if not name:
                continue
            infos = list(map(lambda x: re.sub(r'\s', '', x), dl.xpath(".//p[@class='tel_shop']/text()").getall()))
            infos = list(filter(lambda x: x, infos))
            for info in infos:
                if '厅' in info:
                    rooms = info
                elif '层' in info:
                    floor = info
                elif '向' in info:
                    toward = info
                elif info.endswith('建'):
                    year = info.replace('建', '')
                else:
                    area = info
            address = dl.xpath(".//p[@class='add_shop']/span/text()").get()
            price = ''.join(dl.xpath(".//span[@class='red']//text()").getall())
            unit = dl.xpath(".//dd[@class='price_right']/span[2]/text()").get()
            origin_url = response.urljoin(dl.xpath(".//h4/a/@href").get())
            item = ESFItem(province=province, city=city, name=name, rooms=rooms, floor=floor,
                           toward=toward, year=year, address=address, area=area, price=price,
                           unit=unit, origin_url=origin_url)
            yield item
        next_url = response.urljoin(response.xpath("//div[@class='page_al']/p[1]/a/@href").get())
        if next_url:
            yield scrapy.Request(next_url, callback=self.pare_esf, meta={'city': (province, city)})
