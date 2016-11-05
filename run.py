#!/usr/bin/env python
# -*- coding: utf-8 -*-

from weibo import Client
import config

class WeiboBot():
    def __init__(self, config):
        self.app_key = config.app_key
        self.app_secret = config.app_secret
        self.redirect_uri = config.redirect_uri
        self.username = config.username
        self.password = config.password
        self.keywords = config.keywords.split(',')
        self.client = self.create_api_client()
        self.app = {
            'repost_news': '小易读新闻'
        }

    def create_api_client(self):
        return Client(
            self.app_key,
            self.app_secret,
            self.redirect_uri,
            username = self.username,
            password = self.password
        )

    def read_weibo(self, id):
        '''
        根据微博ID获取单条微博内容
        '''
        return self.client.get('statuses/show', id=id)

    def post_weibo(self, text):
        '''
        使用当前账号发送微博
        '''
        self.client.post('statuses/update', status=text)

    def repost_weibo(self, id, status):
        '''
        转发一条微博
        '''
        print '>>> reposted weibo...'
        self.client.post('statuses/repost', id=id, status=status+'[哈欠]')

    def get_followers(self, screen_name):
        '''
        返回当前账号的关注用户列表
        '''
        return self.client.get('friendships/friends/ids', screen_name=screen_name, count=500)

    def get_friends_timeline_weibo(self):
        '''
        获取当前登录用户及其所关注用户的最新微博的ID
        '''
        return self.client.get('statuses/friends_timeline/ids', feature=1)

    def repost_by_keyword_from_public_timeline(self):
        '''
        返回含有关键字的最新的公共微博
        '''
        weibos = self.client.get('statuses/public_timeline', count=200)
        for weibo in weibos['statuses']:
            for keyword in self.keywords:
                if keyword.decode('utf-8') in weibo['text']:
                    self.repost_weibo(weibo['id'], '#%s##%s#' % (self.app['repost_news'], keyword))
                    return

if __name__ == '__main__':
    bot = WeiboBot(config)

    # 转发最新关注的人的最新的一条微博
    #res = bot.get_friends_timeline_weibo()
    #latest_weibo = res['statuses'][0]
    #bot.repost_weibo(latest_weibo)

    bot.repost_by_keyword_from_public_timeline()
