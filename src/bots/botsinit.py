# -*- coding: utf-8 -*-

import sys
import os
import encodings
import codecs
import logging.handlers
from configparser import NoOptionError, NoSectionError, RawConfigParser, _UNSET

# Bots-modules
from . import botsglobal
from . import botslib
from . import node


class BotsConfig(RawConfigParser):
    ''' As ConfigParser, but raises BotsError instead. '''
    def _get_conv(self, section, option, conv, *, raw=False, vars=None,  # @ReservedAssignment
                  fallback=_UNSET, **kwargs):
        try:
            return self._get(section, conv, option, raw=raw, vars=vars,
                             **kwargs)
        except (NoSectionError, NoOptionError):
            if fallback is _UNSET:
                raise botslib.BotsError(
                    'No entry "%(option)s" in section "%(section)s" in "bots.ini".',
                    {'option': option, 'section': section}
                ) from None
            return fallback


def generalinit(configdir=None):
    # #########################################################################
    # Configdir: settings.py & bots.ini#########################################
    # Configdir MUST be importable. So configdir is relative to PYTHONPATH. Try several options for this import.
    # If configdir is not specified the settings.py and bots.ini is checked from DJANGO_SETTINGS_MODULE import directory.
    if configdir:
        try:
            importnameforsettings = os.path.normpath(os.path.join(configdir, 'settings')).replace(os.sep, '.')
            settings = botslib.botsbaseimport(importnameforsettings)
        except ImportError:  # set pythonpath to config directory first
            if not os.path.exists(configdir):  # check if configdir exists.
                raise botslib.PanicError('In initilisation: path to configuration does not exists: "%(configdir)s".', {'configdir': configdir})
            addtopythonpath = os.path.abspath(os.path.dirname(configdir))
            moduletoimport = os.path.basename(configdir)
            sys.path.append(addtopythonpath)
            importnameforsettings = os.path.normpath(os.path.join(moduletoimport, 'settings')).replace(os.sep, '.')
            settings = botslib.botsbaseimport(importnameforsettings)
        os.environ['DJANGO_SETTINGS_MODULE'] = importnameforsettings
    else:
        if not os.environ.get('DJANGO_SETTINGS_MODULE'):  # check if DJANGO_SETTINGS_MODULE is set.
            raise botslib.PanicError('In initilisation: no fallback settings module specified in DJANGO_SETTINGS_MODULE.')
        settings = botslib.botsbaseimport(os.environ['DJANGO_SETTINGS_MODULE'])
        configdir = os.path.abspath(os.path.dirname(settings.__file__))

    # settings is imported, so now we know where to find bots.ini.
    # note: the imported settings.py itself is NOT used, this is done via django.conf.settings
    config_directory = os.path.abspath(os.path.dirname(settings.__file__))
    inipath = os.path.join(config_directory, 'bots.ini')

    # Ensure the bots.ini exists in the config directory we're going to read it from.
    if not os.path.exists(inipath):
        import bots.templates
        from shutil import copyfile
        template_path = os.path.join(os.path.abspath(os.path.dirname(bots.templates.__file__)), 'bots.ini')
        copyfile(template_path, inipath)

    # Read configuration-file bots.ini.
    botsglobal.ini = BotsConfig()
    botsglobal.ini.read(inipath)

    # 'directories','botspath': absolute path for bots directory
    botsglobal.ini.set('directories', 'botspath', os.path.abspath(os.path.dirname(__file__)))
    # 'directories','config': absolute path for config directory
    botsglobal.ini.set('directories', 'config', config_directory)
    # set config as originally received; used in starting engine via bots-monitor
    botsglobal.ini.set('directories', 'config_org', configdir or '')

    # ###########################################################################
    # Usersys####################################################################
    # usersys MUST be importable. So usersys is relative to PYTHONPATH. Try several options for this import.
    usersys = botsglobal.ini.get('directories', 'usersys', fallback='usersys')
    try:  # usersys outside bots-directory: import usersys
        importnameforusersys = os.path.normpath(usersys).replace(os.sep, '.')
        importedusersys = botslib.botsbaseimport(importnameforusersys)
    except ImportError:  # usersys is in bots directory: import bots.usersys
        try:
            importnameforusersys = os.path.normpath(os.path.join('bots', usersys)).replace(os.sep, '.')
            importedusersys = botslib.botsbaseimport(importnameforusersys)
        except ImportError:  # set pythonpath to usersys directory first
            if not os.path.exists(usersys):  # check if configdir exists.
                raise botslib.PanicError('In initilisation: path to configuration does not exists: "%(usersys)s".', {'usersys': usersys})
            addtopythonpath = os.path.abspath(os.path.dirname(usersys))  # ????
            moduletoimport = os.path.basename(usersys)
            sys.path.append(addtopythonpath)
            importnameforusersys = os.path.normpath(usersys).replace(os.sep, '.')
            importedusersys = botslib.botsbaseimport(importnameforusersys)
    # 'directories','usersysabs': absolute path for config usersysabs
    botsglobal.ini.set('directories', 'usersysabs', os.path.abspath(os.path.dirname(importedusersys.__file__)))  # ???Find pathname usersys using imported usersys
    # botsglobal.usersysimportpath: used for imports from usersys
    botsglobal.usersysimportpath = importnameforusersys
    botsglobal.ini.set('directories', 'templatehtml', botslib.join(botsglobal.ini.get('directories', 'usersysabs'), os.path.join('grammars', 'templatehtml', 'templates')))

    # ###########################################################################
    # Botssys####################################################################
    # 'directories','botssys': absolute path for config botssys
    # if specified as relative in INI, it will be relative to the project's config folder (settings.py).
    botssys = botsglobal.ini.get('directories', 'botssys', fallback='botssys')
    botsglobal.ini.set('directories', 'botssys_org', botssys)            # store original botssys setting
    botsglobal.ini.set('directories', 'botssys', os.path.join(config_directory, botssys))  # use absolute path
    botsglobal.ini.set('directories', 'data', os.path.join(config_directory, botssys, 'data'))
    botsglobal.ini.set('directories', 'logging', os.path.join(config_directory, botssys, 'logging'))

    # ###########################################################################
    # other inits##############################################################
    if botsglobal.ini.get('webserver', 'environment', fallback='development') != 'development':  # values in bots.ini are also used in setting up cherrypy
        logging.raiseExceptions = 0  # during production: if errors occurs in writing to log: ignore error. (leads to a missing log line, better than error;-).
    botslib.dirshouldbethere(botsglobal.ini.get('directories', 'data'))
    botslib.dirshouldbethere(botsglobal.ini.get('directories', 'logging'))
    initbotscharsets()  # initialise bots charsets
    node.Node.checklevel = botsglobal.ini.getint('settings', 'get_checklevel', fallback=1)
    botslib.settimeout(botsglobal.ini.getint('settings', 'globaltimeout', fallback=10))

    # ###########################################################################
    # Init django#################################################################################
    import django
    if hasattr(django, 'setup'):
        django.setup()
    from django.conf import settings
    botsglobal.settings = settings  # settings are accessed using botsglobal


