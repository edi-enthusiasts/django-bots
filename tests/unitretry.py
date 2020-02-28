# -*- coding: utf-8 -*-

import subprocess
import pytest

from . import utilsunit
from bots import botslib
from bots import botsglobal
from bots.botsconfig import EXTERNOUT

'''
plugin unitretry.zip
activate routes
not an acceptance test.

ftp server needs to be activated (plain ftp, port 21)
before running: delete all transactions.!!!
input: mime (complex structure); 2 different edi attachments, and ' tekst' attachemnt
Note: some user scripts are written in this unit test; so one runs errors will occur; write user script which prevents error in next run
Note: runs OK if no errors in unit tests; that is : no exceptions are raised. The bots-engine runs do give errors, but this is needed for retries
'''

pytestmark = pytest.mark.usefixtures('general_init', 'dummy_logging', 'bots_db')


def change_communication_type(idchannel, to_type):
    botslib.changeq(
        '''UPDATE channel SET type = %(to_type)s WHERE idchannel = %(idchannel)s''',
        {'to_type': to_type, 'idchannel': idchannel}
    )


def scriptwrite(path, content):
    f = open(path, 'w')
    f.write(content)
    f.close()


def indicate_rereceive():
    count = 0
    for row in botslib.query('''SELECT idta FROM filereport ORDER BY idta DESC'''):
        count += 1
        botslib.changeq(
            '''UPDATE filereport SET retransmit=1 WHERE idta=%(idta)s''',
            {'idta': row['idta']}
        )
        if count >= 2:
            break


def indicate_send():
    count = 0
    for row in botslib.query(
        '''SELECT idta FROM ta WHERE status=%(status)s ORDER BY idta DESC''',
        {'status': EXTERNOUT}
    ):
        count += 1
        botslib.changeq(
            '''UPDATE ta SET retransmit=%(retransmit)s WHERE idta=%(idta)s''',
            {'retransmit': True, 'idta': row['idta']}
        )
        if count >= 2:
            break


@pytest.fixture(scope='module')
def unitretry_automatic_out(bots_db):  # @UnusedVariable
    out_channel = {
        'idchannel': 'unitretry_automatic_out',
        'inorout': 'out',
        'type': '',
        'charset': '',
        'host': '',
        'username': '',
        'secret': '',
        'starttls': False,
        'apop': False,
        'remove': False,
        'path': '',
        'filename': '',
        'lockname': '',
        'syslock': False,
        'parameters': '',
        'ftpaccount': '',
        'ftpactive': False,
        'ftpbinary': False,
        'askmdn': '',
        'sendmdn': '',
        'mdnchannel': '',
        'archivepath': '',
        'desc': 'This channel is only used for unit testing and can be safely deleted when not testing. (production mode)',
        'testpath': ''
    }
    botslib.changeq('DELETE FROM channel WHERE idchannel=%(idchannel)s', out_channel)
    botslib.changeq('INSERT INTO channel(' + ','.join(out_channel) + ') VALUES(' + ','.join(map('%({0})s'.format, out_channel)) + ')', out_channel)
    yield
    botslib.changeq('DELETE FROM channel WHERE idchannel=%(idchannel)s', out_channel)


@pytest.fixture(scope='module')
def unitretry_mime_out(bots_db):  # @UnusedVariable
    out_channel = {
        'idchannel': 'unitretry_mime_out',
        'inorout': 'out',
        'type': '',
        'charset': '',
        'host': '',
        'username': '',
        'secret': '',
        'starttls': False,
        'apop': False,
        'remove': False,
        'path': '',
        'filename': '',
        'lockname': '',
        'syslock': False,
        'parameters': '',
        'ftpaccount': '',
        'ftpactive': False,
        'ftpbinary': False,
        'askmdn': '',
        'sendmdn': '',
        'mdnchannel': '',
        'archivepath': '',
        'desc': 'This channel is only used for unit testing and can be safely deleted when not testing. (production mode)',
        'testpath': ''
    }
    botslib.changeq('DELETE FROM channel WHERE idchannel=%(idchannel)s', out_channel)
    botslib.changeq('INSERT INTO channel(' + ','.join(out_channel) + ') VALUES(' + ','.join(map('%({0})s'.format, out_channel)) + ')', out_channel)
    yield
    botslib.changeq('DELETE FROM channel WHERE idchannel=%(idchannel)s', out_channel)


