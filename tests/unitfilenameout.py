# -*- coding: utf-8 -*-

import datetime
import pytest
import bots.botslib as botslib
import bots.communication as communication
from bots.botsconfig import DONE

'''
plugin unitfilenameout.zip
active all routes
no acceptance-test!
'''

pytestmark = pytest.mark.usefixtures('run_engine', 'engine_logging', 'bots_db')


def test_route_test_mdn():
    comclass = communication._comsession(
        channeldict={'idchannel': 'dutchic_desadv_out'},
        idroute='dutchic_desadv',
        userscript=None,
        scriptname=None,
        command='new',
        rootidta=0
    )

    for row in botslib.query(
        '''SELECT idta FROM ta
            WHERE status=%(status)s
            AND statust=%(statust)s
            ORDER BY idta DESC''',
        {
            'status': 520,
            'statust': DONE,
            'idroute': 'testmdn',
            'confirmtype': 'send-email-MDN',
            'confirmasked': True
        }
    ):
        sub_unique = botslib.unique('dutchic_desadv_out')
        ta = botslib.OldTransaction(row['idta'])

        assert comclass.filename_formatter('*.edi', ta) == str(sub_unique+1) + '.edi'
        assert comclass.filename_formatter('*.edi', ta) == str(sub_unique+2) + '.edi'
        assert comclass.filename_formatter('*.edi', ta) == str(sub_unique+3) + '.edi'
        assert comclass.filename_formatter('{messagetype}/{editype}/{topartner}/{frompartner}/{botskey}_*', ta) == 'DESADVD96AUNEAN005/edifact/8712345678920/8712345678910/VERZENDVB8_' + str(sub_unique+4)
        assert comclass.filename_formatter('*_{datetime:%Y-%m-%d}.edi', ta) == str(sub_unique+5) + '_' + datetime.datetime.now().strftime('%Y-%m-%d') + '.edi'
        assert comclass.filename_formatter('*_*.edi', ta) == str(sub_unique+6) + '_' + str(sub_unique+6) + '.edi'
        assert comclass.filename_formatter('123.edi', ta) == '123.edi'
        assert comclass.filename_formatter('{infile}', ta) == 'desadv1.edi'
        assert comclass.filename_formatter('{infile:name}.txt', ta) == 'desadv1.txt'
        assert comclass.filename_formatter('{infile:name}.{infile:ext}', ta) == 'desadv1.edi'

        print('expect: <idta>.edi                          ', comclass.filename_formatter('{idta}.edi', ta))

        with pytest.raises(botslib.CommunicationOutError):
            comclass.filename_formatter('{tada}', ta)

        with pytest.raises(botslib.CommunicationOutError):
            comclass.filename_formatter('{infile:test}', ta)

        break  # test only 1 incoming files
    else:
        pytest.fail('No routes to test.')
