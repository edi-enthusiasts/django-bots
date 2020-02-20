# -*- coding: utf-8 -*-

import shutil
import os
import subprocess
import pytest
import utilsunit
import bots.botslib as botslib
from bots.botsconfig import DONE

'''
plugin unitconfirm.zip
active all routes
before each run: clear transactions!

tested is:
- seperate unit tests
- total expectation of whole run
- seperate unit-tests to check confirm-rules
'''

botssys = os.path.join('bots', 'botssys')
pytestmark = pytest.mark.usefixtures('run_engine', 'engine_logging', 'bots_db', 'confirm_rules')


@pytest.fixture(scope='module')
def run_engine():
    newcommand = ['python', '-m', 'bots-engine']
    shutil.rmtree(os.path.join(botssys, 'outfile'), ignore_errors=True)  # remove whole output directory
    assert not subprocess.call(newcommand)


@pytest.fixture(scope='module')
def confirm_rules():
    botslib.prepare_confirmrules()


@pytest.mark.plugin_test
def test_routetestmdn():
    lijst = utilsunit.getdir(os.path.join(botssys, 'outfile', 'confirm', 'mdn', '*'))
    assert len(lijst) == 0

    nr_rows = 0
    for row in botslib.query(
        '''SELECT idta, confirmed, confirmidta FROM ta
            WHERE status=%(status)s
            AND statust=%(statust)s
            AND idroute=%(idroute)s
            AND confirmtype=%(confirmtype)s
            AND confirmasked=%(confirmasked)s
            AND frommail != ''
            ORDER BY idta DESC''',
        {
            'status': 220,
            'statust': DONE,
            'idroute': 'testmdn',
            'confirmtype': 'send-email-MDN',
            'confirmasked': True
        }
    ):
        nr_rows += 1
        print(row['idta'], row['confirmed'], row['confirmidta'])
        assert row['confirmed']
        assert row['confirmidta'] != 0
    else:
        assert nr_rows == 1

    nr_rows = 0
    for row in botslib.query(
        '''SELECT idta, confirmed, confirmidta FROM ta
            WHERE status=%(status)s
            AND statust=%(statust)s
            AND idroute=%(idroute)s
            AND confirmtype=%(confirmtype)s
            AND confirmasked=%(confirmasked)s
            AND frommail != ''
            ORDER BY idta DESC''',
        {
            'status': 500,
            'statust': DONE,
            'idroute': 'testmdn',
            'confirmtype': 'ask-email-MDN',
            'confirmasked': True
        }
    ):
        nr_rows += 1
        assert row['confirmed']
        assert row['confirmidta'] != 0
    else:
        assert nr_rows == 1


@pytest.mark.plugin_test
def testroutetestmdn2():
    lijst = utilsunit.getdir(os.path.join(botssys, 'outfile', 'confirm', 'mdn2', '*'))
    assert len(lijst) == 0

    nr_rows = 0
    for row in botslib.query(
        '''SELECT idta, confirmed, confirmidta FROM ta
            WHERE status=%(status)s
            AND statust=%(statust)s
            AND idroute=%(idroute)s
            AND confirmtype=%(confirmtype)s
            AND confirmasked=%(confirmasked)s
            AND frommail != ''
            ORDER BY idta DESC''',
        {
            'status': 500,
            'statust': DONE,
            'idroute': 'testmdn2',
            'confirmtype': 'ask-email-MDN',
            'confirmasked': True
        }
    ):
        nr_rows += 1
        assert not row['confirmed']
        assert row['confirmidta'] == 0
    else:
        assert nr_rows == 1


@pytest.mark.plugin_test
def testrouteotherx12():
    lijst = utilsunit.getdir(os.path.join(botssys, 'outfile', 'confirm', 'otherx12', '*'))
    assert len(lijst) == 15


@pytest.mark.plugin_test
def testroutetest997():
    '''
    test997 1:  pickup 850*1    ask confirm 850*2   gen & send 850*2
                                send confirm 850*1  gen & send 997*1
    test997 2:  receive 997*1   confirm 850*1       gen xml*1
                receive 850*2   ask confirm 850*3   gen 850*3
                                send confirm 850*2  gen & send 997*2
    test997 3:  receive 997*2   confirm 850*2       gen & send xml (to trash)
                                                    send 850*3 (to trash)
                                                    send xml (to trash)
    '''
    lijst = utilsunit.getdir(os.path.join(botssys, 'outfile', 'confirm', 'x12', '*'))
    assert len(lijst) == 0

    lijst = utilsunit.getdir(os.path.join(botssys, 'outfile', 'confirm', 'trash', '*'))
    assert len(lijst) == 6

    counter = 0
    for row in botslib.query(
        '''SELECT idta, confirmed, confirmidta FROM ta
            WHERE status=%(status)s
            AND statust=%(statust)s
            AND idroute=%(idroute)s
            AND confirmtype=%(confirmtype)s
            AND confirmasked=%(confirmasked)s
            ORDER BY idta DESC''',
        {
            'status': 400,
            'statust': DONE,
            'idroute': 'test997',
            'confirmtype': 'ask-x12-997',
            'confirmasked': True
        }
    ):
        counter += 1
        if counter == 1:
            assert not row['confirmed']
            assert row['confirmidta'] == 0
        elif counter == 2:
            assert row['confirmed']
            assert row['confirmidta'] != 0
        else:
            break
    else:
        assert counter != 0

    for row in botslib.query(
        '''SELECT idta, confirmed, confirmidta FROM ta
            WHERE status=%(status)s
            AND statust=%(statust)s
            AND idroute=%(idroute)s
            AND confirmtype=%(confirmtype)s
            AND confirmasked=%(confirmasked)s
            ORDER BY idta DESC''',
        {
            'status': 310,
            'statust': DONE,
            'idroute': 'test997',
            'confirmtype': 'send-x12-997',
            'confirmasked': True
        }
    ):
        counter += 1
        if counter <= 2:
            assert row['confirmed']
            assert row['confirmidta'] != 0
        else:
            break
    else:
        assert counter != 0


