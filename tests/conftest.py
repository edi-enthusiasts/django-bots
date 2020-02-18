# -*- coding: utf-8 -*-

import pytest
import bots.botsinit as botsinit_module


# Make sure botsinit is only initialized once when starting up the library.
@pytest.fixture(scope='session')
def botsinit():
    botsinit_module.generalinit('config')
    botsinit_module.initbotscharsets()
    return botsinit_module
