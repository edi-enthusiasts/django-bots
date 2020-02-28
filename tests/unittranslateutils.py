# -*- coding: utf-8 -*-

import pytest
import time
import bots.botslib as botslib
import bots.transform as transform
import bots.validate_email as validate_email

'''
plugin unittranslateutils.zip
in bots.ini:  runacceptancetest = False
'''

pytestmark = pytest.mark.usefixtures('bots_db', 'engine_logging')


def delete_ccode(ccodeid_id, leftcode, rightcode=None):
    where_data = {
        'ccodeid_id': ccodeid_id,
        'leftcode': leftcode
    }
    if rightcode is not None:
        where_data['rightcode'] = rightcode

    where_clause = ' AND '.join(map('{0}=%({0})s'.format, where_data))
    botslib.changeq('DELETE FROM ccode WHERE ' + where_clause, where_data)


def insert_ccode(ccodeid_id, leftcode, rightcode='', **kwargs):
    ccode = {
        'ccodeid_id': ccodeid_id,
        'leftcode': leftcode,
        'rightcode': rightcode
    }
    ccode.update(('attr'+i, kwargs.get('attr'+i, '')) for i in map(str, range(1, 9)))
    botslib.changeq(
        'INSERT INTO ccode (' + ','.join(ccode) + ') VALUES (' + ','.join(map('%({0})s'.format, ccode)) + ')',
        ccode
    )


@pytest.fixture(scope='module')
def test_ccodes():
    delete_ccode('artikel', 'TESTIN')
    delete_ccode('artikel', 'TESTOUT')
    delete_ccode('list', 'list')

    insert_ccode('artikel', 'TESTIN', 'TESTOUT', attr1='TESTATTR1')
    insert_ccode('artikel', 'TESTOUT', 'TESTIN')
    for i in ['1', '2', '4', '5']:
        insert_ccode('list', 'list', i)
    yield

    delete_ccode('artikel', 'TESTIN')
    delete_ccode('artikel', 'TESTOUT')
    delete_ccode('list', 'list')


class MyObject(object):
    c = 'c_éëèêíïìîóöòõôúüùûáäàãâñýÿÖÓÒÕ'

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)


def persist_lookup_ts(domein, botskey):
    ''' lookup persistent values in db.'''
    for row in botslib.query(
        '''SELECT ts FROM persist
           WHERE domein=%(domein)s
           AND botskey=%(botskey)s''',
        {'domein': domein, 'botskey': botskey}
    ):
        return row['ts']
    return None


