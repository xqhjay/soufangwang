# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewHouseItem(scrapy.Item):
    collection = 'newhouse'
    province = scrapy.Field()
    city = scrapy.Field()
    # 小区名
    name = scrapy.Field()
    price = scrapy.Field()
    # 几居
    rooms = scrapy.Field()
    area = scrapy.Field()
    address = scrapy.Field()
    # 行政区
    district = scrapy.Field()
    # 是否在售
    sale = scrapy.Field()
    # 标签
    tags = scrapy.Field()
    # 详情页url
    origin_url = scrapy.Field()


class ESFItem(scrapy.Item):
    collection = 'esf'
    province = scrapy.Field()
    city = scrapy.Field()
    # 小区名
    name = scrapy.Field()
    # 几室几厅
    rooms = scrapy.Field()
    # 层
    floor = scrapy.Field()
    # 朝向
    toward = scrapy.Field()
    # 建筑年代
    year = scrapy.Field()
    address = scrapy.Field()
    area = scrapy.Field()
    # 总价
    price = scrapy.Field()
    # 单价
    unit = scrapy.Field()
    # 详情页url
    origin_url = scrapy.Field()
