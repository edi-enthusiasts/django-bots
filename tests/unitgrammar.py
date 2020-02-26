# -*- coding: utf-8 -*-

import pytest
import bots.botslib as botslib
import bots.grammar as grammar

''' plugin unitgrammar.zip
    not an acceptance test.
'''

pytestmark = pytest.mark.usefixtures('general_init', 'init_charsets', 'engine_logging')


@pytest.mark.plugin_test
class TestGrammar:

    def test_general_grammar_errors(self):
        with pytest.raises(botslib.GrammarError):
            grammar.grammarread('flup', 'edifact')  # not existing editype
        with pytest.raises(botslib.GrammarError):
            grammar.grammarread('flup', 'edifact', 'partner')  # not existing editype
        with pytest.raises(botslib.BotsImportError):
            grammar.grammarread('edifact', 'flup')  # not existing messagetype
        with pytest.raises(botslib.BotsImportError):
            grammar.grammarread('edifact', 'flup', 'partner')  # not existing messagetype
        with pytest.raises(botslib.GrammarError):
            grammar.grammarread('test', 'test3')  # no structure
        with pytest.raises(botslib.BotsImportError):
            grammar.grammarread('test', 'test4')  # No tabel - Reference to not-existing tabel
        with pytest.raises(botslib.ScriptImportError):
            grammar.grammarread('test', 'test5')  # Error in tabel: structure is not valid python list (syntax-error)
        with pytest.raises(botslib.GrammarError):
            grammar.grammarread('test', 'test6')  # Error in tabel: record in structure not in recorddefs
        with pytest.raises(botslib.BotsImportError):
            grammar.grammarread('edifact', 'test7')  # error in syntax
        with pytest.raises(botslib.BotsImportError):
            grammar.grammarread('edifact', 'test7', 'partner')  # error in syntax

    def test_gramfield_edifact_and_general(self):
        tabel = grammar.grammarread('edifact', 'edifact')
        gramfield = tabel._checkfield

        # edifact formats to bots formats
        field = ['S001.0001', 'M', 1, 'A']
        fieldresult = ['S001.0001', 1, 1, 'A', True, 0, 0, 'A', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4, 'N']
        fieldresult = ['S001.0001', 1, 4, 'N', True, 0, 0, 'R', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4, 'AN']
        fieldresult = ['S001.0001', 1, 4, 'AN', True, 0, 0, 'A', 1]
        gramfield(field, '')
        assert field == fieldresult

        # min&max length
        field = ['S001.0001', 'M', (2, 4), 'AN']
        fieldresult = ['S001.0001', 1, 4, 'AN', True, 0, 2, 'A', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', (0, 4), 'AN']
        fieldresult = ['S001.0001', 1, 4, 'AN', True, 0, 0, 'A', 1]
        gramfield(field, '')
        assert field == fieldresult

        # decimals
        field = ['S001.0001', 'M', 3.2, 'N']
        fieldresult = ['S001.0001', 1, 3, 'N', True, 2, 0, 'R', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 18.9, 'N']
        fieldresult = ['S001.0001', 1, 18, 'N', True, 9, 0, 'R', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', (4, 4.3), 'N']
        fieldresult = ['S001.0001', 1, 4, 'N', True, 3, 4, 'R', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', (3.2, 4.2), 'N']
        fieldresult = ['S001.0001', 1, 4, 'N', True, 2, 3, 'R', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'C', (3.2, 4.2), 'N']
        fieldresult = ['S001.0001', 0, 4, 'N', True, 2, 3, 'R', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', ('C', 1234567), (3.2, 4.2), 'N']
        fieldresult = ['S001.0001', 0, 4, 'N', True, 2, 3, 'R', 1234567]
        gramfield(field, '')
        assert field == fieldresult

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # test all types of fields (I,R,N,A,D,T); tests not needed repeat for other editypes
        # check field itself
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', 4], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', 4, '', 'M', 4, '', 'M'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', 4, '', 'M', 4, ''], '')

        # check ID
        with pytest.raises(botslib.GrammarError):
            gramfield(['', 'M', 4, 'A'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield([None, 'M', 4, 'A'], '')

        # check M/C
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'A', 4, 'I'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', '', 4, 'I'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', [], 4, 'I'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'MC', 4, 'I'], '')

        # check format
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', 4, 'I'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', 4, 'N7'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', 4, ''], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', 4, 5], '')

        # check length
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', 'N', 'N'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', 0, 'N'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', -2, 'N'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', -3.2, 'N'], '')

        # length for formats without float
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', 2.1, 'A'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', (2.1, 3), 'A'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', (2, 3.2), 'A'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', (3, 2), 'A'], '')

        # length for formats with float
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', 1.1, 'N'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', ('A', 5), 'N'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', (-1, 1), 'N'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', (5, None), 'N'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', (0, 1.1), 'N'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', (0, 0), 'N'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', (2, 1), 'N'], '')

    def test_gramfield_x12(self):
        tabel = grammar.grammarread('x12', 'x12')
        gramfield = tabel._checkfield

        # x12 formats to bots formats
        field = ['S001.0001', 'M', 1, 'AN']
        fieldresult = ['S001.0001', 1, 1, 'AN', True, 0, 0, 'A', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4, 'DT']
        fieldresult = ['S001.0001', 1, 4, 'DT', True, 0, 0, 'D', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4, 'TM']
        fieldresult = ['S001.0001', 1, 4, 'TM', True, 0, 0, 'T', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4, 'B']
        fieldresult = ['S001.0001', 1, 4, 'B', True, 0, 0, 'A', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4, 'ID']
        fieldresult = ['S001.0001', 1, 4, 'ID', True, 0, 0, 'A', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4, 'R']
        fieldresult = ['S001.0001', 1, 4, 'R', True, 0, 0, 'R', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4, 'N']
        fieldresult = ['S001.0001', 1, 4, 'N', True, 0, 0, 'I', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4, 'N0']
        fieldresult = ['S001.0001', 1, 4, 'N0', True, 0, 0, 'I', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4, 'N3']
        fieldresult = ['S001.0001', 1, 4, 'N3', True, 3, 0, 'I', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4, 'N9']
        fieldresult = ['S001.0001', 1, 4, 'N9', True, 9, 0, 'I', 1]
        gramfield(field, '')
        assert field == fieldresult

        # decimals
        field = ['S001.0001', 'M', 3, 'R']
        fieldresult = ['S001.0001', 1, 3, 'R', True, 0, 0, 'R', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4.3, 'R']
        fieldresult = ['S001.0001', 1, 4, 'R', True, 3, 0, 'R', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'C', 4.3, 'R']
        fieldresult = ['S001.0001', 0, 4, 'R', True, 3, 0, 'R', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', ('M', 99999), 4.3, 'R']
        fieldresult = ['S001.0001', 1, 4, 'R', True, 3, 0, 'R', 99999]
        gramfield(field, '')
        assert field == fieldresult

        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', 4, 'D'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', 4.3, 'I'], '')
        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', 4.3, 'NO'], '')

    def test_gramfield_fixed(self):
        tabel = grammar.grammarread('fixed', 'invoicfixed')
        gramfield = tabel._checkfield

        # fixed formats to bots formats
        field = ['S001.0001', 'M', 1, 'A']
        fieldresult = ['S001.0001', 1, 1, 'A', True, 0, 1, 'A', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4, 'D']
        fieldresult = ['S001.0001', 1, 4, 'D', True, 0, 4, 'D', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4, 'T']
        fieldresult = ['S001.0001', 1, 4, 'T', True, 0, 4, 'T', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4, 'R']
        fieldresult = ['S001.0001', 1, 4, 'R', True, 0, 4, 'R', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4.3, 'N']
        fieldresult = ['S001.0001', 1, 4, 'N', True, 3, 4, 'N', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4.3, 'I']
        fieldresult = ['S001.0001', 1, 4, 'I', True, 3, 4, 'I', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'M', 4.3, 'R']
        fieldresult = ['S001.0001', 1, 4, 'R', True, 3, 4, 'R', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', 'C', 4.3, 'R']
        fieldresult = ['S001.0001', 0, 4, 'R', True, 3, 4, 'R', 1]
        gramfield(field, '')
        assert field == fieldresult

        field = ['S001.0001', ('C', 5), 4.3, 'R']
        fieldresult = ['S001.0001', 0, 4, 'R', True, 3, 4, 'R', 5]
        gramfield(field, '')
        assert field == fieldresult

        with pytest.raises(botslib.GrammarError):
            gramfield(['S001.0001', 'M', 4, 'B'], '')
