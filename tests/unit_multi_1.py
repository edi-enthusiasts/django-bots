# -*- coding: utf-8 -*-

import filecmp
import os
import subprocess
import glob
import pytest
import utilsunit
import bots.botslib as botslib
import bots.botsglobal as botsglobal
import bots.transform as transform
from bots.botsconfig import EXTERNOUT, PARSED, SPLITUP, TRANSLATED

'''
plugin 'unit_multi_1'
enable routes
not an acceptance test.
'''


@pytest.fixture(scope='module')
def utils_logger():
    utilsunit.dummylogger()
    utilsunit.cleanoutputdir()


def grammartest(l, expect_error=True):
    if expect_error:
        assert subprocess.call(l), 'grammartest: expected error, but no error'
    else:
        assert not subprocess.call(l), 'grammartest: expected no error, but received an error'


@pytest.mark.usefixtures('bots_db', 'utils_logger')
@pytest.mark.plugin_test
def test_references():
    utilsunit.RunTestCompareResults(
        ['python', '-m', 'bots-engine', 'testreference'],
        {
            'status': 0,
            'lastreceived': 1,
            'lasterror': 0,
            'lastdone': 1,
            'lastok': 0,
            'lastopen': 0,
            'send': 1,
            'processerrors': 0,
            'filesize': 262
        }
    )
    ta_externout = utilsunit.getlastta(EXTERNOUT)
    assert ta_externout['botskey'] == 'BOTSKEY01', 'testreference: botskey not OK'

    ta_externout = utilsunit.getlastta(PARSED)
    assert ta_externout['reference'] == 'UNBREF01', 'testreference: unb ref not OK'

    ta_externout = utilsunit.getlastta(SPLITUP)
    assert ta_externout['reference'] == 'BOTSKEY01', 'testreference: botskey not OK'
    assert ta_externout['botskey'] == 'BOTSKEY01', 'testreference: botskey not OK'

    ta_externout = utilsunit.getlastta(TRANSLATED)
    assert ta_externout['reference'] == 'BOTSKEY01', 'testreference: botskey not OK'
    assert ta_externout['botskey'] == 'BOTSKEY01', 'testreference: botskey not OK'


@pytest.mark.usefixtures('utils_logger')
@pytest.mark.plugin_test
def test_KECA_charset():
    utilsunit.RunTestCompareResults(
        ['python', '-m', 'bots-engine', 'testkeca'],
        {
            'status': 0,
            'lastreceived': 1,
            'lasterror': 0,
            'lastdone': 1,
            'lastok': 0,
            'lastopen': 0,
            'send': 1,
            'processerrors': 0,
            'filesize': 333
        }
    )
    utilsunit.RunTestCompareResults(
        ['python', '-m', 'bots-engine', 'testkeca2'],
        {
            'status': 0,
            'lastreceived': 1,
            'lasterror': 0,
            'lastdone': 1,
            'lastok': 0,
            'lastopen': 0,
            'send': 1,
            'processerrors': 0,
            'filesize': 333
        }
    )


@pytest.mark.usefixtures('utils_logger')
@pytest.mark.plugin_test
def test_mailbag():
    utilsunit.RunTestCompareResults(
        ['python', '-m', 'bots-engine', 'mailbagtest'],
        {
            'status': 0,
            'lastreceived': 18,
            'lasterror': 0,
            'lastdone': 18,
            'lastok': 0,
            'lastopen': 0,
            'send': 44,
            'processerrors': 0,
            'filesize': 39344
        }
    )


@pytest.mark.usefixtures('utils_logger')
@pytest.mark.plugin_test
def test_passthrough():
    utilsunit.RunTestCompareResults(
        ['python', '-m', 'bots-engine', 'passthroughtest'],
        {
            'status': 0,
            'lastreceived': 4,
            'lasterror': 0,
            'lastdone': 4,
            'lastok': 0,
            'lastopen': 0,
            'send': 4,
            'processerrors': 0,
            'filesize': 7346
        }
    )


@pytest.mark.usefixtures('botsinit', 'utils_logger')
@pytest.mark.plugin_test
def test_botsidnr():
    botssys = botsglobal.ini.get('directories', 'botssys')
    utilsunit.RunTestCompareResults(
        ['python', '-m', 'bots-engine', 'test_botsidnr', 'test_changedelete'],
        {
            'status': 0,
            'lastreceived': 2,
            'lasterror': 0,
            'lastdone': 2,
            'lastok': 0,
            'lastopen': 0,
            'send': 4,
            'processerrors': 0,
            'filesize': 5813
        }
    )
    infile = 'infile/test_botsidnr/compare/unitnodebotsidnr1.edi'
    outfile = 'outfile/test_botsidnr/unitnodebotsidnr1.edi'
    infile2 = 'infile/test_botsidnr/compare/unitnodebotsidnr2.edi'
    outfile2 = 'outfile/test_botsidnr/unitnodebotsidnr2.edi'
    assert filecmp.cmp(os.path.join(botssys, infile), os.path.join(botssys, outfile)), 'error in file compare'
    assert filecmp.cmp(os.path.join(botssys, infile2), os.path.join(botssys, outfile2)), 'error in file2 compare'


