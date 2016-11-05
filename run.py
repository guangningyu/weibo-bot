#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
from weibo import Client
import cPickle as pickle
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
        self.state_file = '/home/pi/Documents/MyRepos/weibo-bot/state.pkl'
        self.init_state()
        self.app = {
            'repost_news': '小易读新闻',
            'auto_reply': '小易陪聊'
        }

    def create_api_client(self):
        return Client(
            self.app_key,
            self.app_secret,
            self.redirect_uri,
            username = self.username,
            password = self.password
        )

    def init_state(self):
        if not os.path.exists(self.state_file):
            # set initial state
            self.state = {
                'replied_comments': []
            }
            self.dump_state()
        else:
            self.state = self.load_state()

    def dump_state(self):
        f = file(self.state_file, 'wb')
        pickle.dump(self.state, f, True)

    def load_state(self):
        f = file(self.state_file, 'rb')
        return pickle.load(f)

    def read_weibo(self, id):
        '''
        根据微博ID获取单条微博内容
        '''
        return self.client.get('statuses/show', id=id)

    def read_comments_with_mentions(self):
        '''
        获取提到当前用户的评论
        '''
        return self.client.get('comments/mentions')

    def post_weibo(self, text):
        '''
        使用当前账号发送微博
        '''
        self.client.post('statuses/update', status=text)

    def reply_comment(self, cid, id, reply):
        '''
        回复一条评论
        '''
        self.client.post('comments/reply', cid=cid, id=id, comment=reply, comment_ori=1)

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
        返回含有关键字的最新的公开微博
        '''
        print '>> 筛选最新的公开微博...'
        weibos = self.client.get('statuses/public_timeline', count=200)
        for weibo in weibos['statuses']:
            for keyword in self.keywords:
                if keyword.decode('utf-8') in weibo['text']:
                    self.repost_weibo(weibo['id'], '#%s##%s#' % (self.app['repost_news'], keyword))
                    return

    def get_reply(self, comment):
        answer_pool = [
            '恩，然后呢？',
            '哦，好吧...',
            '人生得意须尽欢啊呦喂！',
            '剽悍的人生不需要解释',
            '大家都是出来混的，都不容易！',
            '人生总有几次踩到大便的时候',
            '令人愉悦的忧伤...',
            'Don\'t panic!',
            '我走来走去，为中国的命运苦苦思索...'
        ]
        reply = random.choice(answer_pool)
        reply += ' #%s#' % self.app['auto_reply']
        return reply

    def reply_comments_with_mentions(self):
        '''
        回复最新的@我的评论
        '''
        print '>> 回复最新的@我的评论...'
        comments = bot.read_comments_with_mentions()['comments']
        for comment in comments:
            cid = comment['id']
            id = comment['status']['id']
            reply = self.get_reply(comment['text'])
            # 如果没有回复过，则进行回复并更新已回复列表
            if cid not in self.state['replied_comments']:
                bot.reply_comment(cid, id, reply)
                self.state['replied_comments'].append(cid)
                self.dump_state()

if __name__ == '__main__':
    bot = WeiboBot(config)
    print bot.state

    # 转发最新关注的人的最新的一条微博
    #res = bot.get_friends_timeline_weibo()
    #latest_weibo = res['statuses'][0]
    #bot.repost_weibo(latest_weibo)

    # 转发最新的含有预设关键词的公开微博
    bot.repost_by_keyword_from_public_timeline()

    # 回复@我的评论
    bot.reply_comments_with_mentions()
