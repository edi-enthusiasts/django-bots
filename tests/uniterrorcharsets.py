# -*- coding: utf-8 -*-

import bots.botslib as botslib
import pytest
from collections import OrderedDict

'''
no plugin needed.
run using pytest.
should give no errors.
utf-16 etc are reported.
'''


@pytest.fixture(params=('False', 'True'))
def botsglobal(request, botsinit):
    import bots.botsglobal as botsglobal_module

    botsglobal_module.logger = botsinit.initenginelogging('engine')
    botsglobal_module.ini.set('settings', 'debug', request.param)
    yield botsglobal_module

    # GC the handlers so their file handles close, and the log file can properly rotate.
    botsglobal_module.logger.handlers.clear()


def check_encoding(expect, msg, *args, **kwargs):
    try:
        raise botslib.BotsError(msg, *args, **kwargs)
    except Exception as err:
        if not isinstance(err, str):
            err = str(err)

        if expect:
            if str(expect) != err.strip():
                raise Exception('Expected("%s") | Received("%s")' % (expect, err)) from None

        txt = botslib.txtexc()
        if not isinstance(txt, str):
            raise Exception('Error txt "%s"' % txt) from None

# .decode(): bytes->unicode
# .encode(): unicode -> bytes


def test_except_safestr(botsglobal):
    # normal, valid handling
    check_encoding('', '', {'test1': 'test1', 'test2': 'test2', 'test3': 'test3'})
    check_encoding('0test', '0test', {'test1': 'test1', 'test2': 'test2', 'test3': 'test3'})
    check_encoding('0test test1 test2', '0test %(test1)s %(test2)s %(test4)s', {'test1': 'test1', 'test2': 'test2', 'test3': 'test3'})
    check_encoding('1test test1 test2 test3', '1test %(test1)s %(test2)s %(test3)s', {'test1': 'test1', 'test2': 'test2', 'test3': 'test3'})
    check_encoding('2test test1 test2 test3', '2test %(test1)s %(test2)s %(test3)s', {'test1': 'test1', 'test2': 'test2', 'test3': 'test3'})
    # different inputs in BotsError
    check_encoding('3test', '3test')
    check_encoding('4test test1 test2', '4test %(test1)s %(test2)s %(test3)s', {'test1': 'test1', 'test2': 'test2'})
    check_encoding('5test test1 test2', '5test %(test1)s %(test2)s %(test3)s', test1='test1', test2='test2')
    check_encoding('6test', '6test %(test1)s %(test2)s %(test3)s', 'test1')
    check_encoding("7test ['test1', 'test2']", '7test %(test1)s %(test2)s %(test3)s', test1=['test1', 'test2'])
    check_encoding("8test OrderedDict([('test1', 'test1'), ('test2', 'test2')])", '8test %(test1)s %(test2)s %(test3)s', test1=OrderedDict((('test1', 'test1'), ('test2', 'test2'))))

    # different charsets in BotsError
    check_encoding('12test test1 test2 test3', '12test %(test1)s %(test2)s %(test3)s', {'test1': 'test1', 'test2': 'test2', 'test3': 'test3'})
    check_encoding(
        '13test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test2\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test3\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202',
        '13test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 %(test1)s %(test2)s %(test3)s',
        {
            'test1': 'test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202',
            'test2': 'test2\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202',
            'test3': 'test3\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202'
        }
    )
    check_encoding(
        '14test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202',
        '14test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 %(test1)s'.encode('utf_8'),
        {'test1': 'test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202'.encode('utf_8')}
    )
    check_encoding(
        '15test test1',
        '15test %(test1)s',
        {'test1': 'test1'.encode('utf_16')}
    )
    check_encoding(
        '16test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202',
        '16test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 %(test1)s',
        {'test1': 'test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202'.encode('utf_16')}
    )
    check_encoding(
        '17test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202',
        '17test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 %(test1)s',
        {'test1': 'test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202'.encode('utf_32')}
    )
    check_encoding(
        '18test\u00E9\u00EB\u00FA\u00FB\u00FC test1\u00E9\u00EB\u00FA\u00FB\u00FC',
        '18test\u00E9\u00EB\u00FA\u00FB\u00FC %(test1)s',
        {'test1': 'test1\u00E9\u00EB\u00FA\u00FB\u00FC'.encode('latin_1')}
    )

    # make utf-8 string, many chars
    s = ''.join(map(chr, range(0, 65536)))
    check_encoding('', s)
    s2 = s.encode('utf-8', 'surrogatepass')
    check_encoding('', s2)

    # make iso-8859-1 string, many chars
    s = ''.join(map(chr, range(0, 256)))
    check_encoding('', s)
    s2 = s.encode('latin_1')
    check_encoding('', s2)
