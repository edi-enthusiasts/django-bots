# -*- coding: utf-8 -*-

''' Declare database tables.
    Django is not always perfect in generating db - but improving ;-)).
    The generated database can be manipulated SQL. see bots/sql/*.
'''
import os
import urllib.parse
import re
from django.db import models
from django.utils.translation import ugettext_lazy as _t  # django 1.7: have to use ugettext_lazy here
from django.core.validators import validate_integer
from django.core.exceptions import ValidationError

# bots-modules
from . import botsglobal
from . import validate_email

# ***Declare constants, mostly codelists.
DEFAULT_ENTRY = ('', "---------")
STATUST = [
    (0, _t('Open')),
    (1, _t('Error')),
    (2, _t('Stuck')),
    (3, _t('Done')),
    (4, _t('Resend')),
    (5, _t('No retry')),
]
STATUS = [
    (1,   _t('Process')),
    (3,   _t('Discarded')),
    (200, _t('Received')),
    (220, _t('Infile')),
    (310, _t('Parsed')),
    (320, _t('Document-in')),
    (330, _t('Document-out')),
    (400, _t('Merged')),
    (500, _t('Outfile')),
    (520, _t('Send')),
]
EDITYPES = [
    # DEFAULT_ENTRY,
    ('csv', _t('csv')),
    ('database', _t('database (old)')),
    ('db', _t('db')),
    ('edifact', _t('edifact')),
    ('email-confirmation', _t('email-confirmation')),
    ('excel', _t('excel (only incoming)')),
    ('fixed', _t('fixed')),
    ('idoc', _t('idoc')),
    ('json', _t('json')),
    ('jsonnocheck', _t('jsonnocheck')),
    ('mailbag', _t('mailbag')),
    ('raw', _t('raw')),
    ('templatehtml', _t('template-html')),
    ('tradacoms', _t('tradacoms')),
    ('xml', _t('xml')),
    ('xmlnocheck', _t('xmlnocheck')),
    ('x12', _t('x12')),
]
INOROUT = (
    ('in', _t('in')),
    ('out', _t('out')),
)
CHANNELTYPE = (  # Note: in communication.py these channeltypes are converted to channeltype to use in acceptance tests.
    ('file', _t('file')),
    ('smtp', _t('smtp')),
    ('smtps', _t('smtps')),
    ('smtpstarttls', _t('smtpstarttls')),
    ('pop3', _t('pop3')),
    ('pop3s', _t('pop3s')),
    ('pop3apop', _t('pop3apop')),
    ('http', _t('http')),
    ('https', _t('https')),
    ('imap4', _t('imap4')),
    ('imap4s', _t('imap4s')),
    ('ftp', _t('ftp')),
    ('ftps', _t('ftps (explicit)')),
    ('ftpis', _t('ftps (implicit)')),
    ('sftp', _t('sftp (ssh)')),
    ('xmlrpc', _t('xmlrpc')),
    ('mimefile', _t('mimefile')),
    ('trash', _t('trash/discard')),
    ('communicationscript', _t('communicationscript')),
    ('db', _t('db')),
    ('database', _t('database (old)')),
)
CONFIRMTYPE = [
    ('ask-email-MDN',       _t('ask an email confirmation (MDN) when sending')),
    ('send-email-MDN',      _t('send an email confirmation (MDN) when receiving')),
    ('ask-x12-997',         _t('ask a x12 confirmation (997) when sending')),
    ('send-x12-997',        _t('send a x12 confirmation (997) when receiving')),
    ('ask-edifact-CONTRL',  _t('ask an edifact confirmation (CONTRL) when sending')),
    ('send-edifact-CONTRL', _t('send an edifact confirmation (CONTRL) when receiving')),
]
RULETYPE = (
    ('all',         _t('Confirm all')),
    ('route',       _t('Route')),
    ('channel',     _t('Channel')),
    ('frompartner', _t('Frompartner')),
    ('topartner',   _t('Topartner')),
    ('messagetype', _t('Messagetype')),
)
ENCODE_MIME = (
    ('always', _t('Base64')),
    ('never',  _t('Never')),
    ('ascii',  _t('Base64 if not ascii')),
)
EDI_AS_ATTACHMENT = (
    ('attachment', _t('As attachment')),
    ('body',       _t('In body of email')),
)
ENCODE_ZIP_IN = (
    (1, _t('Always unzip file')),
    (2, _t('If zip-file: unzip')),
)
ENCODE_ZIP_OUT = (
    (1, _t('Always zip')),
)
TRANSLATETYPES = (
    (0, _t('Nothing')),
    (1, _t('Translate')),
    (2, _t('Pass-through')),
    (3, _t('Parse & Pass-through')),
)
CONFIRMTYPELIST = [DEFAULT_ENTRY] + CONFIRMTYPE
EDITYPESLIST = [DEFAULT_ENTRY] + EDITYPES