# **********************************************************************************
# *** bots specific handling of character-sets (eg UNOA charset) *******************
def initbotscharsets():
    ''' set up right charset handling for specific charsets (UNOA, UNOB, UNOC, etc). '''
    # tell python how to search a codec defined by bots. Bots searches for this in usersys/charset
    codecs.register(codec_search_function)
    # syntax has parameters checkcharsetin or checkcharsetout. These can have value 'botsreplace'
    # eg: 'checkcharsetin':'botsreplace',  #strict, ignore or botsreplace
    # in case of errors: the 'wrong' character is replaced with char as set in bots.ini. Default value in bots.ini is ' ' (space)
    botsglobal.botsreplacechar = botsglobal.ini.get('settings', 'botsreplacechar', fallback=' ')
    codecs.register_error('botsreplace', botsreplacechar_handler)  # need to register the handler for botsreplacechar
    # set aliases for the charsets in bots.ini
    for key, value in botsglobal.ini.items('charsets'):
        encodings.aliases.aliases[key] = value


def codec_search_function(encoding):
    try:
        module, _ = botslib.botsimport('charsets', encoding)
    except botslib.BotsImportError:  # charsetscript not there; other errors like syntax errors are not catched
        return None
    else:
        if hasattr(module, 'getregentry'):
            return module.getregentry()
        else:
            return None


def botsreplacechar_handler(info):
    ''' replaces an char outside a charset by a user defined char. Useful eg for fixed records: recordlength does not change. '''
    return (botsglobal.botsreplacechar, info.start+1)