@pytest.mark.usefixtures('botsinit')
@pytest.mark.plugin_test
def test_ccode_with_unicode():
    domein = 'test'
    tests = [
        ('key1', 'leftcode'),
        ('key2', '~!@#$%^&*()_+}{:";][=-/.,<>?`'),
        ('key3', '?�r����?�s??lzcn?'),
        ('key4', '?�?����䴨???�?��'),
        ('key5', '��???UI��?�`~'),
        ('key6', "a\xac\u1234\u20ac\U00008000"),
        ('key7', "abc_\u03a0\u03a3\u03a9.txt"),
        ('key8', "?�R����?�S??LZCN??"),
        ('key9', "�?�YܨI����???�?���`�`Z?"),
    ]

    botslib.changeq('''DELETE FROM ccode''')
    botslib.changeq('''DELETE FROM ccodetrigger''')
    botslib.changeq(
        '''INSERT INTO ccodetrigger (ccodeid)
            VALUES (%(ccodeid)s)''',
        {'ccodeid': domein}
    )

    for key, value in tests:
        botslib.changeq(
            '''INSERT INTO ccode (ccodeid_id,leftcode,rightcode,attr1,attr2,attr3,attr4,attr5,attr6,attr7,attr8)
                VALUES (%(ccodeid)s,%(leftcode)s,%(rightcode)s,'1','1','1','1','1','1','1','1')''',
            {'ccodeid': domein, 'leftcode': key, 'rightcode': value}
        )

    for key, value in tests:
        for row in botslib.query(
            '''SELECT rightcode FROM ccode
                WHERE ccodeid_id = %(ccodeid)s
                AND leftcode = %(leftcode)s''',
            {'ccodeid': domein, 'leftcode': key}
        ):
            assert row['rightcode'] == value, 'failure in test "%s": result "%s" is not equal to "%s"' % (key, row['rightcode'], value)
            break
        else:
            pytest.fail('??can not find testentry %s %s in db' % (key, value))


@pytest.mark.usefixtures('botsinit')
@pytest.mark.plugin_test
def test_unique_in_run_counter():
    assert 1 == int(transform.unique_runcounter('test')),  'test_unique_in_run_counter'
    assert 1 == int(transform.unique_runcounter('test2')), 'test_unique_in_run_counter'
    assert 2 == int(transform.unique_runcounter('test')),  'test_unique_in_run_counter'
    assert 3 == int(transform.unique_runcounter('test')),  'test_unique_in_run_counter'
    assert 2 == int(transform.unique_runcounter('test2')), 'test_unique_in_run_counter'


@pytest.mark.usefixtures('botsinit')
@pytest.mark.plugin_test
def test_partner_lookup():
    for s in ['attr1', 'attr2', 'attr3', 'attr4', 'attr5']:
        assert transform.partnerlookup('test', s) == s, 'test_partner_lookup'

    # test lookup for non existing partner
    idpartner = 'partner_not_there'
    assert transform.partnerlookup(idpartner, 'attr1', safe=True) == idpartner
    with pytest.raises(botslib.CodeConversionError):
        transform.partnerlookup(idpartner, 'attr1')

    # test lookup where no value is in the database
    idpartner = 'test2'
    assert transform.partnerlookup(idpartner, 'attr1') == 'attr1'
    with pytest.raises(botslib.CodeConversionError):
        transform.partnerlookup(idpartner, 'attr2')


# Test tricky grammars and messages (collision tests).
#  these test should run OK (no grammar-errors, reading & writing OK, extra checks in mappings scripts have to be OK)
@pytest.mark.usefixtures('utils_logger')
@pytest.mark.plugin_test
def test_grammar():
    utilsunit.RunTestCompareResults(
        ['python', '-m', 'bots-engine', 'testgrammar'],
        {
            'status': 0,
            'lastreceived': 8,
            'lasterror': 0,
            'lastdone': 8,
            'lastok': 0,
            'lastopen': 0,
            'send': 9,
            'processerrors': 0,
            'filesize': 2329
        }
    )


@pytest.mark.plugin_test
def test_grammar_collision():
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'CONDRAD96AUNERR001'])
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'CONDRAD96AUNERR002'])
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'CONDRAD96AUNERR003'])
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'CONDRAD96AUNERR004'])
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'CONDRAD96AUNERR005'])
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'CONDRAD96AUNERR006'])
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'CONDRAD96AUNbackcollision2'])
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'CONDRAD96AUNbackcollision3'])
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'CUSCARD96AUNnestedcollision1'])
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'CUSCARD96AUNnestedcollision2'])
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'CUSCARD96AUNnestedcollision3'])
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'DELFORD96AUNbackcollision'])
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'DELJITD96AUNbackcollision'])
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'INVRPTD96AUNnestingcollision'])
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'CONDRAD96AUNno'], expect_error=False)
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'CONDRAD96AUNno2'], expect_error=False)
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'CONESTD96AUNno'], expect_error=False)
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'CONESTD96AUNno2'], expect_error=False)
    grammartest(['python', '-m', 'bots-grammarcheck', 'edifact', 'CUSCARD96AUNno'], expect_error=False)


