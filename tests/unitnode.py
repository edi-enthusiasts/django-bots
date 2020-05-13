# -*- coding: utf-8 -*-

import os
import shutil
import pytest
import bots.inmessage as inmessage
import bots.outmessage as outmessage
import bots.botslib as botslib
import bots.node as node

from os.path import join as path_join

'''
plugin unitnode.zip
not an acceptance test
does not work with get_checklevel=2
'''

# fetchqueries is dynamically added to node, to retrieve and check
collectqueries = {}
pytestmark = pytest.mark.usefixtures('engine_logging', 'node_init')


@pytest.fixture(scope='module')
def unit_node(botssys):
    return path_join(botssys, 'infile', 'unitnode')


@pytest.fixture(scope='module')
def node_init(unit_node):
    shutil.rmtree(path_join(unit_node, 'output'), ignore_errors=True)  # remove whole output directory
    os.makedirs(path_join(unit_node, 'output'), exist_ok=True)


def fetchqueries(self, level=0):
    ''' for debugging usage in mapping script: inn.root.displayqueries() '''
    if self.record:
        tmp = self.queries
        if tmp:
            collectqueries[self.record['BOTSID']] = tmp
    for childnode in self.children:
        childnode.fetchqueries(level+1)


# Helper function to trigger botslib.MessageError because errors are "buffered" in InMessage classes. (parse_edi_file)
def parse_edi_file(*args, **kwargs):
    __tracebackhide__ = True

    edi = inmessage.parse_edi_file(*args, **kwargs)
    edi.checkforerrorlist()
    return edi


