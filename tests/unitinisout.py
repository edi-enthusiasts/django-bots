# -*- coding: utf-8 -*-

import os
import shutil
import filecmp
import pytest
import utilsunit
import bots.botslib as botslib
import bots.inmessage as inmessage
import bots.outmessage as outmessage
try:
    import json as simplejson
except ImportError:
    import simplejson  # @UnusedImport

from os.path import join as path_join

'''
plugin unitinisout.zip
in bots.ini: max_number_errors = 1
not an acceptance test
'''


pytestmark = pytest.mark.usefixtures('engine_logging', 'inisout_init')


@pytest.fixture(scope='module')
def unit_inisout(botssys):
    return path_join(botssys, 'infile', 'unitinisout')


@pytest.fixture(scope='module')
def unit_inmessage_json(botssys):
    return path_join(botssys, 'infile', 'unitinmessagejson')


@pytest.fixture(scope='module')
def unit_inmessage_xml(botssys):
    return path_join(botssys, 'infile', 'unitinmessagexml')


@pytest.fixture(scope='module')
def unit_inmessage_edifact(botssys):
    return path_join(botssys, 'infile', 'unitinmessageedifact')


@pytest.fixture(scope='module')
def inisout_init(general_init, unit_inisout, unit_inmessage_json, unit_inmessage_xml):  # @UnusedVariable
    shutil.rmtree(path_join(unit_inisout, 'output'), ignore_errors=True)  # remove whole output directory
    os.makedirs(path_join(unit_inisout, 'output'), exist_ok=True)
    shutil.rmtree(path_join(unit_inmessage_json, 'output'), ignore_errors=True)  # remove whole output directory
    os.makedirs(path_join(unit_inmessage_json, 'output'), exist_ok=True)
    shutil.rmtree(path_join(unit_inmessage_xml, 'output'), ignore_errors=True)  # remove whole output directory
    os.makedirs(path_join(unit_inmessage_xml, 'output'), exist_ok=True)


# Helper function to trigger botslib.MessageError because errors are "buffered" in InMessage classes. (parse_edi_file)
def parse_edi_file(*args, **kwargs):
    __tracebackhide__ = True
    edi = inmessage.parse_edi_file(*args, **kwargs)
    edi.checkforerrorlist()

    return edi


@pytest.mark.usefixtures('unit_inmessage_xml')
@pytest.mark.plugin_test
class TestInmessageXml:
    ''' Read messages; some should be OK (True), some should give errors (False).
        Tests per editype.
    '''
    def test_xml(self, unit_inmessage_xml):
        # empty file
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck', filename=path_join(unit_inmessage_xml, 'xml', '110401.xml'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxml', filename=path_join(unit_inmessage_xml, 'xml', '110401.xml'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxml', checkunknownentities=True, filename=path_join(unit_inmessage_xml, 'xml', '110401.xml'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxmlflatten', filename=path_join(unit_inmessage_xml, 'xml', '110401.xml'))

        # only root record in 110402.xml
        assert parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck', filename=path_join(unit_inmessage_xml, 'xml', '110402.xml')), 'only a root tag; should be OK'
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxml', filename=path_join(unit_inmessage_xml, 'xml', '110402.xml'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxml', checkunknownentities=True, filename=path_join(unit_inmessage_xml, 'xml', '110402.xml'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxmlflatten', filename=path_join(unit_inmessage_xml, 'xml', '110402.xml'))

        # root tag different from grammar
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxml', filename=path_join(unit_inmessage_xml, 'xml', '110406.xml'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxml', checkunknownentities=True, filename=path_join(unit_inmessage_xml, 'xml', '110406.xml'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxmlflatten', filename=path_join(unit_inmessage_xml, 'xml', '110406.xml'))

        # root tag is double
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck', filename=path_join(unit_inmessage_xml, 'xml', '110407.xml'))

        # invalid: no closing tag
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck', filename=path_join(unit_inmessage_xml, 'xml', '110408.xml'))

        # invalid: extra closing tag
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck', filename=path_join(unit_inmessage_xml, 'xml', '110409.xml'))

        # invalid: mandatory xml-element missing
        assert parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck', filename=path_join(unit_inmessage_xml, 'xml', '110410.xml'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxml', filename=path_join(unit_inmessage_xml, 'xml', '110410.xml'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxml', checkunknownentities=True, filename=path_join(unit_inmessage_xml, 'xml', '110410.xml'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxmlflatten', filename=path_join(unit_inmessage_xml, 'xml', '110410.xml'))

        # invalid: to many occurences
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxml', filename=path_join(unit_inmessage_xml, 'xml', '110411.xml'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxml', checkunknownentities=True, filename=path_join(unit_inmessage_xml, 'xml', '110411.xml'))

        # invalid: missing mandatory xml attribute
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxml', filename=path_join(unit_inmessage_xml, 'xml', '110412.xml'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxml', checkunknownentities=True, filename=path_join(unit_inmessage_xml, 'xml', '110412.xml'))

        # unknown xml element
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxml', checkunknownentities=True, filename=path_join(unit_inmessage_xml, 'xml', '110413.xml'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxml', checkunknownentities=True, filename=path_join(unit_inmessage_xml, 'xml', '110414.xml'))

        # 2x the same xml attribute
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxml', filename=path_join(unit_inmessage_xml, 'xml', '110415.xml'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='xml', messagetype='testxml', checkunknownentities=True, filename=path_join(unit_inmessage_xml, 'xml', '110415.xml'))

        # messages with all max occurences, use attributes, etc
        parse_edi_file(editype='xml', messagetype='testxml', filename=path_join(unit_inmessage_xml, 'xml', '110416.xml'))  # all elements, attributes

        # other order of xml elements; should esult in the same node tree
        in1 = parse_edi_file(editype='xml', messagetype='testxml', filename=path_join(unit_inmessage_xml, 'xml', '110417.xml'))  # as 18., other order of elements
        in2 = parse_edi_file(editype='xml', messagetype='testxml', filename=path_join(unit_inmessage_xml, 'xml', '110418.xml'))
        assert utilsunit.comparenode(in2.root, in1.root), 'compare'

        # ??what is tested here
        inn7 = parse_edi_file(editype='xml', messagetype='testxml', checkunknownentities=True, filename=path_join(unit_inmessage_xml, 'xml', '110405.xml'))  # with <?xml version="1.0" encoding="utf-8"?>
        inn8 = parse_edi_file(editype='xml', messagetype='testxmlflatten', checkunknownentities=True, filename=path_join(unit_inmessage_xml, 'xml', '110405.xml'))  # with <?xml version="1.0" encoding="utf-8"?>
        assert utilsunit.comparenode(inn7.root, inn8.root), 'compare'

        # test different file which should give equal results
        in1 = parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck', filename=path_join(unit_inmessage_xml, 'xml', '110403.xml'))  # no grammar used
        in5 = parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck', filename=path_join(unit_inmessage_xml, 'xml', '110404.xml'))  # no grammar used
        in6 = parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck', filename=path_join(unit_inmessage_xml, 'xml', '110405.xml'))  # no grammar used
        in2 = parse_edi_file(editype='xml', messagetype='testxml', filename=path_join(unit_inmessage_xml, 'xml', '110403.xml'))  # with <?xml version="1.0" encoding="utf-8"?>
        in3 = parse_edi_file(editype='xml', messagetype='testxml', filename=path_join(unit_inmessage_xml, 'xml', '110404.xml'))  # without <?xml version="1.0" encoding="utf-8"?>
        in4 = parse_edi_file(editype='xml', messagetype='testxml', filename=path_join(unit_inmessage_xml, 'xml', '110405.xml'))  # use cr/lf and whitespace for 'nice' xml
        assert utilsunit.comparenode(in2.root, in1.root), 'compare'
        assert utilsunit.comparenode(in2.root, in3.root), 'compare'
        assert utilsunit.comparenode(in2.root, in4.root), 'compare'
        assert utilsunit.comparenode(in2.root, in5.root), 'compare'
        assert utilsunit.comparenode(in2.root, in6.root), 'compare'

        # test different file which should give equal results; flattenxml=True,
        in1 = parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck', filename=path_join(unit_inmessage_xml, 'xml', '110403.xml'))  # no grammar used
        in5 = parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck', filename=path_join(unit_inmessage_xml, 'xml', '110404.xml'))  # no grammar used
        in6 = parse_edi_file(editype='xmlnocheck', messagetype='xmlnocheck', filename=path_join(unit_inmessage_xml, 'xml', '110405.xml'))  # no grammar used
        in4 = parse_edi_file(editype='xml', messagetype='testxmlflatten', filename=path_join(unit_inmessage_xml, 'xml', '110405.xml'))  # use cr/lf and whitespace for 'nice' xml
        in2 = parse_edi_file(editype='xml', messagetype='testxmlflatten', filename=path_join(unit_inmessage_xml, 'xml', '110403.xml'))  # with <?xml version="1.0" encoding="utf-8"?>
        in3 = parse_edi_file(editype='xml', messagetype='testxmlflatten', filename=path_join(unit_inmessage_xml, 'xml', '110404.xml'))  # without <?xml version="1.0" encoding="utf-8"?>
        assert utilsunit.comparenode(in2.root, in1.root), 'compare'
        assert utilsunit.comparenode(in2.root, in3.root), 'compare'
        assert utilsunit.comparenode(in2.root, in4.root), 'compare'
        assert utilsunit.comparenode(in2.root, in5.root), 'compare'
        assert utilsunit.comparenode(in2.root, in6.root), 'compare'