# *** end of bots specific handling of character-sets ******************************
# **********************************************************************************


def connect():
    ''' connect to database for non-django modules eg engine '''
    database = botsglobal.settings.DATABASES['default']
    if database['ENGINE'] == 'django.db.backends.sqlite3':
        # sqlite has some more fiddling; in separate file. Mainly because of some other method of parameter passing.
        if not os.path.isfile(database['NAME']):
            raise botslib.PanicError('Could not find database file for SQLite')
        from . import botssqlite
        botsglobal.db = botssqlite.connect(database=database['NAME'])

    elif database['ENGINE'] == 'django.db.backends.mysql':
        import pymysql
        from pymysql import cursors
        botsglobal.db = pymysql.connect(
            host=database['HOST'],
            port=int(database['PORT']),
            db=database['NAME'],
            user=database['USER'],
            passwd=database['PASSWORD'],
            cursorclass=cursors.DictCursor,
            **database['OPTIONS']
        )

    elif database['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
        import psycopg2.extensions
        import psycopg2.extras
        psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
        botsglobal.db = psycopg2.connect(
            host=database['HOST'],
            port=database['PORT'],
            database=database['NAME'],
            user=database['USER'],
            password=database['PASSWORD'],
            connection_factory=psycopg2.extras.DictConnection
        )
        botsglobal.db.set_client_encoding('UNICODE')

    else:
        raise botslib.PanicError('Unknown database engine "%(engine)s".', {'engine': database['ENGINE']})


# *******************************************************************
# *** init logging **************************************************
# *******************************************************************
logging.addLevelName(25, 'STARTINFO')
convertini2logger = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
    'STARTINFO': 25
}


def initenginelogging(logname):
    # initialise file logging: create main logger 'bots'
    logger = logging.getLogger(logname)
    logger.setLevel(convertini2logger[botsglobal.ini.get('settings', 'log_file_level', fallback='INFO')])
    handler = logging.handlers.RotatingFileHandler(
        os.path.join(botsglobal.ini.get('directories', 'logging'), logname + '.log'),
        backupCount=botsglobal.ini.getint('settings', 'log_file_number', fallback=10)
    )
    fileformat = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s : %(message)s", '%Y%m%d %H:%M:%S')
    handler.setFormatter(fileformat)
    handler.doRollover()  # each run a new log file is used; old one is rotated
    logger.addHandler(handler)
    # initialise file logging: logger for trace of mapping; tried to use filters but got this not to work.....
    botsglobal.logmap = logging.getLogger('engine.map')
    if not botsglobal.ini.getboolean('settings', 'mappingdebug', fallback=False):
        botsglobal.logmap.setLevel(logging.CRITICAL)
    # logger for reading edifile. is now used only very limited (1 place); is done with 'if'
    # botsglobal.ini.getboolean('settings', 'readrecorddebug', fallback=False)
    # initialise console/screen logging
    if botsglobal.ini.getboolean('settings', 'log_console', fallback=True):
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        consuleformat = logging.Formatter("%(levelname)-8s %(message)s")
        console.setFormatter(consuleformat)  # add formatter to console
        logger.addHandler(console)  # add console to logger
    return logger


def initserverlogging(logname):
    # initialise file logging
    logger = logging.getLogger(logname)
    logger.setLevel(convertini2logger[botsglobal.ini.get(logname, 'log_file_level', fallback='INFO')])
    handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(botsglobal.ini.get('directories', 'logging'), logname+'.log'),
        when='midnight',
        backupCount=10
    )
    fileformat = logging.Formatter("%(asctime)s %(levelname)-9s: %(message)s", '%Y%m%d %H:%M:%S')
    handler.setFormatter(fileformat)
    logger.addHandler(handler)
    # initialise console/screen logging
    if botsglobal.ini.getboolean(logname, 'log_console', fallback=True):
        console = logging.StreamHandler()
        console.setLevel(convertini2logger[botsglobal.ini.get(logname, 'log_console_level', fallback='STARTINFO')])
        consoleformat = logging.Formatter("%(asctime)s %(levelname)-9s: %(message)s", '%Y%m%d %H:%M:%S')
        console.setFormatter(consoleformat)  # add formatter to console
        logger.addHandler(console)  # add console to logger
    return logger
