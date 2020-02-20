# -*- coding: utf-8 -*-

import pytest
import bots.botsglobal as botsglobal_module
import bots.botsinit as botsinit_module


# Make sure botsinit is only initialized once when starting up the library.
@pytest.fixture(scope='session')
def botsinit():
    botsinit_module.generalinit('config')
    botsinit_module.initbotscharsets()
    return botsinit_module


@pytest.fixture(scope='session')
def bots_db(botsinit):
    botsinit_module.connect()
    yield botsglobal_module.db
    botsglobal_module.db.close