# ***Functions that produced codelists.**********************************************
def getroutelist():  # needed because the routeid is needed (and this is not theprimary key
    return [DEFAULT_ENTRY]+[(l, l) for l in routes.objects.values_list('idroute', flat=True).order_by('idroute').distinct()]


def getinmessagetypes():
    return [DEFAULT_ENTRY]+[(l, l) for l in translate.objects.values_list('frommessagetype', flat=True).order_by('frommessagetype').distinct()]


def getoutmessagetypes():
    return [DEFAULT_ENTRY]+[(l, l) for l in translate.objects.values_list('tomessagetype', flat=True).order_by('tomessagetype').distinct()]


def getallmessagetypes():
    return [DEFAULT_ENTRY]+[(l, l) for l in sorted(set(list(translate.objects.values_list('tomessagetype', flat=True).all()) + list(translate.objects.values_list('frommessagetype', flat=True).all())))]


def getpartners():
    return [DEFAULT_ENTRY]+[(l, '%s (%s)' % (l, n)) for (l, n) in partner.objects.values_list('idpartner', 'name').filter(active=True)]


def getfromchannels():
    return [DEFAULT_ENTRY]+[(l, '%s (%s)' % (l, t)) for (l, t) in channel.objects.values_list('idchannel', 'type').filter(inorout='in')]


def gettochannels():
    return [DEFAULT_ENTRY]+[(l, '%s (%s)' % (l, t)) for (l, t) in channel.objects.values_list('idchannel', 'type').filter(inorout='out')]


# ***Database tables that produced codelists.**********************************************
class StripCharField(models.CharField):
    ''' strip values before saving to database. this is not default in django #%^&* '''
    def get_prep_value(self, value, *args, **kwargs):
        ''' Convert Python objects (value) to query values (returned) '''
        if isinstance(value, str):
            return value.strip()
        else:
            return value


def multiple_email_validator(value):
    ''' Problems with validating email adresses:
        django's email validating is to strict. (eg if quoted user part, space is not allowed).
        use case: x400 via IPmail (x400 addresses are used in email-addresses).
        Use re-expressions to get this better/conform email standards.
    '''
    if botsglobal.ini.getboolean('webserver', 'use_email_address_validation', fallback=True):  # tric to disable email validation via bots.ini
        emails = re.split(',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', value)  # split emails
        for email in emails:
            if not validate_email.validate_email_address(email):
                raise ValidationError(_t('Enter valid e-mail address(es) separated by commas.'), code='invalid')


def script_link1(script, linktext):
    ''' if script exists return a plain text name as link; else return "no" icon, plain text name
        used in translate (all scripts should exist, missing script is an error).
    '''
    if os.path.exists(script):
        return '<a href="/srcfiler/?src=%s" target="_blank">%s</a>' % (urllib.parse.quote(script.encode("utf-8")), linktext)
    else:
        return '<img src="/media/admin/img/icon-no.gif"></img> %s' % linktext


def script_link2(script):
    ''' if script exists return "yes" icon + view link; else return "no" icon
        used in routes, channels (scripts are optional)
    '''
    if os.path.exists(script):
        return '<a class="nowrap" href="/srcfiler/?src=%s" target="_blank"><img src="/media/admin/img/icon-yes.gif"></img> view</a>' % urllib.parse.quote(script.encode("utf-8"))
    else:
        return '<img src="/media/admin/img/icon-no.gif"></img>'


class MultipleEmailField(models.CharField):
    default_validators = [multiple_email_validator]
    description = _t('One or more e-mail address(es),separated by ",".')


class TextAsInteger(models.CharField):
    default_validators = [validate_integer]


# ***********************************************************************************
# ******** written by webserver ********************************************************
# ***********************************************************************************
class confirmrule(models.Model):
    # id = models.IntegerField(primary_key=True)
    active = \
        models.BooleanField(default=False)
    confirmtype = \
        StripCharField(max_length=35, choices=CONFIRMTYPE)
    ruletype = \
        StripCharField(max_length=35, choices=RULETYPE)
    negativerule = \
        models.BooleanField(default=False, help_text=_t('Use to exclude. Bots first checks positive rules, than negative rules. Eg include certain channel, exclude partner XXX.'))
    frompartner = \
        models.ForeignKey('partner', related_name='cfrompartner', null=True, on_delete=models.CASCADE, blank=True, limit_choices_to={'isgroup': False})
    topartner = \
        models.ForeignKey('partner', related_name='ctopartner', null=True, on_delete=models.CASCADE, blank=True, limit_choices_to={'isgroup': False})
    idroute = \
        StripCharField(max_length=35, null=True, blank=True, verbose_name=_t('route'))
    idchannel = \
        models.ForeignKey('channel', null=True, on_delete=models.CASCADE, blank=True, verbose_name=_t('channel'))
    editype = \
        StripCharField(max_length=35, choices=EDITYPES, blank=True)  # 20121229 is not used anymore.....editype is always clear from context.
    messagetype = \
        StripCharField(max_length=35, blank=True, help_text=_t('Eg "850004010" (x12) or "ORDERSD96AUN" (edifact).'))
    rsrv1 = \
        StripCharField(max_length=35, blank=True, null=True)  # added 20100501
    rsrv2 = \
        models.IntegerField(null=True)  # added 20100501

    def __str__(self):
        return str(self.confirmtype) + ' ' + str(self.ruletype)

    class Meta:
        db_table = 'confirmrule'
        verbose_name = _t('confirm rule')
        ordering = ['confirmtype', 'ruletype', 'negativerule', 'frompartner', 'topartner', 'idroute', 'idchannel', 'messagetype']