@pytest.mark.unit_test
class TestTranslate:

    def test_persist_strings(self):
        domein = 'test'
        botskey = 'test'
        value = 'abcdedfgh'
        value2 = 'IEFJUKAHE*FMhrt4hr f.wch shjeriw'

        transform.persist_delete(domein, botskey)
        transform.persist_add(domein, botskey, value)
        with pytest.raises(botslib.PersistError):
            transform.persist_add(domein, botskey, value)  # is already present
        assert value == transform.persist_lookup(domein, botskey), 'basis'

        transform.persist_update(domein, botskey, value2)
        assert value2 == transform.persist_lookup(domein, botskey), 'basis'

        transform.persist_delete(domein, botskey)
        assert transform.persist_lookup(domein, botskey) is None, 'basis'

        transform.persist_update(domein, botskey, value)  # test-tet is not there. gives no error...

    def test_persist_unicode(self):
        domein = 'test'
        botskey = 'ëö1235:\ufb52\ufb66\ufedb'
        botskey3 = 'ëö135:\ufb52\ufb66\ufedb'
        value = 'xxxxxxxxxxxxxxxxx'
        value2 = 'IEFJUKAHE*FMhr\u0302\u0267t4hr f.wch shjeriw'
        value3 = '1/2/d' * 3024

        transform.persist_delete(domein, botskey)
        transform.persist_delete(domein, botskey3)
        transform.persist_add(domein, botskey3, value3)
        assert value3 == transform.persist_lookup(domein, botskey3), 'basis'

        transform.persist_add(domein, botskey, value)
        with pytest.raises(botslib.PersistError):
            transform.persist_add(domein, botskey, value)  # is already present
        assert value == transform.persist_lookup(domein, botskey), 'basis'

        transform.persist_update(domein, botskey, value2)
        assert value2 == transform.persist_lookup(domein, botskey), 'basis'

        transform.persist_delete(domein, botskey)
        assert transform.persist_lookup(domein, botskey) is None, 'basis'

        transform.persist_update(domein, botskey, value)  # is not there. gives no error...

    def test_persist_moreunicode(self):
        domein = 'test'
        botskey = 'éëèêíïìîóöòõôúüùûáäàãâ\ufb52\ufb66\ufedb'
        botskey3 = 'ëéèõöóòñýÿÖÓÒÕ'
        value = 'éëèêíïìîóöòõôúüùûáäàãâ\ufb52\ufb66\ufedbñýÿÖÓÒÕ'
        value2 = 'ëéèõöóò'
        value3 = '1/2/dñýÿÖÓÒÕ' * 3024

        transform.persist_delete(domein, botskey)
        transform.persist_delete(domein, botskey3)
        transform.persist_add(domein, botskey3, value3)
        assert value3 == transform.persist_lookup(domein, botskey3), 'basis'

        transform.persist_add(domein, botskey, value)
        with pytest.raises(botslib.PersistError):
            transform.persist_add(domein, botskey, value)  # is already present
        assert value == transform.persist_lookup(domein, botskey), 'basis'

        transform.persist_update(domein, botskey, value2)
        assert value2 == transform.persist_lookup(domein, botskey), 'basis'

        transform.persist_delete(domein, botskey)
        assert transform.persist_lookup(domein, botskey) is None, 'basis'

        transform.persist_update(domein, botskey, value)  # is not there. gives no error...

    def test_persist_object(self):
        ''' use objects for pickling '''
        domein = 'test'
        botskey = 'éëèêíïìîóöòõôúüùûáäàãâ\ufb52\ufb66\ufedb'
        myobject = MyObject('a_éëèêíïìîóöòõôúüùûáäàãâñýÿÖÓÒÕ', 'b_éëèêíïìîóöòõôúüùûáäàãâñýÿÖÓÒÕ')
        myobject.d = '1_éëèêíïìîóöòõôúüùûáäàãâñýÿÖÓÒÕ'
        myobject.e = 12345

        transform.persist_delete(domein, botskey)
        transform.persist_add(domein, botskey, myobject)
        assert myobject == transform.persist_lookup(domein, botskey), 'basis'

    def test_persist_timestamp(self):
        domein = 'test'
        botskey = 'timestamp'
        value = 'abcdedfgh'
        value2 = 'IEFJUKAHE*FMhrt4hr f.wch shjeriw'

        transform.persist_delete(domein, botskey)

        transform.persist_add(domein, botskey, value)
        ts1 = persist_lookup_ts(domein, botskey)
        time.sleep(1)
        with pytest.raises(botslib.PersistError):
            transform.persist_add(domein, botskey, value)  # is already present
        assert value == transform.persist_lookup(domein, botskey), 'basis'

        transform.persist_update(domein, botskey, value2)
        assert value2 == transform.persist_lookup(domein, botskey), 'basis'
        ts2 = persist_lookup_ts(domein, botskey)
        print(ts1, ts2)

    @pytest.mark.usefixtures('test_ccodes')
    def test_getcodeset(self):
        assert transform.getcodeset('artikel', 'TESTIN') == ['TESTOUT'], 'test getcodeset'
        assert transform.getcodeset('list', 'list') == ['1', '2', '4', '5'], 'test getcodeset'
        print(transform.getcodeset('list', 'list'))

    # Checks if backwards compatible function names still works
    @pytest.mark.usefixtures('test_ccodes')
    def test_code_conversion(self):
        # codeconversion via tabel ccode OLD functionnames:
        assert transform.codetconversion('artikel', 'TESTIN') == 'TESTOUT', 'basis'
        assert transform.safecodetconversion('artikel', 'TESTIN') == 'TESTOUT', 'basis'
        assert transform.safecodetconversion('artikel', 'TESTINNOT') == 'TESTINNOT', 'basis'
        with pytest.raises(botslib.CodeConversionError):
            transform.codetconversion('artikel', 'TESTINNOT')
        assert transform.rcodetconversion('artikel', 'TESTOUT') == 'TESTIN', 'basis'
        assert transform.safercodetconversion('artikel', 'TESTOUT') == 'TESTIN', 'basis'
        assert transform.safercodetconversion('artikel', 'TESTINNOT') == 'TESTINNOT', 'basis'
        with pytest.raises(botslib.CodeConversionError):
            transform.rcodetconversion('artikel', 'TESTINNOT')

        # attributes
        assert transform.codetconversion('artikel', 'TESTIN', 'attr1') == 'TESTATTR1', 'basis'
        assert transform.safecodetconversion('artikel', 'TESTIN', 'attr1') == 'TESTATTR1', 'basis'

        # codeconversion via tabel ccode:
        assert transform.ccode('artikel', 'TESTIN') == 'TESTOUT', 'basis'
        assert transform.safe_ccode('artikel', 'TESTIN') == 'TESTOUT', 'basis'
        assert transform.safe_ccode('artikel', 'TESTINNOT') == 'TESTINNOT', 'basis'
        with pytest.raises(botslib.CodeConversionError):
            transform.ccode('artikel', 'TESTINNOT')
        assert transform.reverse_ccode('artikel', 'TESTOUT') == 'TESTIN', 'basis'
        assert transform.safe_reverse_ccode('artikel', 'TESTOUT') == 'TESTIN', 'basis'
        assert transform.safe_reverse_ccode('artikel', 'TESTINNOT') == 'TESTINNOT', 'basis'
        with pytest.raises(botslib.CodeConversionError):
            transform.reverse_ccode('artikel', 'TESTINNOT')

        # attributes
        assert transform.ccode('artikel', 'TESTIN', 'attr1') == 'TESTATTR1', 'basis'
        assert transform.safe_ccode('artikel', 'TESTIN', 'attr1') == 'TESTATTR1', 'basis'

    def test_datemask(self):
        assert transform.datemask('12/31/2012', 'MM/DD/YYYY', 'YYYYMMDD') == '20121231', 'test datemask'
        assert transform.datemask('12/31/2012', 'MM/DD/YYYY', 'YYMMDD') == '201231', 'test datemask'

    def test_useoneof(self):
        assert transform.useoneof(None, 'test') == 'test', 'test useoneof'
        assert transform.useoneof('test', 'test1', 'test2') == 'test', 'test useoneof'
        assert transform.useoneof() is None, 'test useoneof'
        assert transform.useoneof(()) is None, 'test useoneof'
        assert transform.useoneof('') is None, 'test useoneof'
        assert transform.useoneof(None, None, None, None) is None, 'test useoneof'

    def test_dateformat(self):
        assert transform.dateformat('') is None, 'test dateformat'
        assert transform.dateformat(None) is None, 'test dateformat'
        assert transform.dateformat('12345678') == '102', 'test dateformat'
        with pytest.raises(botslib.BotsError):
            transform.dateformat('123456789')
        with pytest.raises(botslib.BotsError):
            transform.dateformat('1234567')
        assert transform.dateformat('123456789012') == '203', 'test dateformat'
        assert transform.dateformat('1234567890123456') == '718', 'test dateformat'

    def test_truncate(self):
        assert transform.truncate(5, None) is None, 'test truncate'
        assert transform.truncate(5, 'artikel') == 'artik', 'test truncate'
        assert transform.truncate(10, 'artikel') == 'artikel', 'test truncate'
        assert transform.truncate(1, 'artikel') == 'a', 'test truncate'
        assert transform.truncate(0, 'artikel') == '', 'test truncate'

    def test_concat(self):
        assert transform.concat(None, None) is None, 'test concatenate'
        assert transform.concat('artikel', None) == 'artikel', 'test concatenate'
        assert transform.concat(None, 'artikel') == 'artikel', 'test concatenate'
        assert transform.concat('', 'artikel') == 'artikel', 'test concatenate'
        assert transform.concat('artikel1', 'artikel2') == 'artikel1artikel2', 'test concatenate'
        assert transform.concat('artikel1', 'artikel2', sep=' ') == 'artikel1 artikel2', 'test concatenate'
        assert transform.concat('artikel1', 'artikel2', sep='\n') == 'artikel1\nartikel2', 'test concatenate'
        assert transform.concat('artikel1', 'artikel2', 'artikel3', sep='<br>') == 'artikel1<br>artikel2<br>artikel3', 'test concatenate'

    def test_unique(self):
        newdomain = 'test' + transform.unique('test')
        assert transform.unique(newdomain) == '1', 'init new domain'
        assert transform.unique(newdomain) == '2', 'next one'
        assert transform.unique(newdomain) == '3', 'next one'
        assert transform.unique(newdomain) == '4', 'next one'

        newdomain = 'test' + transform.unique('test')
        assert botslib.checkunique(newdomain, 1), 'init new domain'
        assert not botslib.checkunique(newdomain, 1), 'seq should be 2'
        assert not botslib.checkunique(newdomain, 3), 'seq should be 2'
        assert botslib.checkunique(newdomain, 2), 'next one'
        assert botslib.checkunique(newdomain, 3), 'next one'
        assert botslib.checkunique(newdomain, 4), 'next one'
        assert not botslib.checkunique(newdomain, 4), 'next one'
        assert not botslib.checkunique(newdomain, 6), 'next one'
        assert botslib.checkunique(newdomain, 5), 'next one'

        newdomain = 'test' + transform.unique('test')
        assert '1' == transform.unique(newdomain), 'init new domain'
        assert '1' == transform.unique(newdomain, updatewith=999), 'init new domain'
        assert '999' == transform.unique(newdomain, updatewith=9999), 'init new domain'
        assert '9999' == transform.unique(newdomain, updatewith=9999), 'init new domain'
        assert '9999' == transform.unique(newdomain, updatewith=20140404), 'init new domain'
        assert '20140404' == transform.unique(newdomain, updatewith=20140405), 'init new domain'
        assert '20140405' == transform.unique(newdomain, updatewith=20140406), 'init new domain'
        assert '20140406' == transform.unique(newdomain, updatewith=20140407), 'init new domain'
        assert '20140407' == transform.unique(newdomain, updatewith=20140408), 'init new domain'

    def test_ean(self):
        assert transform.addeancheckdigit('12345678901') == '123456789012', 'UPC'
        assert transform.calceancheckdigit('12345678901') == '2', 'UPC'
        assert transform.checkean('123456789012'), 'UPC'
        assert not transform.checkean('123456789011'), 'UPC'
        assert not transform.checkean('123456789013'), 'UPC'

        assert transform.addeancheckdigit('12345678901') == '123456789012', 'UPC'
        assert transform.calceancheckdigit('12345678901') == '2', 'UPC'
        assert transform.checkean('123456789012'), 'UPC'
        assert not transform.checkean('123456789011'), 'UPC'
        assert not transform.checkean('123456789013'), 'UPC'

        assert transform.addeancheckdigit('1234567') == '12345670', 'EAN8'
        assert transform.calceancheckdigit('1234567') == '0', 'EAN8'
        assert transform.checkean('12345670'), 'EAN8'
        assert not transform.checkean('12345679'), 'EAN8'
        assert not transform.checkean('12345671'), 'EAN8'

        assert transform.addeancheckdigit('123456789012') == '1234567890128', 'EAN13'
        assert transform.calceancheckdigit('123456789012') == '8', 'EAN13'
        assert transform.checkean('1234567890128'), 'EAN13'
        assert not transform.checkean('1234567890125'), 'EAN13'
        assert not transform.checkean('1234567890120'), 'EAN13'

        assert transform.addeancheckdigit('1234567890123') == '12345678901231', 'EAN14'
        assert transform.calceancheckdigit('1234567890123') == '1', 'EAN14'
        assert transform.checkean('12345678901231'), 'EAN14'
        assert not transform.checkean('12345678901230'), 'EAN14'
        assert not transform.checkean('12345678901236'), 'EAN14'

        assert transform.addeancheckdigit('12345678901234567') == '123456789012345675', 'UPC'
        assert transform.calceancheckdigit('12345678901234567') == '5', 'UPC'
        assert transform.checkean('123456789012345675'), 'UPC'
        assert not transform.checkean('123456789012345670'), 'UPC'
        assert not transform.checkean('123456789012345677'), 'UPC'

    def test_validate_email(self):
        assert validate_email.validate_email_address('test@gmail.com')
        assert validate_email.validate_email_address('niceandsimple@example.com')
        assert validate_email.validate_email_address('a.little.lengthy.but.fine@dept.example.com')
        assert validate_email.validate_email_address('disposable.style.email.with+symbol@example.com')
        assert validate_email.validate_email_address('other.email-with-dash@example.com')
        assert validate_email.validate_email_address('"much.more unusual"@example.com')
        assert validate_email.validate_email_address('"very.unusual.@.unusual.com"@example.com')
        assert validate_email.validate_email_address('''"very.(),:;<>[].VERY.very@\\ very.unusual"@strange.example.com''')
        assert validate_email.validate_email_address('admin@mailserver1')
        assert validate_email.validate_email_address('''#!$%&'*+-/=?^_`{}|~@example.org''')
        assert validate_email.validate_email_address('''"()<>[]:,;@\\\"!#$%&'*+-/=?^_`{}| ~.a"@example.org''')
        assert validate_email.validate_email_address('" "@example.org')
        assert validate_email.validate_email_address('üñîçøðé@example.com')
        assert validate_email.validate_email_address('test@üñîçøðé.com')
        assert validate_email.validate_email_address('"test@test"@gmail.com')

        assert not validate_email.validate_email_address('test.gmail.com')
        assert not validate_email.validate_email_address('test@test@gmail.com')
        assert not validate_email.validate_email_address('a"b(c)d,e:f;g<h>i[j\k]l@example.com')
        assert not validate_email.validate_email_address('just"not"right@example.com')
        assert not validate_email.validate_email_address('this is"not\allowed@example.com')
        assert not validate_email.validate_email_address('this is"not\allowed@example.com')
        assert not validate_email.validate_email_address('test..test@gmail.com')
        assert not validate_email.validate_email_address('test.test@gmail..com')
        assert not validate_email.validate_email_address('test test@gmail.com')
        assert validate_email.validate_email_address('"/C=NL/A=400NET/P=XXXXXX/O=XXXXXXXXXXXXXXXXXXXX XXXXXXXX/S=XXXXXXXXXXX XXXXXXXX/"@xgateprod.400net.nl')
        assert not validate_email.validate_email_address('/C=NL/A=400NET/P=XXXXX/O=XXXXXXXXXX XXXXXXXXXXXXXXXXXX/S=XXXXXXXXXXX XXXXXXXX/@xgateprod.400net.nl')
        assert validate_email.validate_email_address('/C=NL/A=400NET/P=XXXXX/O=XXXXXXXXXXXXXXXXXXXXXXXXXXXX/S=XXXXXXXXXXXXXXXXXXX/@xgateprod.400net.nl')
