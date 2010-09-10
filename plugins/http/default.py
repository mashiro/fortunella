#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fortunella.plugins.http import Handler
import re
import httplib
import socket
import ImageFile # require PIL

class Default(Handler):
    def init(self, config):
        self.priority = 0
        self.config = config or {}
        self.max_redirect = self.config.get('MaxRedirect', 10)
        self.user_agent = self.config.get('UserAgent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)')
        self.block_size = self.config.get('BlockSize', 4096)
        self.re_charset = re.compile(r'charset=([\w-]+)', re.IGNORECASE|re.DOTALL)
        self.re_metatitle = re.compile(r'<meta.*?name="title".*?content="(.*?)".*?>', re.IGNORECASE|re.DOTALL)
        self.re_title = re.compile(r'<title.*?>\s*(.*?)\s*</title>', re.IGNORECASE|re.DOTALL)
        self.re_linebreak = re.compile(r'\r|\n|\r\n', re.IGNORECASE|re.DOTALL)

    def process(self, url):
        return self.fetch_head(url)

    def fetch_head(self, url, limit=None):
        try:
            if limit is None:
                limit = self.max_redirect
            if limit <= 0:
                return "Redirect loop?: last:%s" % url

            scheme, host, path = self.urlparse(url)
            conn = httplib.HTTPConnection(host)
            conn.request('HEAD', path, headers=dict(UserAgent=self.user_agent))
            res = conn.getresponse()
            if 301 <= res.status and res.status <= 399:
                location = res.getheader('location')
                return self.fetch_head(location, limit-1)

            content_type = res.getheader('content-type') or ''
            content_length = int(res.getheader('content-length') or 0)
            if 'html' in content_type:
                return self.fetch_html(url, content_type)
            elif 'image' in content_type:
                return self.fetch_image(url, content_length)
            else:
                return '[%s] %dKB' % (content_type, content_length / 1024)
        except socket.gaierror, e:
            return e[1]
        except Exception, e:
            return e

    def fetch_html(self, url, content_type):
        scheme, host, path = self.urlparse(url)
        conn = httplib.HTTPConnection(host)
        conn.request('GET', path, headers=dict(UserAgent=self.user_agent, Range=self.block_size))
        res = conn.getresponse()
        data = res.read()

        charset = self.search(self.re_charset, data, 'utf-8')
        data = data.decode(charset, 'replace')
        title = self.search(self.re_metatitle, data, None)
        if title is None:
            title = self.search(self.re_title, data, 'no titles')
        title = self.re_linebreak.sub('', title)
        return '%s [%s]' % (title, content_type)

    def fetch_image(self, url, content_length):
        scheme, host, path = self.urlparse(url)
        conn = httplib.HTTPConnection(host)
        conn.request('GET', path, headers=dict(UserAgent=self.user_agent))
        res = conn.getresponse()

        parser = ImageFile.Parser()
        size = content_length / 1024
        while True:
            data = res.read(1024)
            if not data:
                break
            parser.feed(data)
            if parser.image:
                image = parser.image
                width, height = image.size
                return '%s Image, %dx%d %dKB' % (image.format, width, height, size)

        return 'Unknown Image, %dKB' % (size)

    @classmethod
    def search(cls, regexp, target, default='', index=1):
        match = regexp.search(target)
        if match:
            return match.group(index)
        return default

    @classmethod
    def urlparse(cls, url):
        tokens = url.split('/', 3)
        if len(tokens) > 3:
            tokens[3] = '/' + tokens[3]
        else:
            tokens.append('/')
        scheme = tokens[0][:-1]
        host = tokens[2]
        path = tokens[3]
        return (scheme, host, path)