class ccodetrigger(models.Model):
    ccodeid = \
        StripCharField(primary_key=True, max_length=35, verbose_name=_t('Type of user code'))
    ccodeid_desc = \
        models.TextField(blank=True, null=True, verbose_name=_t('Description'))

    def __str__(self):
        return str(self.ccodeid)

    class Meta:
        db_table = 'ccodetrigger'
        verbose_name = _t('user code type')
        ordering = ['ccodeid']


class ccode(models.Model):
    # id = models.IntegerField(primary_key=True)  # added 20091221
    ccodeid = \
        models.ForeignKey(ccodetrigger, on_delete=models.CASCADE, verbose_name=_t('Type of user code'))
    leftcode = \
        StripCharField(max_length=35, db_index=True)
    rightcode = \
        StripCharField(max_length=70, db_index=True)
    attr1 = \
        StripCharField(max_length=70, blank=True)
    attr2 = \
        StripCharField(max_length=35, blank=True)
    attr3 = \
        StripCharField(max_length=35, blank=True)
    attr4 = \
        StripCharField(max_length=35, blank=True)
    attr5 = \
        StripCharField(max_length=35, blank=True)
    attr6 = \
        StripCharField(max_length=35, blank=True)
    attr7 = \
        StripCharField(max_length=35, blank=True)
    attr8 = \
        StripCharField(max_length=35, blank=True)

    def __str__(self):
        return str(self.ccodeid) + ' ' + str(self.leftcode) + ' ' + str(self.rightcode)

    class Meta:
        db_table = 'ccode'
        verbose_name = _t('user code')
        unique_together = (('ccodeid', 'leftcode', 'rightcode'),)
        ordering = ['ccodeid', 'leftcode']