# Check if right entries have been read (partners/patnergroups).
@pytest.mark.usefixtures('botsinit')
@pytest.mark.plugin_test
def test_plugin():
    for row in botslib.query(
        '''SELECT COUNT(*) as count FROM partner
            WHERE isgroup = %(isgroup)s''',
        {'isgroup': False}
    ):
        assert row['count'] == 5, 'error partner count'
        break
    else:
        pytest.fail('no partner count?')

    for row in botslib.query(
        '''SELECT COUNT(*) as count FROM partner
            WHERE isgroup = %(isgroup)s''',
        {'isgroup': True}
    ):
        assert row['count'] == 3, 'error partner count'
        break
    else:
        pytest.fail('no partner count?')

    for row in botslib.query(
        '''SELECT COUNT(*) as count FROM partnergroup
            WHERE from_partner_id=%(from_partner_id)s''',
        {'from_partner_id': 'plugintest1'}
    ):
        assert row['count'] == 3, 'error partner count'
        break
    else:
        pytest.fail('no partner count?')

    for row in botslib.query(
        '''SELECT to_partner_id FROM partnergroup
            WHERE from_partner_id=%(from_partner_id)s''',
        {'from_partner_id': 'plugintest2'}
    ):
        assert row['to_partner_id'] == 'plugingroup2', 'error partner count'

    for row in botslib.query(
        '''SELECT COUNT(*) as count FROM partnergroup
            WHERE to_partner_id=%(to_partner_id)s  ''',
        {'to_partner_id': 'plugingroup2'}
    ):
        assert row['count'] == 2, 'error partner count'
        break
    else:
        pytest.fail('no partner count?')


# Test csv with records too big/small/not correct ending etc.
@pytest.mark.usefixtures('utils_logger')
@pytest.mark.plugin_test
def test_csv_orders_input():
    utilsunit.RunTestCompareResults(
        ['python', '-m', 'bots-engine', 'csv_orders_inputtest'],
        {
            'status': 1,
            'lastreceived': 5,
            'lasterror': 2,
            'lastdone': 3,
            'lastok': 0,
            'lastopen': 0,
            'send': 3,
            'processerrors': 0,
            'filesize': 131
        }
    )


@pytest.mark.usefixtures('utils_logger')
@pytest.mark.plugin_test
def test_extended_alt_func():
    utilsunit.RunTestCompareResults(
        ['python', '-m', 'bots-engine', 'testextendedalt'],
        {
            'status': 0,
            'lastreceived': 1,
            'lasterror': 0,
            'lastdone': 1,
            'lastok': 0,
            'lastopen': 0,
            'send': 3,
            'processerrors': 0,
            'filesize': 261
        }
    )


@pytest.mark.usefixtures('utils_logger')
@pytest.mark.plugin_test
def test_incoming_mime():
    utilsunit.RunTestCompareResults(
        ['python', '-m', 'bots-engine', 'testincomingmime'],
        {
            'status': 1,
            'lastreceived': 5,
            'lasterror': 5,
            'lastdone': 0,
            'lastok': 0,
            'lastopen': 0,
            'send': 0,
            'processerrors': 0,
            'filesize': 22592
        }
    )


@pytest.mark.usefixtures('botsinit', 'utils_logger')
@pytest.mark.plugin_test
def test_xml_out_specials():
    botssys = botsglobal.ini.get('directories', 'botssys')
    utilsunit.RunTestCompareResults(
        ['python', '-m', 'bots-engine', 'testxml_outspecials'],
        {
            'status': 0,
            'lastreceived': 2,
            'lasterror': 0,
            'lastdone': 2,
            'lastok': 0,
            'lastopen': 0,
            'send': 2,
            'processerrors': 0,
            'filesize': 1337
        }
    )
    cmpfile = 'infile/testxml_outspecials/compare/01xml02OK.xml'
    outfilepath = 'outfile/testxml_outspecials/*'
    for filename in glob.glob(os.path.join(botssys, outfilepath)):
        assert filecmp.cmp(os.path.join(botssys, cmpfile), filename), 'error in file compare'


@pytest.mark.usefixtures('utils_logger')
@pytest.mark.plugin_test
def test_max_file_size():
    utilsunit.RunTestCompareResults(
        ['python', '-m', 'bots-engine', 'maxsizeinfile'],
        {
            'status': 1,
            'lastreceived': 1,
            'lasterror': 1,
            'lastdone': 0,
            'lastok': 0,
            'lastopen': 0,
            'send': 0,
            'processerrors': 0,
            'filesize': 6702825
        }
    )