@pytest.mark.usefixtures('unit_node')
@pytest.mark.plugin_test
class TestNode:
    ''' test node.py and message.py. '''

    def test_edifact01(self, unit_node):
        inn = parse_edi_file(
            editype='edifact',
            messagetype='invoicwithenvelope',
            filename=path_join(unit_node, 'nodetest01.edi')
        )
        out = outmessage.outmessage_init(
            editype='edifact',
            messagetype='invoicwithenvelope',
            filename=path_join(unit_node, 'output', 'inisout03.edi'),
            divtext='',
            topartner=''
        )  # make outmessage object
        assert hasattr(inn, 'root')
        out.root = inn.root

        # * getloop **************************************
        count = 0
        for t in inn.getloop({'BOTSID': 'XXX'}):
            count += 1
        assert count == 0, 'Cmplines'

        count = 0
        for t in inn.getloop({'BOTSID': 'UNB'}):
            count += 1
        assert count == 2, 'Cmplines'

        count = 0
        for t in out.getloop({'BOTSID': 'UNB'}, {'BOTSID': 'XXX'}):
            count += 1
        assert count == 0, 'Cmplines'

        count = 0
        for t in out.getloop({'BOTSID': 'UNB'}, {'BOTSID': 'UNH'}):
            count += 1
        assert count == 3, 'Cmplines'

        count = 0
        for t in inn.getloop({'BOTSID': 'UNB'}, {'BOTSID': 'UNH'}, {'BOTSID': 'XXX'}):
            count += 1
        assert count == 0, 'Cmplines'

        count = 0
        for t in inn.getloop({'BOTSID': 'UNB'}, {'BOTSID': 'UNH'}, {'BOTSID': 'LIN'}):
            count += 1
        assert count == 6, 'Cmplines'

        count = 0
        for t in inn.getloop({'BOTSID': 'UNB'}, {'BOTSID': 'XXX'}, {'BOTSID': 'LIN'}, {'BOTSID': 'QTY'}):
            count += 1
        assert count == 0, 'Cmplines'

        count = 0
        for t in inn.getloop({'BOTSID': 'UNB'}, {'BOTSID': 'UNH'}, {'BOTSID': 'LIN'}, {'BOTSID': 'XXX'}):
            count += 1
        assert count == 0, 'Cmplines'

        count = 0
        for t in inn.getloop({'BOTSID': 'UNB'}, {'BOTSID': 'UNH'}, {'BOTSID': 'LIN'}, {'BOTSID': 'QTY'}):
            count += 1
        assert count == 6, 'Cmplines'

        # * getcount, getcountmpath **************************************
        count = 0
        countlist = [5, 0, 1]
        nrsegmentslist = [132, 10, 12]
        for t in out.getloop({'BOTSID': 'UNB'}, {'BOTSID': 'UNH'}):
            count2 = 0
            for u in t.getloop({'BOTSID': 'UNH'}, {'BOTSID': 'LIN'}):
                count2 += 1
            count3 = t.getcountoccurrences({'BOTSID': 'UNH'}, {'BOTSID': 'LIN'})
            assert t.getcount() == nrsegmentslist[count], 'Cmplines'
            assert count2 == countlist[count], 'Cmplines'
            assert count3 == countlist[count], 'Cmplines'
            count += 1
        assert out.getcountoccurrences({'BOTSID': 'UNB'}, {'BOTSID': 'UNH'}) == count, 'Cmplines'
        assert inn.getcountoccurrences({'BOTSID': 'UNB'}, {'BOTSID': 'UNH'}) == count, 'Cmplines'
        assert inn.getcount() == sum(nrsegmentslist, 4), 'Cmplines'
        assert out.getcount() == sum(nrsegmentslist, 4), 'Cmplines'

        # * get, getnozero, countmpath, sort**************************************
        for t in out.getloop({'BOTSID': 'UNB'}, {'BOTSID': 'UNH'}):
            with pytest.raises(botslib.MappingRootError):
                out.get()
            with pytest.raises(botslib.MappingRootError):
                out.getnozero()
            with pytest.raises(botslib.MappingRootError):
                out.get(0)
            with pytest.raises(botslib.MappingRootError):
                out.getnozero(0)

            t.sort({'BOTSID': 'UNH'}, {'BOTSID': 'LIN', 'C212.7140': None})
            start = '0'
            for u in t.getloop({'BOTSID': 'UNH'}, {'BOTSID': 'LIN'}):
                nextstart = u.get({'BOTSID': 'LIN', 'C212.7140': None})
                self.assertTrue(start < nextstart)
                start = nextstart
            t.sort({'BOTSID': 'UNH'}, {'BOTSID': 'LIN', '1082': None})
            start = '0'
            for u in t.getloop({'BOTSID': 'UNH'}, {'BOTSID': 'LIN'}):
                nextstart = u.get({'BOTSID': 'LIN', '1082': None})
                self.assertTrue(start < nextstart)
                start = nextstart

        with pytest.raises(botslib.MappingRootError):
            out.get()
        with pytest.raises(botslib.MappingRootError):
            out.getnozero()

        first = True
        for t in out.getloop({'BOTSID': 'UNB'}):
            if first:
                assert '15' == t.getcountsum(
                    {'BOTSID': 'UNB'},
                    {'BOTSID': 'UNH'},
                    {'BOTSID': 'LIN', '1082': None}
                ), 'Cmplines'
                assert '8' == t.getcountsum(
                    {'BOTSID': 'UNB'},
                    {'BOTSID': 'UNH'},
                    {'BOTSID': 'LIN'},
                    {'BOTSID': 'QTY', 'C186.6063': '47', 'C186.6060': None}
                ), 'Cmplines'
                assert '0' == t.getcountsum(
                    {'BOTSID': 'UNB'},
                    {'BOTSID': 'UNH'},
                    {'BOTSID': 'LIN'},
                    {'BOTSID': 'QTY', 'C186.6063': '12', 'C186.6060': None}
                ), 'Cmplines'
                assert '54.4' == t.getcountsum(
                    {'BOTSID': 'UNB'},
                    {'BOTSID': 'UNH'},
                    {'BOTSID': 'LIN'},
                    {'BOTSID': 'MOA', 'C516.5025': '203', 'C516.5004': None}
                ), 'Cmplines'
                first = False
            else:
                assert '1' == t.getcountsum(
                    {'BOTSID': 'UNB'},
                    {'BOTSID': 'UNH'},
                    {'BOTSID': 'LIN'},
                    {'BOTSID': 'QTY', 'C186.6063': '47', 'C186.6060': None}
                ), 'Cmplines'
                assert '0' == t.getcountsum(
                    {'BOTSID': 'UNB'},
                    {'BOTSID': 'UNH'},
                    {'BOTSID': 'LIN'},
                    {'BOTSID': 'QTY', 'C186.6063': '12', 'C186.6060': None}
                ), 'Cmplines'
                assert '0' == t.getcountsum(
                    {'BOTSID': 'UNB'},
                    {'BOTSID': 'UNH'},
                    {'BOTSID': 'LIN'},
                    {'BOTSID': 'MOA', 'C516.5025': '203', 'C516.5004': None}
                ), 'Cmplines'

    def test_edifact02(self, unit_node):
        # display query correct? incluuding propagating 'down the tree'?
        inn = parse_edi_file(
            editype='edifact',
            messagetype='invoicwithenvelopetestquery',
            filename=path_join(unit_node, 'nodetest01.edi')
        )
        assert hasattr(inn, 'root')

        inn.root.processqueries({}, 2)
        inn.root.displayqueries()

    def test_edifact03(self, unit_node):
        # display query correct? incluuding propagating 'down the tree'?
        node.Node.fetchqueries = fetchqueries
        inn = parse_edi_file(
            editype='edifact',
            messagetype='edifact',
            filename=path_join(unit_node, '0T0000000015.edi')
        )
        assert hasattr(inn, 'root')

        inn.root.processqueries({}, 2)
        inn.root.fetchqueries()
        print(collectqueries)

        comparequeries = {'UNH': {'reference': 'UNHREF', 'messagetype': 'ORDERSD96AUNEAN008', 'reference2': 'UNBREF', 'topartner': 'PARTNER2', 'alt': '50EAB', 'alt2': '50E9', 'frompartner': 'PARTNER1'}, 'UNB': {'topartner': 'PARTNER2', 'reference2': 'UNBREF', 'reference': 'UNBREF', 'frompartner': 'PARTNER1'}, 'UNZ': {'reference': 'UNBREF', 'reference2': 'UNBREF', 'topartner': 'PARTNER2', 'frompartner': 'PARTNER1'}}
        assert comparequeries == collectqueries

        inn.root.displayqueries()