class channel(models.Model):
    idchannel = \
        StripCharField(max_length=35, primary_key=True)
    inorout = \
        StripCharField(max_length=35, choices=INOROUT, verbose_name=_t('in/out'))
    type = \
        StripCharField(max_length=35, choices=CHANNELTYPE)  # protocol type: ftp, smtp, file, etc
    charset = \
        StripCharField(max_length=35, default='us-ascii')  # 20120828: not used anymore; in database is NOT NULL
    host = \
        StripCharField(max_length=256, blank=True)
    port = \
        models.PositiveIntegerField(default=0, blank=True, null=True)
    username = \
        StripCharField(max_length=35, blank=True)
    secret = \
        StripCharField(max_length=35, blank=True, verbose_name=_t('password'))
    starttls = \
        models.BooleanField(default=False, verbose_name='No check from-address', help_text=_t("Do not check if incoming 'from' email addresses is known."))  # 20091027: used as 'no check on "from:" email address'
    apop = \
        models.BooleanField(default=False, verbose_name='No check to-address', help_text=_t("Do not check if incoming 'to' email addresses is known."))  # 20110104: used as 'no check on "to:" email address'
    remove = \
        models.BooleanField(default=False, help_text=_t("Delete incoming edi files after reading.<br>Use in production else files are read again and again."))
    path = \
        StripCharField(max_length=256, blank=True)  # different from host - in ftp both host and path are used
    filename = \
        StripCharField(max_length=256, blank=True, help_text=_t('Incoming: use wild-cards eg: "*.edi".<br>Outgoing: many options, see <a target="_blank" href="http://code.google.com/p/bots/wiki/Filenames">wiki</a>.<br>Advised: use "*" in filename (is replaced by unique counter per channel).<br>eg "D_*.edi" gives D_1.edi, D_2.edi, etc.'))
    lockname = \
        StripCharField(max_length=35, blank=True, verbose_name=_t('Lock-file'), help_text=_t('Directory locking: if lock-file exists in directory, directory is locked for reading/writing.'))
    syslock = \
        models.BooleanField(default=False, verbose_name=_t('System locks'), help_text=_t('Use system file locks for reading or writing edi files (windows, *nix).'))
    parameters = \
        StripCharField(max_length=70, blank=True, help_text=_t('For use in user communication scripting.'))
    ftpaccount = \
        StripCharField(max_length=35, blank=True, verbose_name=_t('ftp account'), help_text=_t('FTP account information; note that few systems implement this.'))
    ftpactive = \
        models.BooleanField(default=False, verbose_name=_t('ftp active mode'), help_text=_t('Passive mode is used unless this is ticked.'))
    ftpbinary = \
        models.BooleanField(default=False, verbose_name=_t('ftp binary transfer mode'), help_text=_t('File transfers are ASCII unless this is ticked.'))
    askmdn = \
        StripCharField(max_length=17, blank=True, choices=ENCODE_MIME, verbose_name=_t('mime encoding'))  # 20100703: used to indicate mime-encoding
    sendmdn = \
        StripCharField(max_length=17, blank=True, choices=EDI_AS_ATTACHMENT, verbose_name=_t('as body or attachment'))  # 20120922: for email/mime: edi file as attachment or in body
    mdnchannel = \
        StripCharField(max_length=35, blank=True, verbose_name=_t('Tmp-part file name'), help_text=_t('Write file than rename. Bots renames to filename without this tmp-part.<br>Eg first write "myfile.edi.tmp", tmp-part is ".tmp", rename to "myfile.edi".'))  # 20140113:use as tmp part of file name
    archivepath = \
        StripCharField(max_length=256, blank=True, verbose_name=_t('Archive path'), help_text=_t('Write edi files to an archive.<br>See <a target="_blank" href="http://code.google.com/p/bots/wiki/Archiving">wiki</a>. Eg: "C:/edi/archive/mychannel".'))  # added 20091028
    desc = \
        models.TextField(max_length=256, null=True, blank=True, verbose_name=_t('Description'))
    rsrv1 = \
        TextAsInteger(max_length=35, blank=True, null=True, verbose_name=_t('Max failures'), help_text=_t('Max number of connection failures of incommunication before this is reported as a processerror (default: direct report).'))  # added 20100501 #20140315: used as max_com
    rsrv2 = \
        models.IntegerField(null=True, blank=True, verbose_name=_t('Max seconds'), help_text=_t('Max seconds for in-communication channel to run. Purpose: limit incoming edi files; for large volumes it is better read more often than all files in one time.'))  # added 20100501. 20110906: max communication time.
    rsrv3 = \
        models.IntegerField(null=True, blank=True, verbose_name=_t('Max days archive'), help_text=_t('Max number of days files are kept in archive.<br>Overrules global setting in bots.ini.'))  # added 20121030. #20131231: use as maxdaysarchive
    keyfile = \
        StripCharField(max_length=256, blank=True, null=True, verbose_name=_t('Private key file'), help_text=_t('Path to file that contains PEM formatted private key.'))  # added 20121201
    certfile = \
        StripCharField(max_length=256, blank=True, null=True, verbose_name=_t('Certificate chain file'), help_text=_t('Path to file that contains PEM formatted certificate chain.'))  # added 20121201
    testpath = \
        StripCharField(max_length=256, blank=True, verbose_name=_t('Acceptance test path'), help_text=_t('Path used during acceptance tests, see <a target="_blank" href="http://code.google.com/p/bots/wiki/DeploymentAcceptance">wiki</a>.'))  # added 20120111

    def communicationscript(self):
        return script_link2(os.path.join(botsglobal.ini.get('directories', 'usersysabs'), 'communicationscripts', self.idchannel + '.py'))
    communicationscript.allow_tags = True
    communicationscript.short_description = 'User script'

    class Meta:
        ordering = ['idchannel']
        db_table = 'channel'

    def __str__(self):
        return self.idchannel + ' (' + self.type + ')'


