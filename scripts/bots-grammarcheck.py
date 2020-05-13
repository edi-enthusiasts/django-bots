#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import join as path_join
from bots import grammarcheck

if __name__ == '__main__':
    grammarcheck.start()
    # grammarcheck.startmulti(path_join('bots', 'usersys', 'grammars', 'edifact', '*'), 'edifact')  # for bulk check of grammars