@pytest.mark.usefixtures('unit_inmessage_xml')
@pytest.mark.plugin_test
class TestinisoutXml:

    def test_xml01a(self, unit_inmessage_xml):
        ''' check  xml; new behaviour '''
        filenamein = path_join(unit_inmessage_xml, 'xml', 'inisout02.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout01a.xml')
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenamein, filenameout=filenameout)
        assert filecmp.cmp(filenameout, filenamein)

    def test_xml02a(self, unit_inmessage_xml):
        ''' check xmlnoccheck; new behaviour '''
        filenamein = path_join(unit_inmessage_xml, 'xml', 'inisout02.xml')
        filenametmp = path_join(unit_inmessage_xml, 'output', 'inisout02tmpa.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout02a.xml')
        utilsunit.readwrite(editype='xmlnocheck', messagetype='xmlnocheck', filenamein=filenamein, filenameout=filenametmp)
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenametmp, filenameout=filenameout)
        assert filecmp.cmp(filenameout, filenamein)

    def test_xml03(self, unit_inmessage_xml):
        ''' check  xml (different grammar) '''
        filenamein = path_join(unit_inmessage_xml, 'xml', '110419.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout03.xml')
        utilsunit.readwrite(editype='xml', messagetype='testxmlflatten', charset='utf-8', filenamein=filenamein, filenameout=filenameout)
        assert filecmp.cmp(filenamein, filenameout)

    def test_xml04(self, unit_inmessage_xml):
        ''' check xmlnoccheck '''
        filenamein = path_join(unit_inmessage_xml, 'xml', '110419.xml')
        filenametmp = path_join(unit_inmessage_xml, 'output', 'inisout04tmp.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout04.xml')
        utilsunit.readwrite(editype='xmlnocheck', messagetype='xmlnocheck', charset='utf-8', filenamein=filenamein, filenameout=filenametmp)
        utilsunit.readwrite(editype='xml', messagetype='testxmlflatten', charset='utf-8', filenamein=filenametmp, filenameout=filenameout)
        assert filecmp.cmp(filenamein, filenameout)

    def test_xml05(self, unit_inmessage_xml):
        ''' test xml;  iso-8859-1 '''
        filenamein = path_join(unit_inmessage_xml, 'xml', 'inisout03.xml')
        filenamecmp = path_join(unit_inmessage_xml, 'xml', 'inisoutcompare05.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout05.xml')
        utilsunit.readwrite(editype='xml', messagetype='testxml', filenamein=filenamein, filenameout=filenameout, charset='ISO-8859-1')
        assert filecmp.cmp(filenameout, filenamecmp)

    def test_xml06(self, unit_inmessage_xml):
        ''' test xmlnocheck; iso-8859-1 '''
        filenamein = path_join(unit_inmessage_xml, 'xml', 'inisout03.xml')
        filenametmp = path_join(unit_inmessage_xml, 'output', 'inisout05tmp.xml')
        filenamecmp = path_join(unit_inmessage_xml, 'xml', 'inisoutcompare05.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout05a.xml')
        utilsunit.readwrite(editype='xmlnocheck', messagetype='xmlnocheck', filenamein=filenamein, filenameout=filenametmp, charset='ISO-8859-1')
        utilsunit.readwrite(editype='xml', messagetype='testxml', filenamein=filenametmp, filenameout=filenameout, charset='ISO-8859-1')
        assert filecmp.cmp(filenameout, filenamecmp)

    def test_xml09(self, unit_inmessage_xml):
        ''' BOM;; BOM is not written.... '''
        filenamein = path_join(unit_inmessage_xml, 'xml', 'inisout05.xml')
        filenamecmp = path_join(unit_inmessage_xml, 'xml', 'inisout04.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout09.xml')
        utilsunit.readwrite(editype='xml', messagetype='testxml', filenamein=filenamein, filenameout=filenameout, charset='utf-8')
        assert filecmp.cmp(filenameout, filenamecmp)

    def test_xml10(self, unit_inmessage_xml):
        ''' BOM;; BOM is not written.... '''
        filenamein = path_join(unit_inmessage_xml, 'xml', 'inisout05.xml')
        filenametmp = path_join(unit_inmessage_xml, 'output', 'inisout10tmp.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout10.xml')
        filenamecmp = path_join(unit_inmessage_xml, 'xml', 'inisout04.xml')
        utilsunit.readwrite(editype='xmlnocheck', messagetype='xmlnocheck', filenamein=filenamein, filenameout=filenametmp)
        utilsunit.readwrite(editype='xml', messagetype='testxml', filenamein=filenametmp, filenameout=filenameout, charset='utf-8')
        assert filecmp.cmp(filenameout, filenamecmp)

    def test_xml11(self, unit_inmessage_xml):
        ''' check  xml; new behaviour; use standalone parameter '''
        filenamein = path_join(unit_inmessage_xml, 'xml', 'inisout06.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout11.xml')
        filenamecmp = path_join(unit_inmessage_xml, 'xml', 'inisout02.xml')
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenamein, filenameout=filenameout, standalone=None)
        assert filecmp.cmp(filenameout, filenamecmp)

    def test_xml11a(self, unit_inmessage_xml):
        ''' check  xml; new behaviour; use standalone parameter '''
        filenamein = path_join(unit_inmessage_xml, 'xml', 'inisout06.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout11a.xml')
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenamein, filenameout=filenameout, standalone='no')
        assert filecmp.cmp(filenameout, filenamein)

    def test_xml12(self, unit_inmessage_xml):
        ''' check xmlnoccheck; new behaviour use standalone parameter '''
        filenamein = path_join(unit_inmessage_xml, 'xml', 'inisout06.xml')
        filenametmp = path_join(unit_inmessage_xml, 'output', 'inisout12tmp.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout12.xml')
        utilsunit.readwrite(editype='xmlnocheck', messagetype='xmlnocheck', filenamein=filenamein, filenameout=filenametmp, standalone='no')
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenametmp, filenameout=filenameout, standalone='no')
        assert filecmp.cmp(filenameout, filenamein)

    def test_xml13(self, unit_inmessage_xml):
        ''' check  xml; read doctype&write doctype '''
        filenamein = path_join(unit_inmessage_xml, 'xml', 'inisout13.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout13.xml')
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenamein, filenameout=filenameout, DOCTYPE='mydoctype SYSTEM "mydoctype.dtd"')
        assert filecmp.cmp(filenameout, filenamein)

    def test_xml14(self, unit_inmessage_xml):
        ''' check xmlnoccheck;  read doctype&write doctype '''
        filenamein = path_join(unit_inmessage_xml, 'xml', 'inisout13.xml')
        filenametmp = path_join(unit_inmessage_xml, 'output', 'inisout14tmp.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout14.xml')
        utilsunit.readwrite(editype='xmlnocheck', messagetype='xmlnocheck', filenamein=filenamein, filenameout=filenametmp, DOCTYPE='mydoctype SYSTEM "mydoctype.dtd"')
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenametmp, filenameout=filenameout, DOCTYPE='mydoctype SYSTEM "mydoctype.dtd"')
        assert filecmp.cmp(filenameout, filenamein)

    def test_xml15(self, unit_inmessage_xml):
        ''' check  xml; read processing_instructions&write processing_instructions '''
        filenamein = path_join(unit_inmessage_xml, 'xml', 'inisout15.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout15.xml')
        utilsunit.readwrite(
            editype='xml',
            messagetype='xmlorder',
            filenamein=filenamein,
            filenameout=filenameout,
            processing_instructions=[
                ('xml-stylesheet', 'href="mystylesheet.xsl" type="text/xml"'),
                ('type-of-ppi', 'attr1="value1" attr2="value2"')
            ]
        )
        assert filecmp.cmp(filenameout, filenamein)

    def test_xml16(self, unit_inmessage_xml):
        ''' check xmlnoccheck;  read processing_instructions&write processing_instructions '''
        filenamein = path_join(unit_inmessage_xml, 'xml', 'inisout15.xml')
        filenametmp = path_join(unit_inmessage_xml, 'output', 'inisout16tmp.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout16.xml')
        utilsunit.readwrite(
            editype='xmlnocheck',
            messagetype='xmlnocheck',
            filenamein=filenamein,
            filenameout=filenametmp,
            processing_instructions=[
                ('xml-stylesheet', 'href="mystylesheet.xsl" type="text/xml"'),
                ('type-of-ppi', 'attr1="value1" attr2="value2"')
            ]
        )
        utilsunit.readwrite(
            editype='xml',
            messagetype='xmlorder',
            filenamein=filenametmp,
            filenameout=filenameout,
            processing_instructions=[
                ('xml-stylesheet', 'href="mystylesheet.xsl" type="text/xml"'),
                ('type-of-ppi', 'attr1="value1" attr2="value2"')
            ]
        )
        assert filecmp.cmp(filenameout, filenamein)

    def test_xml17(self, unit_inmessage_xml):
        ''' check  xml; read processing_instructions&doctype&comments. Do not write these. '''
        filenamein = path_join(unit_inmessage_xml, 'xml', 'inisout17.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout17.xml')
        filenamecmp = path_join(unit_inmessage_xml, 'xml', 'inisout02.xml')
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenamein, filenameout=filenameout)
        assert filecmp.cmp(filenameout, filenamecmp)

    def test_xml18(self, unit_inmessage_xml):
        ''' check  xml; read processing_instructions&doctype&comments. Do not write these. '''
        filenamein = path_join(unit_inmessage_xml, 'xml', 'inisout17.xml')
        filenametmp = path_join(unit_inmessage_xml, 'output', 'inisout18tmp.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout18.xml')
        filenamecmp = path_join(unit_inmessage_xml, 'xml', 'inisout02.xml')
        utilsunit.readwrite(editype='xmlnocheck', messagetype='xmlnocheck', filenamein=filenamein, filenameout=filenametmp)
        utilsunit.readwrite(editype='xml', messagetype='xmlorder', filenamein=filenametmp, filenameout=filenameout)
        assert filecmp.cmp(filenameout, filenamecmp)

    def test_xml19(self, unit_inmessage_xml):
        ''' check  xml; indented; use lot of options. '''
        filenamein = path_join(unit_inmessage_xml, 'xml', 'inisout02.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout19.xml')
        filenamecmp = path_join(unit_inmessage_xml, 'xml', 'inisout19.xml')
        utilsunit.readwrite(
            editype='xml',
            messagetype='xmlorder',
            filenamein=filenamein,
            filenameout=filenameout,
            indented=True,
            standalone='yes',
            DOCTYPE='mydoctype SYSTEM "mydoctype.dtd"',
            processing_instructions=[
                ('xml-stylesheet', 'href="mystylesheet.xsl" type="text/xml"'),
                ('type-of-ppi', 'attr1="value1" attr2="value2"')
            ]
        )
        assert filecmp.cmp(filenameout, filenamecmp)

    def test_xml20(self, unit_inmessage_xml):
        ''' check  xml; indented; use lot of options. '''
        filenamein = path_join(unit_inmessage_xml, 'xml', 'inisout02.xml')
        filenametmp = path_join(unit_inmessage_xml, 'output', 'inisout20tmp.xml')
        filenameout = path_join(unit_inmessage_xml, 'output', 'inisout20.xml')
        filenamecmp = path_join(unit_inmessage_xml, 'xml', 'inisout19.xml')
        utilsunit.readwrite(
            editype='xmlnocheck',
            messagetype='xmlnocheck',
            filenamein=filenamein,
            filenameout=filenametmp,
            indented=True,
            standalone='yes',
            DOCTYPE='mydoctype SYSTEM "mydoctype.dtd"',
            processing_instructions=[
                ('xml-stylesheet', 'href="mystylesheet.xsl" type="text/xml"'),
                ('type-of-ppi', 'attr1="value1" attr2="value2"')
            ]
        )
        utilsunit.readwrite(
            editype='xml',
            messagetype='xmlorder',
            filenamein=filenametmp,
            filenameout=filenameout,
            indented=True,
            standalone='yes',
            DOCTYPE='mydoctype SYSTEM "mydoctype.dtd"',
            processing_instructions=[
                ('xml-stylesheet', 'href="mystylesheet.xsl" type="text/xml"'),
                ('type-of-ppi', 'attr1="value1" attr2="value2"')
            ]
        )
        assert filecmp.cmp(filenameout, filenamecmp)