class partner(models.Model):
    idpartner = \
        StripCharField(max_length=35, primary_key=True, verbose_name=_t('partner identification'))
    active = \
        models.BooleanField(default=False)
    isgroup = \
        models.BooleanField(default=False, help_text=_t('Indicate if normal partner or a partner group. Partners can be assigned to partner groups.'))
    name = \
        StripCharField(max_length=256)  # only used for user information
    mail = \
        MultipleEmailField(max_length=256, blank=True)
    cc = \
        MultipleEmailField(max_length=256, blank=True, help_text=_t('Multiple CC-addresses supported (comma-separated).'))
    mail2 = \
        models.ManyToManyField(channel, through='chanpar', blank=True)
    group = \
        models.ManyToManyField("self", db_table='partnergroup', blank=True, symmetrical=False, limit_choices_to={'isgroup': True})
    rsrv1 = \
        StripCharField(max_length=35, blank=True, null=True)  # added 20100501
    rsrv2 = \
        models.IntegerField(null=True)  # added 20100501
    name1 = \
        StripCharField(max_length=70, blank=True, null=True)  # added 20121201
    name2 = \
        StripCharField(max_length=70, blank=True, null=True)  # added 20121201
    name3 = \
        StripCharField(max_length=70, blank=True, null=True)  # added 20121201
    address1 = \
        StripCharField(max_length=70, blank=True, null=True)  # added 20121201
    address2 = \
        StripCharField(max_length=70, blank=True, null=True)  # added 20121201
    address3 = \
        StripCharField(max_length=70, blank=True, null=True)  # added 20121201
    city = \
        StripCharField(max_length=35, blank=True, null=True)  # added 20121201
    postalcode = \
        StripCharField(max_length=17, blank=True, null=True)  # added 20121201
    countrysubdivision = \
        StripCharField(max_length=9, blank=True, null=True)  # added 20121201
    countrycode = \
        StripCharField(max_length=3, blank=True, null=True)  # added 20121201
    phone1 = \
        StripCharField(max_length=17, blank=True, null=True)  # added 20121201
    phone2 = \
        StripCharField(max_length=17, blank=True, null=True)  # added 20121201
    startdate = \
        models.DateField(blank=True, null=True)  # added 20121201
    enddate = \
        models.DateField(blank=True, null=True)  # added 20121201
    desc = \
        models.TextField(blank=True, null=True, verbose_name=_t('Description'))  # added 20121201
    attr1 = \
        StripCharField(max_length=35, blank=True, null=True, verbose_name=_t('attr1'))  # user can customise verbose name
    attr2 = \
        StripCharField(max_length=35, blank=True, null=True, verbose_name=_t('attr2'))
    attr3 = \
        StripCharField(max_length=35, blank=True, null=True, verbose_name=_t('attr3'))
    attr4 = \
        StripCharField(max_length=35, blank=True, null=True, verbose_name=_t('attr4'))
    attr5 = \
        StripCharField(max_length=35, blank=True, null=True, verbose_name=_t('attr5'))

    class Meta:
        ordering = ['idpartner']
        db_table = 'partner'

    def __str__(self):
        return str(self.idpartner) + ' (' + str(self.name) + ')'

    def save(self, *args, **kwargs):
        if isinstance(self, partnergroep):
            self.isgroup = True
        else:
            self.isgroup = False
        super(partner, self).save(*args, **kwargs)


class partnergroep(partner):

    class Meta:
        proxy = True
        ordering = ['idpartner']
        db_table = 'partner'


class chanpar(models.Model):
    # id = models.IntegerField(primary_key=True)  # added 20091221
    idpartner = \
        models.ForeignKey(partner, on_delete=models.CASCADE, verbose_name=_t('partner'))
    idchannel = \
        models.ForeignKey(channel, on_delete=models.CASCADE, verbose_name=_t('channel'))
    mail = \
        MultipleEmailField(max_length=256)
    cc = \
        MultipleEmailField(max_length=256, blank=True)  # added 20091111
    askmdn = \
        models.BooleanField(default=False)  # not used anymore 20091019
    sendmdn = \
        models.BooleanField(default=False)  # not used anymore 20091019

    class Meta:
        unique_together = (('idpartner', 'idchannel'))
        ordering = ['idpartner', 'idchannel']
        db_table = 'chanpar'
        verbose_name = _t('email address per channel')
        verbose_name_plural = _t('email address per channel')

    def __str__(self):
        return str(self.idpartner) + ' ' + str(self.idchannel) + ' ' + str(self.mail)


class translate(models.Model):
    # id = models.IntegerField(primary_key=True)
    active = \
        models.BooleanField(default=False)
    fromeditype = \
        StripCharField(max_length=35, choices=EDITYPES, help_text=_t('Editype to translate from.'))
    frommessagetype = \
        StripCharField(max_length=35, help_text=_t('Messagetype to translate from.'))
    alt = \
        StripCharField(max_length=35, null=False, blank=True, verbose_name=_t('Alternative translation'), help_text=_t('Do translation only for this alternative translation.'))
    frompartner = \
        models.ForeignKey(partner, related_name='tfrompartner', null=True, blank=True, on_delete=models.PROTECT, help_text=_t('Do translation only for this frompartner.'))
    topartner = \
        models.ForeignKey(partner, related_name='ttopartner', null=True, blank=True, on_delete=models.PROTECT, help_text=_t('Do translation only for this topartner.'))
    tscript = \
        StripCharField(max_length=35, verbose_name=_t('Mapping Script'), help_text=_t('Mappingscript to use in translation.'))
    toeditype = \
        StripCharField(max_length=35, choices=EDITYPES, help_text=_t('Editype to translate to.'))
    tomessagetype = \
        StripCharField(max_length=35, help_text=_t('Messagetype to translate to.'))
    desc = \
        models.TextField(max_length=256, null=True, blank=True, verbose_name=_t('Description'))
    rsrv1 = \
        StripCharField(max_length=35, blank=True, null=True)  # added 20100501
    rsrv2 = \
        models.IntegerField(null=True)  # added 20100501

    def tscript_link(self):
        return script_link1(os.path.join(botsglobal.ini.get('directories', 'usersysabs'), 'mappings', self.fromeditype, self.tscript + '.py'), self.tscript)

    tscript_link.allow_tags = True
    tscript_link.short_description = 'Mapping Script'

    def frommessagetype_link(self):
        return script_link1(os.path.join(botsglobal.ini.get('directories', 'usersysabs'), 'grammars', self.fromeditype, self.frommessagetype + '.py'), self.frommessagetype)

    frommessagetype_link.allow_tags = True
    frommessagetype_link.short_description = 'Frommessagetype'

    def tomessagetype_link(self):
        return script_link1(os.path.join(botsglobal.ini.get('directories', 'usersysabs'), 'grammars', self.toeditype, self.tomessagetype + '.py'), self.tomessagetype)

    tomessagetype_link.allow_tags = True
    tomessagetype_link.short_description = 'Tomessagetype'

    class Meta:
        db_table = 'translate'
        verbose_name = _t('translation rule')
        ordering = ['fromeditype', 'frommessagetype', 'frompartner', 'topartner', 'alt']

    def __str__(self):
        return str(self.fromeditype) + ' ' + str(self.frommessagetype) + ' ' + str(self.alt) + ' ' + str(self.frompartner) + ' ' + str(self.topartner)


