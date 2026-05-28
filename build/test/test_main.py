import unittest
import makesite
import os
import shutil
import json

from test import path


class MainTest(unittest.TestCase):
    def setUp(self):
        path.move('_site', '_site.backup')
        path.move('params.json', 'params.json.backup')

    def tearDown(self):
        path.move('_site.backup', '_site')
        path.move('params.json.backup', 'params')

    def test_site_missing(self):
        makesite.main()
        self.assertTrue(os.path.isdir('_site'))

    def test_site_exists(self):
        os.mkdir('_site')
        with open('_site/foo.txt', 'w') as f:
            f.write('foo')
        self.assertTrue(os.path.isfile('_site/foo.txt'))
        makesite.main()
        self.assertFalse(os.path.isfile('_site/foo.txt'))

    def test_generates_blog_index(self):
        makesite.main()
        self.assertTrue(os.path.isfile('_site/blog/index.html'))
        self.assertTrue(os.path.isfile('_site/blog/rss.xml'))
        # self.assertTrue(os.path.isfile('_site/news/index.html'))
        # self.assertTrue(os.path.isfile('_site/news/rss.xml'))
        shutil.rmtree('_site')

    def test_generates_blog_posts(self):
        makesite.main()
        self.assertTrue(os.path.isfile('_site/blog/first-blog/index.html'))
        self.assertTrue(os.path.isfile('_site/blog/no-minecraft-for-guest-network/index.html'))
        shutil.rmtree('_site')

    def test_json_params(self):
        params = {
            'base_path': '/base',
            'subtitle': 'Foo',
            'author': 'Bar',
            'site_url': 'http://localhost/base'
        }
        with open('params.json', 'w') as f:
            json.dump(params, f)
        makesite.main()
        self.assertTrue(os.path.isdir('_site'))
        shutil.rmtree('_site')