@pytest.mark.usefixtures('unit_inmessage_json')
@pytest.mark.plugin_test
class TestInmessageJson:
    # ***********************************************************************
    # ****** test json eg list of article (as eg used in database comm ******
    # ***********************************************************************
    def test_json01(self, unit_inmessage_json):
        filein = path_join(unit_inmessage_json, 'org', '01.jsn')
        filecomp = path_join(unit_inmessage_json, 'comp', '01.xml')
        inn1 = parse_edi_file(filename=filein, editype='json', messagetype='articles')
        inn2 = parse_edi_file(filename=filecomp, editype='xml', messagetype='articles')
        assert utilsunit.comparenode(inn1.root, inn2.root)

    def test_json01_nocheck(self, unit_inmessage_json):
        filein = path_join(unit_inmessage_json, 'org', '01.jsn')
        filecomp = path_join(unit_inmessage_json, 'comp', '01.xml')
        inn1 = parse_edi_file(filename=filein, editype='jsonnocheck', messagetype='articles')
        inn2 = parse_edi_file(filename=filecomp, editype='xml', messagetype='articles')
        assert utilsunit.comparenode(inn1.root, inn2.root)

    def test_json11(self, unit_inmessage_json):
        filein = path_join(unit_inmessage_json, 'org', '11.jsn')
        filecomp = path_join(unit_inmessage_json, 'comp', '01.xml')
        inn1 = parse_edi_file(filename=filein, editype='json', messagetype='articles')
        inn2 = parse_edi_file(filename=filecomp, editype='xml', messagetype='articles')
        assert utilsunit.comparenode(inn1.root, inn2.root)

    def test_json11_nocheck(self, unit_inmessage_json):
        filein = path_join(unit_inmessage_json, 'org', '11.jsn')
        filecomp = path_join(unit_inmessage_json, 'comp', '01.xml')
        inn1 = parse_edi_file(filename=filein, editype='jsonnocheck', messagetype='articles')
        inn2 = parse_edi_file(filename=filecomp, editype='xml', messagetype='articles')
        assert utilsunit.comparenode(inn1.root, inn2.root)

    # ***********************************************************************
    # *********json incoming tests complex structure*************************
    # ***********************************************************************
    def test_json_invoic01(self, unit_inmessage_json):
        filein = path_join(unit_inmessage_json, 'org', 'invoic01.jsn')
        filecomp = path_join(unit_inmessage_json, 'comp', 'invoic01.xml')
        inn1 = parse_edi_file(filename=filein, editype='json', messagetype='invoic')
        inn2 = parse_edi_file(filename=filecomp, editype='xml', messagetype='invoic')
        assert utilsunit.comparenode(inn1.root, inn2.root)

    def test_json_invoic01_nocheck(self, unit_inmessage_json):
        filein = path_join(unit_inmessage_json, 'org', 'invoic01.jsn')
        filecomp = path_join(unit_inmessage_json, 'comp', 'invoic01.xml')
        inn1 = parse_edi_file(filename=filein, editype='jsonnocheck', messagetype='invoic')
        inn2 = parse_edi_file(filename=filecomp, editype='xml', messagetype='invoic')
        assert utilsunit.comparenode(inn1.root, inn2.root)

    def test_json_invoic02(self, unit_inmessage_json):
        ''' check  01.xml the same after read & write/check '''
        filein = path_join(unit_inmessage_json, 'org', 'invoic02.jsn')
        filecomp = path_join(unit_inmessage_json, 'comp', 'invoic01.xml')
        inn1 = parse_edi_file(filename=filein, editype='json', messagetype='invoic')
        inn2 = parse_edi_file(filename=filecomp, editype='xml', messagetype='invoic')
        assert utilsunit.comparenode(inn1.root, inn2.root)

    def test_json_invoic02_nocheck(self, unit_inmessage_json):
        ''' check  01.xml the same after read & write/check '''
        filein = path_join(unit_inmessage_json, 'org', 'invoic02.jsn')
        filecomp = path_join(unit_inmessage_json, 'comp', 'invoic01.xml')
        inn1 = parse_edi_file(filename=filein, editype='jsonnocheck', messagetype='invoic')
        inn2 = parse_edi_file(filename=filecomp, editype='xml', messagetype='invoic')
        assert utilsunit.comparenode(inn1.root, inn2.root)

    # ***********************************************************************
    # *********json incoming tests int,float*********************************
    # ***********************************************************************
    def test_json_invoic03(self, unit_inmessage_json):
        ''' test int, float in json '''
        filein = path_join(unit_inmessage_json, 'org', 'invoic03.jsn')
        filecomp = path_join(unit_inmessage_json, 'comp', 'invoic02.xml')
        inn1 = parse_edi_file(filename=filein, editype='json', messagetype='invoic')
        inn2 = parse_edi_file(filename=filecomp, editype='xml', messagetype='invoic')
        assert utilsunit.comparenode(inn1.root, inn2.root)

    def test_json_invoic03_xml_nocheck(self, unit_inmessage_json):
        ''' test int, float in json '''
        filein = path_join(unit_inmessage_json, 'org', 'invoic03.jsn')
        filecomp = path_join(unit_inmessage_json, 'comp', 'invoic02.xml')
        inn1 = parse_edi_file(filename=filein, editype='json', messagetype='invoic')
        inn2 = parse_edi_file(filename=filecomp, editype='xmlnocheck', messagetype='invoic')
        assert utilsunit.comparenode(inn1.root, inn2.root)

    def test_json_invoic03_nocheck(self, unit_inmessage_json):
        ''' test int, float in json '''
        filein = path_join(unit_inmessage_json, 'org', 'invoic03.jsn')
        filecomp = path_join(unit_inmessage_json, 'comp', 'invoic02.xml')
        inn1 = parse_edi_file(filename=filein, editype='jsonnocheck', messagetype='invoic')
        inn2 = parse_edi_file(filename=filecomp, editype='xml', messagetype='invoic')
        assert utilsunit.comparenode(inn1.root, inn2.root)

    def test_json_invoic03_nocheck_xml_nocheck(self, unit_inmessage_json):
        ''' test int, float in json '''
        filein = path_join(unit_inmessage_json, 'org', 'invoic03.jsn')
        filecomp = path_join(unit_inmessage_json, 'comp', 'invoic02.xml')
        inn1 = parse_edi_file(filename=filein, editype='jsonnocheck', messagetype='invoic')
        inn2 = parse_edi_file(filename=filecomp, editype='xmlnocheck', messagetype='invoic')
        assert utilsunit.comparenode(inn1.root, inn2.root)

    def test_json_div(self, unit_inmessage_json):
        assert parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=True, filename=path_join(unit_inmessage_json, 'org', '130101.json')), 'standaard test'
        assert parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck', filename=path_join(unit_inmessage_json, 'org', '130101.json')), 'standaard test'

        # empty object
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=True, filename=path_join(unit_inmessage_json, 'org', '130102.json'))

        # unknown field
        assert parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=False, filename=path_join(unit_inmessage_json, 'org', '130103.json')), 'unknown field'
        assert parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck', filename=path_join(unit_inmessage_json, 'org', '130103.json')), 'unknown field'
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=True, filename=path_join(unit_inmessage_json, 'org', '130103.json'))  # unknown field

        # compare standard test with standard est with extra unknown fields and objects: must give same tree:
        in1 = parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=True, filename=path_join(unit_inmessage_json, 'org', '130101.json'))
        in2 = parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=False, filename=path_join(unit_inmessage_json, 'org', '130115.json'))
        assert utilsunit.comparenode(in1.root, in2.root), 'compare'

        # numeriek field
        assert parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=False, filename=path_join(unit_inmessage_json, 'org', '130104.json')), 'numeriek field'
        assert parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck', checkunknownentities=False, filename=path_join(unit_inmessage_json, 'org', '130104.json')), 'numeriek field'
        assert parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=True, filename=path_join(unit_inmessage_json, 'org', '130104.json')), 'numeriek field'

        assert parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=False, filename=path_join(unit_inmessage_json, 'org', '130105.json')), 'fucked up'
        assert parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck', filename=path_join(unit_inmessage_json, 'org', '130105.json')), 'fucked up'
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=True, filename=path_join(unit_inmessage_json, 'org', '130105.json'))  # fucked up

        assert parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=False, filename=path_join(unit_inmessage_json, 'org', '130106.json')), 'fucked up'
        assert parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck', filename=path_join(unit_inmessage_json, 'org', '130106.json')), 'fucked up'
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=True, filename=path_join(unit_inmessage_json, 'org', '130106.json'))  # fucked up

        assert parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=False, filename=path_join(unit_inmessage_json, 'org', '130107.json')), 'fucked up'
        assert parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck', filename=path_join(unit_inmessage_json, 'org', '130107.json')), 'fucked up'
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=True, filename=path_join(unit_inmessage_json, 'org', '130107.json'))  # fucked up

        # root is list with 3 messagetrees
        inn = parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=False, filename=path_join(unit_inmessage_json, 'org', '130108.json'))
        assert len(inn.root.children) == 3, 'should deliver 3 messagetrees'
        inn = parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck', filename=path_join(unit_inmessage_json, 'org', '130108.json'))
        assert len(inn.root.children) == 3, 'should deliver 3 messagetrees'

        # root is list, but list has a non-object member
        assert parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=False, filename=path_join(unit_inmessage_json, 'org', '130109.json')), 'root is list, but list has a non-object member'
        assert parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck', filename=path_join(unit_inmessage_json, 'org', '130109.json')), 'root is list, but list has a non-object member'
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=True, filename=path_join(unit_inmessage_json, 'org', '130109.json'))  # root is list, but list has a non-object member

        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=False, filename=path_join(unit_inmessage_json, 'org', '130110.json'))  # too many occurences

        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=False, filename=path_join(unit_inmessage_json, 'org', '130111.json'))  # ent TEST1 should have a TEST2
        assert parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck', filename=path_join(unit_inmessage_json, 'org', '130111.json')), 'ent TEST1 should have a TEST2'
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=True, filename=path_join(unit_inmessage_json, 'org', '130111.json'))  # ent TEST1 should have a TEST2

        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=False, filename=path_join(unit_inmessage_json, 'org', '130112.json'))  # ent TEST1 has a TEST2
        assert parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck', filename=path_join(unit_inmessage_json, 'org', '130112.json')), 'ent TEST1 has a TEST2'
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=True, filename=path_join(unit_inmessage_json, 'org', '130112.json'))  # ent TEST1 has a TEST2

        # unknown entries
        inn = parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=False, filename=path_join(unit_inmessage_json, 'org', '130113.json'))

        # empty file
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=False, filename=path_join(unit_inmessage_json, 'org', '130114.json'))  # empty file
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='jsonnocheck', messagetype='jsonnocheck', filename=path_join(unit_inmessage_json, 'org', '130114.json'))  # empty file

        # numeric key
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=False, filename=path_join(unit_inmessage_json, 'org', '130116.json'))

        # key is list
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='json', messagetype='testjsonorder01', checkunknownentities=False, filename=path_join(unit_inmessage_json, 'org', '130117.json'))

    def test_inisout_json01(self, unit_inmessage_json):
        filein = path_join(unit_inmessage_json, 'org', 'inisout01.json')
        fileout1 = path_join(unit_inmessage_json, 'output', 'inisout01.json')
        fileout3 = path_join(unit_inmessage_json, 'output', 'inisout03.json')
        utilsunit.readwrite(editype='json', messagetype='jsonorder', filenamein=filein, filenameout=fileout1)
        utilsunit.readwrite(editype='jsonnocheck', messagetype='jsonnocheck', filenamein=filein, filenameout=fileout3)
        inn1 = parse_edi_file(filename=fileout1, editype='jsonnocheck', messagetype='jsonnocheck')
        inn2 = parse_edi_file(filename=fileout3, editype='jsonnocheck', messagetype='jsonnocheck')
        assert utilsunit.comparenode(inn1.root, inn2.root)

    def test_inisout_json02(self, unit_inmessage_json):
        # fails. this is because list of messages is read; and these are written in one time....nice for next release...
        filein = path_join(unit_inmessage_json, 'org', 'inisout05.json')
        fileout = path_join(unit_inmessage_json, 'output', 'inisout05.json')
        inn = parse_edi_file(editype='json', messagetype='jsoninvoic', filename=filein)
        out = outmessage.outmessage_init(editype='json', messagetype='jsoninvoic', filename=fileout, divtext='', topartner='')  # make outmessage object
        inn.root.display()
        out.root = inn.root
        out.writeall()

        inn1 = parse_edi_file(filename=filein, editype='jsonnocheck', messagetype='jsonnocheck', defaultBOTSIDroot='HEA')
        inn2 = parse_edi_file(filename=fileout, editype='jsonnocheck', messagetype='jsonnocheck')
        inn1.root.display()
        inn2.root.display()
        assert utilsunit.comparenode(inn1.root, inn2.root)

        rawfile1 = utilsunit.readfile(filein)
        rawfile2 = utilsunit.readfile(fileout)
        jsonobject1 = simplejson.loads(rawfile1)
        jsonobject2 = simplejson.loads(rawfile2)
        assert jsonobject1 == jsonobject2, 'CmpJson'

    def test_inisout_json03(self, unit_inmessage_json):
        ''' non-ascii-char '''
        filein = path_join(unit_inmessage_json, 'org', 'inisout04.json')
        fileout = path_join(unit_inmessage_json, 'output', 'inisout04.json')
        utilsunit.readwrite(editype='json', messagetype='jsonorder', filenamein=filein, filenameout=fileout)
        inn1 = parse_edi_file(filename=filein, editype='jsonnocheck', messagetype='jsonnocheck')
        inn2 = parse_edi_file(filename=fileout, editype='jsonnocheck', messagetype='jsonnocheck')
        assert utilsunit.comparenode(inn1.root, inn2.root)

    def test_inisout_json04(self, unit_inmessage_json):
        filein = path_join(unit_inmessage_json, 'org', 'inisout05.json')
        inn1 = parse_edi_file(filename=filein, editype='jsonnocheck', messagetype='jsonnocheck', defaultBOTSIDroot='HEA')
        inn2 = parse_edi_file(filename=filein, editype='json', messagetype='jsoninvoic')
        assert utilsunit.comparenode(inn1.root, inn2.root)