class routes(models.Model):
    # id = models.IntegerField(primary_key=True)
    idroute = \
        StripCharField(max_length=35, db_index=True, help_text=_t('Identification of route; a composite route consists of multiple parts having the same "idroute".'))
    seq = \
        models.PositiveIntegerField(default=1, verbose_name=_t('Sequence'), help_text=_t('For routes consisting of multiple parts, this indicates the order these parts are run.'))
    active = \
        models.BooleanField(default=False, help_text=_t('Bots-engine only uses active routes.'))
    fromchannel = \
        models.ForeignKey(channel, related_name='rfromchannel', null=True, on_delete=models.SET_NULL, blank=True, verbose_name=_t('incoming channel'), limit_choices_to={'inorout': 'in'}, help_text=_t('Receive edi files via this communication channel.'))
    fromeditype = \
        StripCharField(max_length=35, choices=EDITYPES, blank=True, help_text=_t('Editype of the incoming edi files.'))
    frommessagetype = \
        StripCharField(max_length=35, blank=True, help_text=_t('Messagetype of incoming edi files. For edifact: messagetype=edifact; for x12: messagetype=x12.'))
    tochannel = \
        models.ForeignKey(channel, related_name='rtochannel', null=True, on_delete=models.SET_NULL, blank=True, verbose_name=_t('outgoing channel'), limit_choices_to={'inorout': 'out'}, help_text=_t('Send edi files via this communication channel.'))
    toeditype = \
        StripCharField(max_length=35, choices=EDITYPES, blank=True, help_text=_t('Filter edi files of this editype for outgoing channel.'))
    tomessagetype = \
        StripCharField(max_length=35, blank=True, help_text=_t('Filter edi files of this messagetype for outgoing channel.'))
    alt = \
        StripCharField(max_length=35, default='', blank=True, verbose_name='Alternative translation', help_text=_t('Only use if there is more than one "translation" for the same editype and messagetype.'))
    frompartner = \
        models.ForeignKey(partner, related_name='rfrompartner', null=True, on_delete=models.SET_NULL, blank=True, limit_choices_to={'isgroup': False}, help_text=_t('The frompartner of the incoming edi files.'))
    topartner = \
        models.ForeignKey(partner, related_name='rtopartner', null=True, on_delete=models.SET_NULL, blank=True, limit_choices_to={'isgroup': False}, help_text=_t('The topartner of the incoming edi files.'))
    frompartner_tochannel = \
        models.ForeignKey(partner, related_name='rfrompartner_tochannel', null=True, on_delete=models.PROTECT, blank=True, help_text=_t('Filter edi files of this partner/partnergroup for outgoing channel'))
    topartner_tochannel = \
        models.ForeignKey(partner, related_name='rtopartner_tochannel', null=True, on_delete=models.PROTECT, blank=True, help_text=_t('Filter edi files of this partner/partnergroup for outgoing channel'))
    testindicator = \
        StripCharField(max_length=1, blank=True, help_text=_t('Filter edi files with this test-indicator for outgoing channel.'))
    translateind = \
        models.IntegerField(default=1, choices=TRANSLATETYPES, verbose_name='translate', help_text=_t('Indicates what to do with incoming files for this route(part).'))
    notindefaultrun = \
        models.BooleanField(default=False, blank=True, verbose_name=_t('Not in default run'), help_text=_t('Do not use this route in a normal run. Advanced, related to scheduling specific routes or not.'))
    desc = \
        models.TextField(max_length=256, null=True, blank=True, verbose_name=_t('Description'))
    rsrv1 = \
        StripCharField(max_length=35, blank=True, null=True)  # added 20100501
    rsrv2 = \
        models.IntegerField(null=True, blank=True)  # added 20100501
    defer = \
        models.BooleanField(default=False, blank=True, help_text=_t('Set ready for communication, defer actual communication. Communication is done later in another route(-part).'))  # added 20100601
    zip_incoming = \
        models.IntegerField(null=True, blank=True, choices=ENCODE_ZIP_IN, verbose_name=_t('Incoming zip-file handling'), help_text=_t('Unzip received files.'))  # added 20100501 #20120828: use for zip-options
    zip_outgoing = \
        models.IntegerField(null=True, blank=True, choices=ENCODE_ZIP_OUT, verbose_name=_t('Outgoing zip-file handling'), help_text=_t('Send files as zip-files.'))  # added 20100501

    def routescript(self):
        return script_link2(os.path.join(botsglobal.ini.get('directories', 'usersysabs'), 'routescripts', self.idroute + '.py'))

    routescript.allow_tags = True
    routescript.short_description = 'Script'

    def indefaultrun(obj):  # @NoSelf
        return not obj.notindefaultrun

    indefaultrun.boolean = True
    indefaultrun.short_description = 'Default run'

    class Meta:
        db_table = 'routes'
        verbose_name = _t('route')
        unique_together = ('idroute', 'seq')
        ordering = ['idroute', 'seq']

    def __str__(self):
        return str(self.idroute) + ' ' + str(self.seq)

    def translt(self):
        if self.translateind == 0:
            return '<img alt="%s" src="/media/admin/img/icon-no.gif"></img>' % (self.get_translateind_display())
        elif self.translateind == 1:
            return '<img alt="%s" src="/media/admin/img/icon-yes.gif"></img>' % (self.get_translateind_display())
        elif self.translateind == 2:
            return '<img alt="%s" src="/media/images/icon-pass.gif"></img>' % (self.get_translateind_display())
        elif self.translateind == 3:
            return '<img alt="%s" src="/media/images/icon-pass_parse.gif"></img>' % (self.get_translateind_display())

    translt.allow_tags = True
    translt.admin_order_field = 'translateind'


