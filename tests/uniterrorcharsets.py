#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bots.botslib as botslib
import bots.botsglobal as botsglobal
import bots.botsinit as botsinit

'''
no plugin needed.
run in commandline.
should give no errors.
utf-16 etc are reported.
'''


def testraise(expect, msg, *args, **kwargs):
    try:
        raise botslib.BotsError(msg, *args, **kwargs)
    except Exception:
        if not isinstance(msg, str):
            msg = str(msg)
            print('not a string', type(msg), expect)
            print('Error xxx\n', msg)
        if expect:
            if str(expect) != msg.strip():
                print(expect, '(expected)')
                print(msg, '(received)')
        txt = botslib.txtexc()
        if not isinstance(txt, str):
            print('Error txt\n', txt)

# .decode(): bytes->unicode
# .encode(): unicode -> bytes


def testrun():
    print('\n')
    # normal, valid handling
    testraise('', '', {'test1': 'test1', 'test2': 'test2', 'test3': 'test3'})
    testraise('0test', '0test', {'test1': 'test1', 'test2': 'test2', 'test3': 'test3'})
    testraise('0test test1 test2', '0test %(test1)s %(test2)s %(test4)s', {'test1': 'test1', 'test2': 'test2', 'test3': 'test3'})
    testraise('1test test1 test2 test3', '1test %(test1)s %(test2)s %(test3)s', {'test1': 'test1', 'test2': 'test2', 'test3': 'test3'})
    testraise('2test test1 test2 test3', '2test %(test1)s %(test2)s %(test3)s', {'test1': 'test1', 'test2': 'test2', 'test3': 'test3'})
    # different inputs in BotsError
    testraise('3test', '3test')
    testraise('4test test1 test2', '4test %(test1)s %(test2)s %(test3)s', {'test1': 'test1', 'test2': 'test2'})
    testraise('5test test1 test2', '5test %(test1)s %(test2)s %(test3)s', test1='test1', test2='test2')
    testraise('6test', '6test %(test1)s %(test2)s %(test3)s', 'test1')
    testraise("7test ['test1', 'test2']", '7test %(test1)s %(test2)s %(test3)s', test1=['test1', 'test2'])
    testraise("8test {'test1': 'test1', 'test2': 'test2'}", '8test %(test1)s %(test2)s %(test3)s', test1={'test1': 'test1', 'test2': 'test2'})
    testraise(
        "9test [<module 'bots.botslib' from '/home/hje/Bots/botsdev/bots/botslib.pyc'>, <module 'bots.botslib' from '/home/hje/Bots/botsdev/bots/botslib.pyc'>]",
        '9test %(test1)s %(test2)s %(test3)s',
        test1=[botslib, botslib]
    )

    # different charsets in BotsError
    testraise('12test test1 test2 test3', '12test %(test1)s %(test2)s %(test3)s', {'test1': 'test1', 'test2': 'test2', 'test3': 'test3'})
    testraise(
        '13test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test2\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test3\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202',
        '13test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 %(test1)s %(test2)s %(test3)s',
        {
            'test1': 'test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202',
            'test2': 'test2\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202',
            'test3': 'test3\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202'
        }
    )
    testraise(
        '14test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202',
        '14test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 %(test1)s'.encode('utf_8'),
        {'test1': 'test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202'.encode('utf_8')}
    )
    testraise(
        '15test test1',
        '15test %(test1)s',
        {'test1': 'test1'.encode('utf_16')}
    )
    testraise(
        '16test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202',
        '16test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 %(test1)s',
        {'test1': 'test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202'.encode('utf_16')}
    )
    testraise(
        '17test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202',
        '17test\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202 %(test1)s',
        {'test1': 'test1\u00E9\u00EB\u00FA\u00FB\u00FC\u0103\u0178\u01A1\u0202'.encode('utf_32')}
    )
    testraise(
        '18test\u00E9\u00EB\u00FA\u00FB\u00FC test1\u00E9\u00EB\u00FA\u00FB\u00FC',
        '18test\u00E9\u00EB\u00FA\u00FB\u00FC %(test1)s',
        {'test1': 'test1\u00E9\u00EB\u00FA\u00FB\u00FC'.encode('latin_1')}
    )
    testraise(
        '19test test1',
        '19test %(test1)s',
        {'test1': 'test1'.encode('cp500')}
    )
    testraise(
        '20test test1',
        '20test %(test1)s',
        {'test1': 'test1'.encode('euc_jp')}
    )
    # make utf-8 string,many chars
    l = []  # @IgnorePep8
    for i in range(0, pow(256, 2)):
        l.append(chr(i))
    s = ''.join(l)
    print(type(s))
    testraise('', s)
    # print type(s)
    s2 = s.encode('utf-8')
    print(type(s2))
    testraise('', s2)

    # make iso-8859-1 string,many chars
    l = []  # @IgnorePep8
    for i in range(0, 256):
        l.append(chr(i))
    s = ''.join(l)
    print(type(s))
    # print s
    testraise('', s)
    s2 = s.decode('latin_1')
    print(type(s2))
    testraise('', s2)


if __name__ == '__main__':
    botsinit.generalinit('config')
    botsinit.initbotscharsets()
    botsglobal.logger = botsinit.initenginelogging('engine')
    botsglobal.ini.set('settings', 'debug', 'False')
    testrun()
    botsglobal.ini.set('settings', 'debug', 'True')
    testrun()