@pytest.mark.usefixtures('unit_inmessage_edifact')
@pytest.mark.plugin_test
class TestInmessage:

    def test_edifact_0401(self, unit_inmessage_edifact):
        ''' 0401 Errors in records '''
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0401', '040101.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0401', '040102.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0401', '040103.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0401', '040104.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0401', '040105.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0401', '040106.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0401', '040107.edi'))

    def test_edifact_0403(self, unit_inmessage_edifact):
        # test charsets
        # with pytest.raises(botslib.MessageError):
        #     parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0403', '040301.edi'))  # UNOA-regular OK for UNOA as UNOC
        # with pytest.raises(botslib.MessageError):
        #     parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0403', '040302F-generated.edi'))  # UNOA-regular  OK for UNOA as UNOC
        in0 = parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0403', '040303.edi'))  # UNOA-regular also UNOA-strict @UnusedVariable
        in1 = parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0403', '040306.edi'))  # UNOA regular
        in2 = parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0403', 'T0000000005.edi'))  # UNOA regular
        in3 = parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0403', 'T0000000006.edi'))  # UNOA regular
        for in1node, in2node, in3node in zip(in1.nextmessage(), in2.nextmessage(), in3.nextmessage()):
            assert utilsunit.comparenode(in1node.root, in2node.root), 'compare'
            assert utilsunit.comparenode(in1node.root, in3node.root), 'compare'

        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0403', '040305.edi'))  # needs UNOA regular
        # in1 = parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0403', '040305.edi'))  # needs UNOA extended; add (and delete later)
        in7 = parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0403', '040304.edi'))   # UNOB-regular @UnusedVariable
        in5 = parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0403', 'T0000000008.edi'))  # UNOB regular @UnusedVariable
        in4 = parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0403', 'T0000000007-generated.edi'))  # UNOB regular @UnusedVariable
        in6 = parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0403', 'T0000000009.edi'))  # UNOC @UnusedVariable

    def test_edifact_0404(self, unit_inmessage_edifact):
        # envelope tests
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040401.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040402.edi'))
        assert parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040403.edi')), 'standaard test'
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040404.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040405.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040406.edi'))
        # with pytest.raises(botslib.InMessageError):
        #     parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040407.edi'))  # syntax version '0'; is not checked anymore
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040408.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040409.edi'))
        assert parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040410.edi')), 'standaard test'
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040411.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040412.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040413.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040414.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040415.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040416.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040417.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0404', '040418.edi'))

    def test_edifact_0407(self, unit_inmessage_edifact):
        # lex test with characters in strange places
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0407', '040701.edi'))

        assert parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0407', '040702.edi')), 'standaard test'

        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0407', '040703.edi'))
        with pytest.raises(botslib.MessageError):
            parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0407', '040704.edi'))

        assert parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0407', '040705.edi')), 'standaard test'
        assert parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0407', '040706.edi')), 'UNOA Crtl-Z at end'
        assert parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0407', '040707.edi')), 'UNOB Crtl-Z at end'
        assert parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0407', '040708.edi')), 'UNOC Crtl-Z at end'

    def test_edifact_0408(self, unit_inmessage_edifact):
        # differentenvelopingsamecontent: 1rst UNH per UNB, 2nd has 2 UNB for all UNH's, 3rd has UNG-UNE
        in1 = parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0408', '040801.edi'))
        in2 = parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0408', '040802.edi'))
        in3 = parse_edi_file(editype='edifact', messagetype='edifact', filename=path_join(unit_inmessage_edifact, '0408', '040803.edi'))
        for in1node, in2node, in3node in zip(in1.nextmessage(), in2.nextmessage(), in3.nextmessage()):
            assert utilsunit.comparenode(in1node.root, in2node.root), 'compare'
            assert utilsunit.comparenode(in1node.root, in3node.root), 'compare'