# ***********************************************************************************
# ******** written by engine ********************************************************
# ***********************************************************************************
class filereport(models.Model):
    # id = models.IntegerField(primary_key=True)
    idta = \
        models.IntegerField(primary_key=True)
    reportidta = \
        models.IntegerField()
    statust = \
        models.IntegerField(choices=STATUST)
    retransmit = \
        models.IntegerField()
    idroute = \
        StripCharField(max_length=35)
    fromchannel = \
        StripCharField(max_length=35)
    tochannel = \
        StripCharField(max_length=35)
    frompartner = \
        StripCharField(max_length=35)
    topartner = \
        StripCharField(max_length=35)
    frommail = \
        StripCharField(max_length=256)
    tomail = \
        StripCharField(max_length=256)
    ineditype = \
        StripCharField(max_length=35, choices=EDITYPES)
    inmessagetype = \
        StripCharField(max_length=35)
    outeditype = \
        StripCharField(max_length=35, choices=EDITYPES)
    outmessagetype = \
        StripCharField(max_length=35)
    incontenttype = \
        StripCharField(max_length=35)
    outcontenttype = \
        StripCharField(max_length=35)
    nrmessages = \
        models.IntegerField()
    ts = \
        models.DateTimeField(db_index=True)  # copied from ta
    infilename = \
        StripCharField(max_length=256)
    inidta = \
        models.IntegerField(null=True)  # not used anymore
    outfilename = \
        StripCharField(max_length=256)
    outidta = \
        models.IntegerField()
    divtext = \
        StripCharField(max_length=35)
    errortext = \
        models.TextField()
    rsrv1 = \
        StripCharField(max_length=35, blank=True, null=True)  # added 20100501; 20120618: email subject
    rsrv2 = \
        models.IntegerField(null=True)  # added 20100501
    filesize = \
        models.IntegerField(null=True)  # added 20121030

    class Meta:
        db_table = 'filereport'


class mutex(models.Model):
    # specific SQL is used (database defaults are used)
    mutexk = models.IntegerField(primary_key=True)  # is always value '1'
    mutexer = models.IntegerField()
    ts = models.DateTimeField()  # timestamp of mutex

    class Meta:
        db_table = 'mutex'


class persist(models.Model):
    # OK, this has gone wrong. There is no primary key here, so django generates this. But there is no ID in the custom sql.
    # Django still uses the ID in sql manager. This leads to an error in snapshot plugin. Disabled this in snapshot function; to fix this really database has to be changed.
    # specific SQL is used (database defaults are used)
    domein = \
        StripCharField(max_length=35)
    botskey = \
        StripCharField(max_length=35)
    content = \
        models.TextField()
    ts = \
        models.DateTimeField()

    class Meta:
        db_table = 'persist'
        unique_together = ("domein", "botskey")