@pytest.mark.plugin_test
def testroutetestcontrl():
    '''
    test997 1:  pickup ORDERS*1   ask confirm ORDERS*2   gen & send ORDERS*2
                                  send confirm ORDERS*1  gen & send CONTRL*1
    test997 2:  receive CONTRL*1  confirm ORDERS*1       gen xml*1
                receive ORDERS*2  ask confirm ORDERS*3   gen ORDERS*3
                                  send confirm ORDERS*2  gen & send CONTRL*2
    test997 3:  receive CONTRL*2  confirm ORDERS*2       gen & send xml (to trash)
                                                         send ORDERS*3 (to trash)
                                                         send xml (to trash)
    '''
    lijst = utilsunit.getdir(os.path.join(botssys, 'outfile', 'confirm', 'edifact', '*'))
    assert len(lijst) == 0

    lijst = utilsunit.getdir(os.path.join(botssys, 'outfile', 'confirm', 'trash', '*'))
    assert len(lijst) == 6

    counter = 0
    for row in botslib.query(
        '''SELECT idta, confirmed, confirmidta FROM ta
            WHERE status=%(status)s
            AND statust=%(statust)s
            AND idroute=%(idroute)s
            AND confirmtype=%(confirmtype)s
            AND confirmasked=%(confirmasked)s
            ORDER BY idta DESC''',
        {
            'status': 400,
            'statust': DONE,
            'idroute': 'testcontrl',
            'confirmtype': 'ask-edifact-CONTRL',
            'confirmasked': True
        }
    ):
        counter += 1
        if counter == 1:
            assert not row['confirmed']
            assert row['confirmidta'] == 0
        elif counter == 2:
            assert row['confirmed']
            assert row['confirmidta'] != 0
        else:
            break
    else:
        assert counter != 0

    for row in botslib.query(
        '''SELECT idta, confirmed, confirmidta FROM ta
            WHERE status=%(status)s
            AND statust=%(statust)s
            AND idroute=%(idroute)s
            AND confirmtype=%(confirmtype)s
            AND confirmasked=%(confirmasked)s
            ORDER BY idta DESC''',
        {
            'status': 310,
            'statust': DONE,
            'idroute': 'testcontrl',
            'confirmtype': 'send-edifact-CONTRL',
            'confirmasked': True
        }
    ):
        counter += 1
        if counter <= 2:
            assert row['confirmed']
            assert row['confirmidta'] != 0
        else:
            break
    else:
        assert counter != 0


@pytest.mark.plugin_test
def testconfirmrulesdirect():
    assert botslib.checkconfirmrules('send-x12-997', idroute='idroute', idchannel='tochannel', topartner='topartner', frompartner='frompartner', editype='x12', messagetype='messagetype')
    assert botslib.checkconfirmrules('send-x12-997', idroute='idroute', idchannel='tochannel', topartner='topartner', frompartner='frompartner', editype='x12', messagetype='justfortes')
    assert botslib.checkconfirmrules('send-x12-997', idroute='idroute', idchannel='tochannel', topartner='topartner', frompartner='frompartner', editype='x12', messagetype='justfortest2')
    assert not botslib.checkconfirmrules('send-x12-997', idroute='idroute', idchannel='tochannel', topartner='topartner', frompartner='frompartner', editype='x12', messagetype='justfortest')

    assert botslib.checkconfirmrules('send-email-MDN', idroute='idroute', idchannel='tochannel', topartner='topartner', frompartner='frompartner', editype='x12', messagetype='messagetype')
    assert not botslib.checkconfirmrules('send-email-MDN', idroute='otherx12', idchannel='tochannel', topartner='topartner', frompartner='frompartner', editype='x12', messagetype='messagetype')
    assert not botslib.checkconfirmrules('send-email-MDN', idroute='idroute', idchannel='mdn2_in', topartner='topartner', frompartner='frompartner', editype='x12', messagetype='messagetype')
    assert not botslib.checkconfirmrules('send-email-MDN', idroute='idroute', idchannel='tochannel', topartner='partnerunittest', frompartner='frompartner', editype='x12', messagetype='messagetype')
    assert not botslib.checkconfirmrules('send-email-MDN', idroute='idroute', idchannel='tochannel', topartner='topartner', frompartner='partnerunittest', editype='x12', messagetype='messagetype')
    assert not botslib.checkconfirmrules('send-email-MDN', idroute='otherx12', idchannel='mdn2_in', topartner='partnerunittest', frompartner='partnerunittest', editype='x12', messagetype='messagetype')
    assert botslib.checkconfirmrules('send-email-MDN', idroute='otherx1', idchannel='mdn2_i', topartner='partnerunittes', frompartner='partnerunittes', editype='x12', messagetype='messagetype')