@pytest.mark.usefixtures('unit_inisout')
@pytest.mark.plugin_test
class TestinisoutEdifact:

    def test_edifact02(self, unit_inisout):
        infile = path_join(unit_inisout, 'org', 'inisout02.edi')
        outfile = path_join(unit_inisout, 'output', 'inisout02.edi')
        inn = parse_edi_file(editype='edifact', messagetype='orderswithenvelope', filename=infile)
        out = outmessage.outmessage_init(editype='edifact', messagetype='orderswithenvelope', filename=outfile, divtext='', topartner='')  # make outmessage object
        out.root = inn.root
        out.writeall()
        assert filecmp.cmp(outfile, infile)

    def test_edifact03(self, unit_inisout):
        # takes quite long
        infile = path_join(unit_inisout, 'org', 'inisout03.edi')
        outfile = path_join(unit_inisout, 'output', 'inisout03.edi')
        inn = parse_edi_file(editype='edifact', messagetype='invoicwithenvelope', filename=infile)
        out = outmessage.outmessage_init(editype='edifact', messagetype='invoicwithenvelope', filename=outfile, divtext='', topartner='')  # make outmessage object
        out.root = inn.root
        out.writeall()
        assert filecmp.cmp(outfile, infile)

    def test_edifact04(self, unit_inisout):
        utilsunit.readwrite(
            editype='edifact',
            messagetype='orderswithenvelope',
            filenamein=path_join(unit_inisout, '0406edifact', '040601.edi'),
            filenameout=path_join(unit_inisout, 'output', '040601.edi')
        )
        utilsunit.readwrite(
            editype='edifact',
            messagetype='orderswithenvelope',
            filenamein=path_join(unit_inisout, '0406edifact', '040602.edi'),
            filenameout=path_join(unit_inisout, 'output', '040602.edi')
        )
        utilsunit.readwrite(
            editype='edifact',
            messagetype='orderswithenvelope',
            filenamein=path_join(unit_inisout, '0406edifact', '040603.edi'),
            filenameout=path_join(unit_inisout, 'output', '040603.edi')
        )
        utilsunit.readwrite(
            editype='edifact',
            messagetype='orderswithenvelope',
            filenamein=path_join(unit_inisout, '0406edifact', '040604.edi'),
            filenameout=path_join(unit_inisout, 'output', '040604.edi')
        )
        utilsunit.readwrite(
            editype='edifact',
            messagetype='orderswithenvelope',
            filenamein=path_join(unit_inisout, '0406edifact', '040605.edi'),
            filenameout=path_join(unit_inisout, 'output', '040605.edi')
        )
        utilsunit.readwrite(
            editype='edifact',
            messagetype='orderswithenvelope',
            filenamein=path_join(unit_inisout, '0406edifact', '040606.edi'),
            filenameout=path_join(unit_inisout, 'output', '040606.edi')
        )
        utilsunit.readwrite(
            editype='edifact',
            messagetype='orderswithenvelope',
            filenamein=path_join(unit_inisout, '0406edifact', '040607.edi'),
            filenameout=path_join(unit_inisout, 'output', '040607.edi')
        )
        utilsunit.readwrite(
            editype='edifact',
            messagetype='orderswithenvelope',
            filenamein=path_join(unit_inisout, '0406edifact', '040608.edi'),
            filenameout=path_join(unit_inisout, 'output', '040608.edi')
        )
        assert filecmp.cmp(path_join(unit_inisout, 'output', '040601.edi'), path_join(unit_inisout, 'output', '040602.edi'))
        assert filecmp.cmp(path_join(unit_inisout, 'output', '040601.edi'), path_join(unit_inisout, 'output', '040603.edi'))
        assert filecmp.cmp(path_join(unit_inisout, 'output', '040601.edi'), path_join(unit_inisout, 'output', '040604.edi'))
        assert filecmp.cmp(path_join(unit_inisout, 'output', '040601.edi'), path_join(unit_inisout, 'output', '040605.edi'))
        assert filecmp.cmp(path_join(unit_inisout, 'output', '040601.edi'), path_join(unit_inisout, 'output', '040606.edi'))
        assert filecmp.cmp(path_join(unit_inisout, 'output', '040601.edi'), path_join(unit_inisout, 'output', '040607.edi'))
        assert filecmp.cmp(path_join(unit_inisout, 'output', '040601.edi'), path_join(unit_inisout, 'output', '040608.edi'))


