# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient



class ZhihuuserPipeline(object):
    def __init__(self):
        self.client = MongoClient()
        self.database = self.client['zhuhu_spider']
        self.db = self.database['zhuhu_user_infomation']

    def process_item(self, item, spider):#这里以每个用户url_token为ID，有则更新，没有则插入
        self.db.update({'url_token':item['url_token']},dict(item),True)
        return item

    def close_spider(self,spider):
        self.client.close()