@pytest.fixture(scope='module')
def unitretry_automatic(bots_db, unitretry_automatic_out):  # @UnusedVariable
    route = {
        'idroute': 'unitretry_automatic',
        'seq': 1,
        'active': True,
        'fromchannel_id': None,
        'fromeditype': '',
        'frommessagetype': '',
        'tochannel_id': 'unitretry_automatic_out',
        'toeditype': '',
        'tomessagetype': '',
        'alt': '',
        'testindicator': '',
        'translateind': 1,
        'notindefaultrun': 0,
        'desc': 'This route is only used for unit testing and can be safely deleted when not testing. (production mode)',
        'defer': False
    }
    botslib.changeq('DELETE FROM routes WHERE idroute=%(idroute)s', route)
    botslib.changeq('INSERT INTO routes(' + ','.join(route) + ') VALUES(' + ','.join(map('%({0})s'.format, route)) + ')', route)
    yield
    botslib.changeq('DELETE FROM routes WHERE idroute=%(idroute)s', route)


@pytest.fixture(scope='module')
def unitretry_automatic3(bots_db, unitretry_automatic_out):  # @UnusedVariable
    route3 = {
        'idroute': 'unitretry_automatic3',
        'seq': 1,
        'active': True,
        'fromchannel_id': None,
        'fromeditype': '',
        'frommessagetype': '',
        'tochannel_id': 'unitretry_automatic_out',
        'toeditype': '',
        'tomessagetype': '',
        'alt': '',
        'testindicator': '',
        'translateind': 1,
        'notindefaultrun': 0,
        'desc': 'This route is only used for unit testing and can be safely deleted when not testing. (production mode)',
        'defer': False
    }
    botslib.changeq('DELETE FROM routes WHERE idroute=%(idroute)s', route3)
    botslib.changeq('INSERT INTO routes(' + ','.join(route3) + ') VALUES(' + ','.join(map('%({0})s'.format, route3)) + ')', route3)
    yield
    botslib.changeq('DELETE FROM routes WHERE idroute=%(idroute)s', route3)


@pytest.fixture(scope='module')
def unitretry_mime(bots_db, unitretry_mime_out):  # @UnusedVariable
    route3 = {
        'idroute': 'unitretry_mime',
        'seq': 1,
        'active': True,
        'fromchannel_id': None,
        'fromeditype': '',
        'frommessagetype': '',
        'tochannel_id': 'unitretry_mime_out',
        'toeditype': '',
        'tomessagetype': '',
        'alt': '',
        'testindicator': '',
        'translateind': 1,
        'notindefaultrun': 0,
        'desc': 'This route is only used for unit testing and can be safely deleted when not testing. (production mode)',
        'defer': False
    }
    botslib.changeq('DELETE FROM routes WHERE idroute=%(idroute)s', route3)
    botslib.changeq('INSERT INTO routes(' + ','.join(route3) + ') VALUES(' + ','.join(map('%({0})s'.format, route3)) + ')', route3)
    yield
    botslib.changeq('DELETE FROM routes WHERE idroute=%(idroute)s', route3)


