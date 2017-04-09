# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import json
from zhihuuser.items import ZhihuUserItem#导入我们刚刚定义的items，这里从文件最外层开始带入



class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://www.zhihu.com/']
    start_user ='wang-tuan-jie-55'#开始放进去的第一个用户的ID



    include_follow='data[*].answer_count, articles_count, gender, follower_count, is_followed, is_following, badge[?(type = best_answerer)].topics'
    #上面这个是查询粉丝或者关注列表里面的用户需要附带的参数
    include_userinfo='locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,avatar_hue,answer_count,articles_count,pins_count,question_count,commercial_question_count,favorite_count,favorited_count,logs_count,marked_answers_count,marked_answers_text,message_thread_token,account_status,is_active,is_force_renamed,is_bind_sina,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics'
    #上面这个是查询个人信息需要附带的一个参数


    followers_url = 'https://www.zhihu.com/api/v4/members/{user_name}/followers?include={include_follow}&offset={offset}&limit={limit}'
    #获取粉丝列表的url,里面的参数分别是用户的ID，查询参数，这个在浏览器复制就可以了，offset表示第几页的粉丝或者关注者，limit表示每页的数量，这里网页上默认是20
    followees_url = 'https://www.zhihu.com/api/v4/members/{user_name}/followees?include={include_follow}&offset={offset}&limit={limit}'
    # 获取关注列表的URL，根上面的就差了一个字母
    userinfo_url= 'https://www.zhihu.com/api/v4/members/{user_name}?include={include_userinfo}'
    #上面这个是提取用户信息信息的url
    def start_requests(self):
        yield Request(url=self.userinfo_url.format(user_name=self.start_user,include_userinfo=self.include_userinfo),callback=self.get_user_info)
        #上面是访问第一个用户，获取详细信息
        yield Request(url=self.followers_url.format(user_name=self.start_user,include_follow=self.include_follow,offset=0,limit=20),callback=self.get_followers_parse)
        #上面是访问第一个用户的粉丝列表，下面是访问关注列表
        yield Request(url=self.followees_url.format(user_name=self.start_user,include_follow=self.include_follow,offset=0,limit=20),callback=self.get_followees_parse)

    def get_user_info(self,response):#获取用户信息信息
        data = json.loads(response.text)
        #print(data)
        item = ZhihuUserItem()
        for Field in item.fields:#可以获取在item里面定义的key值，就是那些locations，employments等
            #print(Field)
            if Field in data.keys():
                item[Field]=data.get(Field)#获取字典里面的值
        yield item
        yield Request(url=self.followers_url.format(user_name=data.get('url_token'),include_follow=self.include_follow,offset=0,limit=20),callback=self.get_followers_parse)
        yield Request(url=self.followees_url.format(user_name=data.get('url_token'), include_follow=self.include_follow, offset=0,limit=20), callback=self.get_followees_parse)

    def get_followers_parse(self, response):#获取粉丝列表
        try:#这里添加的异常是防止有些用户没有粉丝
            followers_data = json.loads(response.text)

            try:
                if  followers_data.get('data'):  # data里面是一个由字典组成的列表，每个字典是粉丝的相关信息
                    for one_user in followers_data.get('data'):
                        user_name = one_user['url_token']#提取url_token然后访问他的详细信息
                        yield Request(url=self.userinfo_url.format(user_name=user_name,include_userinfo=self.include_userinfo),callback=self.get_user_info)
                        #将所有粉丝或者关注者的url_token提取出来，放进一开始我们构造的用户详细信息的网址里面，提取他们的信息

                if  'paging' in followers_data.keys() and followers_data.get('paging').get('is_end') ==False:
                    yield Request(url=followers_data.get('paging').get('next'),callback=self.get_followers_parse)
            except Exception as e:
                print(e,'该用户没有url_token')
        except Exception as e:
            print(e,' 该用户没有粉丝')

    def get_followees_parse(self,response):#获取关注者的函数
        try:#这里添加的异常是防止有些用户没有关注者
            followees_data = json.loads(response.text)
            try:
                if followees_data.get('data'):
                    for one_user in followees_data.get('data'):
                        user_name = one_user['url_token']#提取url_token然后访问他的详细信息
                        yield Request(url=self.userinfo_url.format(user_name=user_name,include_userinfo=self.include_userinfo),callback=self.get_user_info)
                        #将所有粉丝或者关注者的url_token提取出来，放进一开始我们构造的用户详细信息的网址里面，提取他们的信息

                if  'paging' in followees_data.keys() and followees_data.get('paging').get('is_end') ==False:#判断是否有下一页
                    yield Request(url=followees_data.get('paging').get('next'),callback=self.get_followees_parse)
            except Exception as e:
                print(e,'该用户没有url_token或者data')
        except Exception as e:
            print(e,' 该用户没有粉丝')
