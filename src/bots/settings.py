# -*- coding: utf-8 -*-
# Django settings specific only to bots.

from django.conf import settings

SETTINGS = getattr(settings, 'BOTS', {})

del settings
del SETTINGS
