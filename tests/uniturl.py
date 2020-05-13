# -*- coding: utf-8 -*-

import pytest
from bots.botslib import Uri

''' no plugin '''


@pytest.mark.unit_test
class TestUriTranslate:

    def test_combinations(self):
        assert str(Uri(
            scheme='scheme',
            username='username',
            password='password',
            hostname='hostname',
            port=80,
            path='path1/path2',
            filename='filename',
            query={'query': 'argument'},
            fragment='fragment'
        )) == 'scheme://username:password@hostname:80/path1/path2/filename', 'basis'

        assert str(Uri(
            scheme='scheme',
            username='username',
            password='password',
            hostname='hostname',
            port=80,
            path='path1/path2',
            filename='filename'
        )) == 'scheme://username:password@hostname:80/path1/path2/filename', 'basis'

        assert str(Uri(scheme='scheme', path='/path1/path2', filename='filename')) == 'scheme:/path1/path2/filename'
        assert str(Uri(scheme='scheme', path='path1/path2', filename='filename')) == 'scheme:path1/path2/filename'
        assert str(Uri(path='path1/path2', filename='filename')) == 'path1/path2/filename'
        assert str(Uri(path='path1/path2')) == 'path1/path2/'
        assert str(Uri(filename='filename')) == 'filename'
        assert str(Uri(scheme='scheme', path='path1/path2')) == 'scheme:path1/path2/'
        assert str(Uri(scheme='scheme', filename='filename')) == 'scheme:filename'

        assert str(Uri(
            scheme='scheme',
            username='username',
            password='password',
            hostname='hostname',
            port=80,
            path='path1/path2')
        ) == 'scheme://username:password@hostname:80/path1/path2/', 'basis'

        assert str(Uri(
            scheme='scheme',
            username='username',
            password='password',
            hostname='hostname',
            port=80,
            filename='filename'
        )) == 'scheme://username:password@hostname:80/filename', 'basis'

        assert str(Uri(
            scheme='scheme',
            username='username',
            password='password',
            hostname='hostname',
            port=80
        )) == 'scheme://username:password@hostname:80', 'basis'

        assert str(Uri(
            scheme='scheme',
            username='username',
            password='password',
            hostname='hostname'
        )) == 'scheme://username:password@hostname', 'bas'

        assert str(Uri(
            scheme='scheme',
            username='username',
            hostname='hostname'
        )) == 'scheme://username@hostname', 'bas'

        assert str(Uri(scheme='scheme', hostname='hostname')) == 'scheme://hostname', 'bas'

        assert str(Uri(
            scheme='scheme',
            username='username',
            hostname='hostname',
            port=80,
            path='path1/path2',
            filename='filename'
        )) == 'scheme://username@hostname:80/path1/path2/filename', 'no password'

        assert str(Uri(
            scheme='scheme',
            password='password',
            hostname='hostname',
            port=80,
            path='path1/path2',
            filename='filename'
        )) == 'scheme://hostname:80/path1/path2/filename', 'no username'

        assert str(Uri(
            scheme='scheme',
            username='username',
            password='password',
            path='path1/path2',
            filename='filename'
        )) == 'scheme:path1/path2/filename', 'no hostname'

        assert str(Uri(
            username='username',
            password='password',
            hostname='hostname',
            port=80,
            path='path1/path2',
            filename='filename'
        )) == '//username:password@hostname:80/path1/path2/filename', 'no scheme'

        assert str(Uri(
            username='username',
            password='password',
            port=80,
            path='path1/path2',
            filename='filename'
        )) == 'path1/path2/filename', 'no scheme no hostname'

    def test_empty(self):
        # tests for empty values
        assert str(Uri(
            scheme=None,
            username='username',
            password='password',
            hostname='hostname',
            port=80,
            path='path1/path2',
            filename='filename'
        )) == '//username:password@hostname:80/path1/path2/filename', 'basis'

        assert str(Uri(
            scheme='',
            username='username',
            password='password',
            hostname='hostname',
            port=80,
            path='path1/path2',
            filename='filename'
        )) == '//username:password@hostname:80/path1/path2/filename', 'basis'

        assert str(Uri(
            scheme='scheme',
            username=None,
            password=None,
            hostname='hostname',
            port=80,
            path='path1/path2',
            filename='filename'
        )) == 'scheme://hostname:80/path1/path2/filename', 'basis'

        assert str(Uri(
            scheme='scheme',
            username='',
            password='',
            hostname='hostname',
            port=80,
            path='path1/path2',
            filename='filename'
        )) == 'scheme://hostname:80/path1/path2/filename', 'basis'

        assert str(Uri(
            scheme='scheme',
            username='username',
            password='password',
            hostname='hostname',
            port=80,
            path='path1/path2',
            filename='filename'
        )) == 'scheme://username:password@hostname:80/path1/path2/filename', 'basis'

    def test_calls(self):
        assert Uri(
            scheme='scheme',
            path='/path1/path2',
            filename='filename'
        ).uri(filename='filename2') == 'scheme:/path1/path2/filename2'