# ~~~~route unitretry_automatic~~~~
@pytest.mark.usefixtures('unitretry_automatic', 'unitretry_automatic3')
@pytest.mark.plugin_test
def test_retry_automatic():
    # channel has type file: this goes OK
    change_communication_type('unitretry_automatic_out', 'file')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_automatic', 'unitretry_automatic3'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 2,
            'lasterror': 0,
            'lastdone': 2,
            'lastok': 0,
            'lastopen': 0,
            'send': 2,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report
    row = utilsunit.getreportlastrun()
    assert row['filesize'] == 1482, '1 filesize not OK: %s' % row['filesize']

    # change channel type to ftp: errors (run twice)
    change_communication_type('unitretry_automatic_out', 'ftp')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_automatic', 'unitretry_automatic3'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 1,
            'lastreceived': 2,
            'lasterror': 2,
            'lastdone': 0,
            'lastok': 0,
            'lastopen': 0,
            'send': 0,
            'processerrors': 1
        },
        utilsunit.getreportlastrun()
    )  # check report
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_automatic', 'unitretry_automatic3'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 1,
            'lastreceived': 2,
            'lasterror': 2,
            'lastdone': 0,
            'lastok': 0,
            'lastopen': 0,
            'send': 0,
            'processerrors': 1
        },
        utilsunit.getreportlastrun()
    )  # check report

    # change channel type to file and do automaticretrycommunication: OK
    change_communication_type('unitretry_automatic_out', 'file')
    assert not subprocess.call(['python', '-m', 'bots-engine', '--automaticretrycommunication'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 4,
            'lasterror': 0,
            'lastdone': 4,
            'lastok': 0,
            'lastopen': 0,
            'send': 4,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report

    # run automaticretrycommunication again: no new run is made, same results as last run
    assert not subprocess.call(['python', '-m', 'bots-engine', '--automaticretrycommunication'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 4,
            'lasterror': 0,
            'lastdone': 4,
            'lastok': 0,
            'lastopen': 0,
            'send': 4,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report

    # channel has type file: this goes OK
    change_communication_type('unitretry_automatic_out', 'file')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_automatic', 'unitretry_automatic3'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 2,
            'lasterror': 0,
            'lastdone': 2,
            'lastok': 0,
            'lastopen': 0,
            'send': 2,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report
    row = utilsunit.getreportlastrun()
    assert row['filesize'] == 1482, '2 filesize not OK: %s' % row['filesize']

    # rereceive last 2 files
    indicate_rereceive()
    assert not subprocess.call(['python', '-m', 'bots-engine', '--rereceive'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 2,
            'lasterror': 0,
            'lastdone': 2,
            'lastok': 0,
            'lastopen': 0,
            'send': 1,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report
    row = utilsunit.getreportlastrun()
    assert row['filesize'] == 1482, '3 filesize not OK: %s' % row['filesize']

    # resend last 2 files
    indicate_send()
    assert not subprocess.call(['python', '-m', 'bots-engine', '--resend'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 2,
            'lasterror': 0,
            'lastdone': 2,
            'lastok': 0,
            'lastopen': 0,
            'send': 2,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report

    # ***run with communciation errors, run OK, communciation errors, run OK, run automaticretry
    # change channel type to ftp: errors
    change_communication_type('unitretry_automatic_out', 'ftp')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_automatic', 'unitretry_automatic3'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 1,
            'lastreceived': 2,
            'lasterror': 2,
            'lastdone': 0,
            'lastok': 0,
            'lastopen': 0,
            'send': 0,
            'processerrors': 1
        },
        utilsunit.getreportlastrun()
    )  # check report

    # channel has type file: this goes OK
    change_communication_type('unitretry_automatic_out', 'file')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_automatic', 'unitretry_automatic3'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 2,
            'lasterror': 0,
            'lastdone': 2,
            'lastok': 0,
            'lastopen': 0,
            'send': 2,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report
    row = utilsunit.getreportlastrun()
    assert row['filesize'] == 1482, '4 filesize not OK: %s' % row['filesize']

    # change channel type to ftp: errors
    change_communication_type('unitretry_automatic_out', 'ftp')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_automatic', 'unitretry_automatic3'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 1,
            'lastreceived': 2,
            'lasterror': 2,
            'lastdone': 0,
            'lastok': 0,
            'lastopen': 0,
            'send': 0,
            'processerrors': 1
        },
        utilsunit.getreportlastrun()
    )  # check report

    # channel has type file: this goes OK
    change_communication_type('unitretry_automatic_out', 'file')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_automatic', 'unitretry_automatic3'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 2,
            'lasterror': 0,
            'lastdone': 2,
            'lastok': 0,
            'lastopen': 0,
            'send': 2,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report
    row = utilsunit.getreportlastrun()
    assert row['filesize'] == 1482, '5 filesize not OK: %s' % row['filesize']

    # change channel type to file and do automaticretrycommunication: OK
    change_communication_type('unitretry_automatic_out', 'file')
    assert not subprocess.call(['python', '-m', 'bots-engine', '--automaticretrycommunication'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 4,
            'lasterror': 0,
            'lastdone': 4,
            'lastok': 0,
            'lastopen': 0,
            'send': 4,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report

    # change channel type to ftp: errors
    change_communication_type('unitretry_automatic_out', 'ftp')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_automatic', 'unitretry_automatic3'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 1,
            'lastreceived': 2,
            'lasterror': 2,
            'lastdone': 0,
            'lastok': 0,
            'lastopen': 0,
            'send': 0,
            'processerrors': 1
        },
        utilsunit.getreportlastrun()
    )  # check report

    # channel has type file: this goes OK
    change_communication_type('unitretry_automatic_out', 'file')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_automatic', 'unitretry_automatic3'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 2,
            'lasterror': 0,
            'lastdone': 2,
            'lastok': 0,
            'lastopen': 0,
            'send': 2,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report
    row = utilsunit.getreportlastrun()
    assert row['filesize'] == 1482, '6 filesize not OK: %s' % row['filesize']

    # change channel type to file and do automaticretrycommunication: OK
    change_communication_type('unitretry_automatic_out', 'file')
    assert not subprocess.call(['python', '-m', 'bots-engine', '--automaticretrycommunication'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 2,
            'lasterror': 0,
            'lastdone': 2,
            'lastok': 0,
            'lastopen': 0,
            'send': 2,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report


# ~~~~route unitretry_mime: logic for mime-handling is different for resend~~~~
@pytest.mark.usefixtures('unitretry_mime_out')
@pytest.mark.plugin_test
def test_retry_mime():
    change_communication_type('unitretry_mime_out', 'mimefile')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_mime'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 1,
            'lasterror': 0,
            'lastdone': 1,
            'lastok': 0,
            'lastopen': 0,
            'send': 1,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report
    row = utilsunit.getreportlastrun()
    assert row['filesize'] == 741, '7 filesize not OK: %s' % row['filesize']

    # change channel type to ftp: errors (run twice)
    change_communication_type('unitretry_mime_out', 'ftp')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_mime'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 1,
            'lastreceived': 1,
            'lasterror': 1,
            'lastdone': 0,
            'lastok': 0,
            'lastopen': 0,
            'send': 0,
            'processerrors': 1
        },
        utilsunit.getreportlastrun()
    )  # check report
    change_communication_type('unitretry_mime_out', 'ftp')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_mime'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 1,
            'lastreceived': 1,
            'lasterror': 1,
            'lastdone': 0,
            'lastok': 0,
            'lastopen': 0,
            'send': 0,
            'processerrors': 1
        },
        utilsunit.getreportlastrun()
    )  # check report
    row = utilsunit.getreportlastrun()
    assert row['filesize'] == 741, '8 filesize not OK: %s' % row['filesize']

    # change channel type to mimefile and do automaticretrycommunication: OK
    change_communication_type('unitretry_mime_out', 'mimefile')
    assert not subprocess.call(['python', '-m', 'bots-engine', '--automaticretrycommunication'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 2,
            'lasterror': 0,
            'lastdone': 2,
            'lastok': 0,
            'lastopen': 0,
            'send': 2,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report

    # run automaticretrycommunication again: no new run is made, same results as last run
    assert not subprocess.call(['python', '-m', 'bots-engine', '--automaticretrycommunication'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 2,
            'lasterror': 0,
            'lastdone': 2,
            'lastok': 0,
            'lastopen': 0,
            'send': 2,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report

    # channel has type file: this goes OK
    change_communication_type('unitretry_mime_out', 'mimefile')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_mime'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 1,
            'lasterror': 0,
            'lastdone': 1,
            'lastok': 0,
            'lastopen': 0,
            'send': 1,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report
    row = utilsunit.getreportlastrun()
    assert row['filesize'] == 741, '9 filesize not OK: %s' % row['filesize']

    # ***run with communciation errors, run OK, communciation errors, run OK, run automaticretry
    # change channel type to ftp: errors
    change_communication_type('unitretry_mime_out', 'ftp')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_mime'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 1,
            'lastreceived': 1,
            'lasterror': 1,
            'lastdone': 0,
            'lastok': 0,
            'lastopen': 0,
            'send': 0,
            'processerrors': 1
        },
        utilsunit.getreportlastrun()
    )  # check report

    # channel has type file: this goes OK
    change_communication_type('unitretry_mime_out', 'mimefile')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_mime'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 1,
            'lasterror': 0,
            'lastdone': 1,
            'lastok': 0,
            'lastopen': 0,
            'send': 1,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report
    row = utilsunit.getreportlastrun()
    assert row['filesize'] == 741, '10 filesize not OK: %s' % row['filesize']

    # change channel type to ftp: errors
    change_communication_type('unitretry_mime_out', 'ftp')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_mime'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 1,
            'lastreceived': 1,
            'lasterror': 1,
            'lastdone': 0,
            'lastok': 0,
            'lastopen': 0,
            'send': 0,
            'processerrors': 1
        },
        utilsunit.getreportlastrun()
    )  # check report

    # channel has type file: this goes OK
    change_communication_type('unitretry_mime_out', 'mimefile')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_mime'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 1,
            'lasterror': 0,
            'lastdone': 1,
            'lastok': 0,
            'lastopen': 0,
            'send': 1,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report
    row = utilsunit.getreportlastrun()
    assert row['filesize'] == 741, '11 filesize not OK: %s' % row['filesize']

    # change channel type to file and do automaticretrycommunication: OK
    change_communication_type('unitretry_mime_out', 'mimefile')
    assert not subprocess.call(['python', '-m', 'bots-engine', '--automaticretrycommunication'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 2,
            'lasterror': 0,
            'lastdone': 2,
            'lastok': 0,
            'lastopen': 0,
            'send': 2,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report

    # change channel type to ftp: errors
    change_communication_type('unitretry_mime_out', 'ftp')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_mime'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 1,
            'lastreceived': 1,
            'lasterror': 1,
            'lastdone': 0,
            'lastok': 0,
            'lastopen': 0,
            'send': 0,
            'processerrors': 1
        },
        utilsunit.getreportlastrun()
    )  # check report

    # channel has type file: this goes OK
    change_communication_type('unitretry_mime_out', 'mimefile')
    assert not subprocess.call(['python', '-m', 'bots-engine', 'unitretry_mime'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 1,
            'lasterror': 0,
            'lastdone': 1,
            'lastok': 0,
            'lastopen': 0,
            'send': 1,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report
    row = utilsunit.getreportlastrun()
    assert row['filesize'] == 741, '12 filesize not OK: %s' % row['filesize']

    # change channel type to file and do automaticretrycommunication: OK
    change_communication_type('unitretry_mime_out', 'mimefile')
    assert not subprocess.call(['python', '-m', 'bots-engine', '--automaticretrycommunication'])  # run bots
    botsglobal.db.commit()
    utilsunit.comparedicts(
        {
            'status': 0,
            'lastreceived': 1,
            'lasterror': 0,
            'lastdone': 1,
            'lastok': 0,
            'lastopen': 0,
            'send': 1,
            'processerrors': 0
        },
        utilsunit.getreportlastrun()
    )  # check report