@pytest.mark.usefixtures('unit_inisout')
@pytest.mark.plugin_test
class TestinisoutInh:

    def test_inh01(self, unit_inisout):
        filenamein = path_join(unit_inisout, 'org', 'inisout01.inh')
        filenameout = path_join(unit_inisout, 'output', 'inisout01.inh')
        inn = parse_edi_file(editype='fixed', messagetype='invoicfixed', filename=filenamein)
        out = outmessage.outmessage_init(editype='fixed', messagetype='invoicfixed', filename=filenameout, divtext='', topartner='KCS0004')  # make outmessage object
        out.root = inn.root
        out.writeall()
        assert filecmp.cmp(filenameout, filenamein)

    def test_idoc01(self, unit_inisout):
        filenamein = path_join(unit_inisout, 'org', 'inisout01.idoc')
        filenameout = path_join(unit_inisout, 'output', 'inisout01.idoc')
        inn = parse_edi_file(editype='idoc', messagetype='WP_PLU02', filename=filenamein)
        out = outmessage.outmessage_init(editype='idoc', messagetype='WP_PLU02', filename=filenameout, divtext='', topartner='')  # make outmessage object
        out.root = inn.root
        out.writeall()
        assert filecmp.cmp(filenameout, filenamein)


@pytest.mark.usefixtures('unit_inisout')
@pytest.mark.plugin_test
class TestinisoutX12:

    def test_x12_01(self, unit_inisout):
        filenamein = path_join(unit_inisout, 'org', 'inisout01.x12')
        filenameout = path_join(unit_inisout, 'output', 'inisout01.x12')
        inn = parse_edi_file(editype='x12', messagetype='850withenvelope', filename=filenamein)
        assert inn.ta_info['frompartner'] == '11111111111', 'ISA partner without spaces'
        assert inn.ta_info['topartner'] == '22222222222', 'ISA partner without spaces'
        out = outmessage.outmessage_init(editype='x12', messagetype='850withenvelope', filename=filenameout, divtext='', topartner='')  # make outmessage object
        out.root = inn.root
        out.writeall()
        linesfile1 = utilsunit.readfilelines(filenamein)
        linesfile2 = utilsunit.readfilelines(filenameout)
        assert linesfile1[0][:103] == linesfile2[0][:103], 'first part of ISA'
        for line1, line2 in zip(linesfile1[1:], linesfile2[1:]):
            assert line1 == line2, 'Cmplines'

    def test_x12_02(self, unit_inisout):
        filenamein = path_join(unit_inisout, 'org', 'inisout02.x12')
        filenameout = path_join(unit_inisout, 'output', 'inisout02.x12')
        inn = parse_edi_file(editype='x12', messagetype='850withenvelope', filename=filenamein)
        out = outmessage.outmessage_init(add_crlfafterrecord_sep='', editype='x12', messagetype='850withenvelope', filename=filenameout, divtext='', topartner='')  # make outmessage object
        out.root = inn.root
        out.writeall()
        linesfile1 = utilsunit.readfile(filenamein)
        linesfile2 = utilsunit.readfile(filenameout)
        assert linesfile1[:103] == linesfile2[:103], 'first part of ISA'
        assert linesfile1[105:] == linesfile2[103:], 'rest of message'