class report(models.Model):
    idta = \
        models.IntegerField(primary_key=True)  # rename to reportidta
    lastreceived = \
        models.IntegerField()
    lastdone = \
        models.IntegerField()
    lastopen = \
        models.IntegerField()
    lastok = \
        models.IntegerField()
    lasterror = \
        models.IntegerField()
    send = \
        models.IntegerField()
    processerrors = \
        models.IntegerField()
    ts = \
        models.DateTimeField(db_index=True)  # copied from (runroot)ta
    type = \
        StripCharField(max_length=35)
    status = \
        models.BooleanField()
    rsrv1 = \
        StripCharField(max_length=35, blank=True, null=True)  # added 20100501. 20131230: used to store the commandline for the run.
    rsrv2 = \
        models.IntegerField(null=True)  # added 20100501.
    filesize = \
        models.IntegerField(null=True)  # added 20121030: total size of messages that have been translated.
    acceptance = \
        models.IntegerField(null=True)  # added 20130114:

    class Meta:
        db_table = 'report'


# trigger for sqlite to use local time (instead of utc). I can not add this to sqlite specific sql code, as django does not allow complex (begin ... end) sql here.
# CREATE TRIGGER uselocaltime  AFTER INSERT ON ta
# BEGIN
# UPDATE ta
# SET ts = datetime('now','localtime')
# WHERE idta = new.idta ;
# END;
class ta(models.Model):
    # specific SQL is used (database defaults are used)
    idta = \
        models.AutoField(primary_key=True)
    statust = \
        models.IntegerField(choices=STATUST)
    status = \
        models.IntegerField(choices=STATUS)
    parent = \
        models.IntegerField(db_index=True)
    child = \
        models.IntegerField()
    script = \
        models.IntegerField()
    idroute = \
        StripCharField(max_length=35)
    filename = \
        StripCharField(max_length=256)
    frompartner = \
        StripCharField(max_length=35)
    topartner = \
        StripCharField(max_length=35)
    fromchannel = \
        StripCharField(max_length=35)
    tochannel = \
        StripCharField(max_length=35)
    editype = \
        StripCharField(max_length=35)
    messagetype = \
        StripCharField(max_length=35)
    alt = \
        StripCharField(max_length=35)
    divtext = \
        StripCharField(max_length=35)  # name of translation script.
    merge = \
        models.BooleanField()
    nrmessages = \
        models.IntegerField()
    testindicator = \
        StripCharField(max_length=10)  # 0:production; 1:test. Length to 1?
    reference = \
        StripCharField(max_length=70, db_index=True)
    frommail = \
        StripCharField(max_length=256)
    tomail = \
        StripCharField(max_length=256)
    charset = \
        StripCharField(max_length=35)
    statuse = \
        models.IntegerField()  # obsolete 20091019
    retransmit = \
        models.BooleanField()  # 20070831: only retransmit, not rereceive
    contenttype = \
        StripCharField(max_length=35)
    errortext = \
        models.TextField()  # 20120921: unlimited length
    ts = \
        models.DateTimeField()
    confirmasked = \
        models.BooleanField()  # added 20091019; confirmation asked or send
    confirmed = \
        models.BooleanField()  # added 20091019; is confirmation received (when asked)
    confirmtype = \
        StripCharField(max_length=35)  # added 20091019
    confirmidta = \
        models.IntegerField()  # added 20091019
    envelope = \
        StripCharField(max_length=35)  # added 20091024
    botskey = \
        StripCharField(max_length=35)  # added 20091024
    cc = \
        StripCharField(max_length=512)  # added 20091111
    rsrv1 = \
        StripCharField(max_length=35)  # added 20100501; 20120618: email subject
    rsrv2 = \
        models.IntegerField(null=True)  # added 20100501
    rsrv3 = \
        StripCharField(max_length=35)  # added 20100501; 20131231: envelopeID to explicitly control enveloping (enveloping criterium)
    rsrv4 = \
        models.IntegerField(null=True)  # added 20100501
    rsrv5 = \
        StripCharField(max_length=35)  # added 20121030
    filesize = \
        models.IntegerField(null=True)  # added 20121030
    numberofresends = \
        models.IntegerField(null=True)  # added 20121030; if all OK (no resend) this is 0

    class Meta:
        db_table = 'ta'


class uniek(models.Model):
    # specific SQL is used (database defaults are used)
    domein = \
        StripCharField(max_length=35, primary_key=True, verbose_name=_t('Counter domain'))
    nummer = \
        models.IntegerField(verbose_name=_t('Last used number'))

    class Meta:
        db_table = 'uniek'
        verbose_name = _t('counter')
        ordering = ['domein']