@pytest.mark.usefixtures('unit_inisout')
@pytest.mark.plugin_test
class TestinisoutCsv:

    def test_csv001(self, unit_inisout):
        filenamein = path_join(unit_inisout, 'org', 'inisout01.csv')
        filenameout = path_join(unit_inisout, 'output', 'inisout01.csv')
        utilsunit.readwrite(editype='csv', messagetype='invoic', filenamein=filenamein, filenameout=filenameout)
        assert filecmp.cmp(filenameout, filenamein)

    def test_csv003(self, unit_inisout):
        # utf-charset
        filenamein = path_join(unit_inisout, 'org', 'inisout03.csv')
        filenameout = path_join(unit_inisout, 'output', 'inisout03.csv')
        utilsunit.readwrite(editype='csv', messagetype='invoic', filenamein=filenamein, filenameout=filenameout)
        assert filecmp.cmp(filenameout, filenamein)

    def test_csv004(self, unit_inisout):
        # utf-charset with BOM **error. BOM is not removed by python.
        filenamein = path_join(unit_inisout, 'org', 'inisout04.csv'),
        filenameout = path_join(unit_inisout, 'output', 'inisout04.csv')
        utilsunit.readwrite(editype='csv', messagetype='invoic', filenamein=filenamein, filenameout=filenameout)
        assert filecmp.cmp(filenameout, filenamein)
