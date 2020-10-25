# -*- coding: utf-8 -*-

from django.forms import (
    Form, DateTimeField, FileField,
    ChoiceField, TypedChoiceField,
    IntegerField, BooleanField,
    CharField
)
from django.forms.widgets import FileInput, HiddenInput as HIDDENINPUT
from django.utils.translation import ugettext as _t
# ***********
from . import models
from . import viewlib


class Select(Form):
    datefrom = DateTimeField(initial=viewlib.datetimefrom)
    dateuntil = DateTimeField(initial=viewlib.datetimeuntil)
    page = IntegerField(required=False, initial=1, widget=HIDDENINPUT())
    sortedby = CharField(initial='ts', widget=HIDDENINPUT())
    sortedasc = BooleanField(initial=False, required=False, widget=HIDDENINPUT())
    select_desc = 'data'


class View(Form):
    datefrom = DateTimeField(required=False, initial=viewlib.datetimefrom, widget=HIDDENINPUT())
    dateuntil = DateTimeField(required=False, initial=viewlib.datetimeuntil, widget=HIDDENINPUT())
    page = IntegerField(required=False, initial=1, widget=HIDDENINPUT())
    sortedby = CharField(required=False, initial='ts', widget=HIDDENINPUT())
    sortedasc = BooleanField(required=False, initial=False, widget=HIDDENINPUT())


class SelectReports(Select):
    template = 'bots/selectform.html'
    action = 'reports/'
    select_desc = 'reports'
    status = ChoiceField(
        [
            models.DEFAULT_ENTRY,
            ('1', "Error"),
            ('0', "Done")
        ],
        required=False,
        initial=''
    )


class ViewReports(View):
    template = 'bots/reports.html'
    action = 'reports/'
    status = IntegerField(required=False, initial='', widget=HIDDENINPUT())


class SelectIncoming(Select):
    template = 'bots/selectform.html'
    action = 'incoming/'
    select_desc = 'incoming files'
    statust = ChoiceField(
        [
            models.DEFAULT_ENTRY,
            ('1', "Error"),
            ('3', "Done")
        ],
        required=False,
        initial=''
    )
    idroute = ChoiceField([], required=False, initial='')
    fromchannel = ChoiceField([], required=False)
    frompartner = ChoiceField([], required=False)
    topartner = ChoiceField([], required=False)
    ineditype = ChoiceField(models.EDITYPESLIST, required=False)
    inmessagetype = ChoiceField([], required=False)
    outeditype = ChoiceField(models.EDITYPESLIST, required=False)
    outmessagetype = ChoiceField([], required=False)
    infilename = CharField(required=False, label='Filename', max_length=70)
    lastrun = BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super(SelectIncoming, self).__init__(*args, **kwargs)
        self.fields['idroute'].choices = models.getroutelist()
        self.fields['inmessagetype'].choices = models.getinmessagetypes()
        self.fields['outmessagetype'].choices = models.getoutmessagetypes()
        self.fields['frompartner'].choices = models.getpartners()
        self.fields['topartner'].choices = models.getpartners()
        self.fields['fromchannel'].choices = models.getfromchannels()


class ViewIncoming(View):
    template = 'bots/incoming.html'
    action = 'incoming/'
    statust = IntegerField(required=False, initial='', widget=HIDDENINPUT())
    idroute = CharField(required=False, widget=HIDDENINPUT())
    fromchannel = CharField(required=False, widget=HIDDENINPUT())
    frompartner = CharField(required=False, widget=HIDDENINPUT())
    topartner = CharField(required=False, widget=HIDDENINPUT())
    ineditype = CharField(required=False, widget=HIDDENINPUT())
    inmessagetype = CharField(required=False, widget=HIDDENINPUT())
    outeditype = CharField(required=False, widget=HIDDENINPUT())
    outmessagetype = CharField(required=False, widget=HIDDENINPUT())
    infilename = CharField(required=False, widget=HIDDENINPUT(), max_length=256)
    lastrun = BooleanField(required=False, initial=False, widget=HIDDENINPUT())


class SelectDocument(Select):
    template = 'bots/selectform.html'
    action = 'document/'
    select_desc = 'documents'
    status = TypedChoiceField(
        [
            (0, "---------"),
            (320, _t('Document-in')),
            (330, _t('Document-out'))
        ],
        required=False,
        initial=0,
        coerce=int
    )
    idroute = ChoiceField([], required=False, initial='')
    frompartner = ChoiceField([], required=False)
    topartner = ChoiceField([], required=False)
    editype = ChoiceField(models.EDITYPESLIST, required=False)
    messagetype = ChoiceField(required=False)
    lastrun = BooleanField(required=False, initial=False)
    reference = CharField(required=False, label='Reference', max_length=70)

    def __init__(self, *args, **kwargs):
        super(SelectDocument, self).__init__(*args, **kwargs)
        self.fields['idroute'].choices = models.getroutelist()
        self.fields['messagetype'].choices = models.getoutmessagetypes()
        self.fields['frompartner'].choices = models.getpartners()
        self.fields['topartner'].choices = models.getpartners()


class ViewDocument(View):
    template = 'bots/document.html'
    action = 'document/'
    status = IntegerField(required=False, initial=0, widget=HIDDENINPUT())
    idroute = CharField(required=False, widget=HIDDENINPUT())
    frompartner = CharField(required=False, widget=HIDDENINPUT())
    topartner = CharField(required=False, widget=HIDDENINPUT())
    editype = CharField(required=False, widget=HIDDENINPUT())
    messagetype = CharField(required=False, widget=HIDDENINPUT())
    lastrun = BooleanField(required=False, initial=False, widget=HIDDENINPUT())
    reference = CharField(required=False, widget=HIDDENINPUT())


class SelectOutgoing(Select):
    template = 'bots/selectform.html'
    action = 'outgoing/'
    select_desc = 'outgoing files'
    statust = ChoiceField(
        [
            models.DEFAULT_ENTRY,
            ('1', "Error"),
            ('3', "Done"),
            ('4', "Resend")
        ],
        required=False,
        initial=''
    )
    idroute = ChoiceField([], required=False, initial='')
    tochannel = ChoiceField([], required=False)
    frompartner = ChoiceField([], required=False)
    topartner = ChoiceField([], required=False)
    editype = ChoiceField(models.EDITYPESLIST, required=False)
    messagetype = ChoiceField(required=False)
    filename = CharField(required=False, label='Filename', max_length=256)
    lastrun = BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super(SelectOutgoing, self).__init__(*args, **kwargs)
        self.fields['idroute'].choices = models.getroutelist()
        self.fields['messagetype'].choices = models.getoutmessagetypes()
        self.fields['frompartner'].choices = models.getpartners()
        self.fields['topartner'].choices = models.getpartners()
        self.fields['tochannel'].choices = models.gettochannels()


class ViewOutgoing(View):
    template = 'bots/outgoing.html'
    action = 'outgoing/'
    statust = IntegerField(required=False, initial='', widget=HIDDENINPUT())
    idroute = CharField(required=False, widget=HIDDENINPUT())
    tochannel = CharField(required=False, widget=HIDDENINPUT())
    frompartner = CharField(required=False, widget=HIDDENINPUT())
    topartner = CharField(required=False, widget=HIDDENINPUT())
    editype = CharField(required=False, widget=HIDDENINPUT())
    messagetype = CharField(required=False, widget=HIDDENINPUT())
    filename = CharField(required=False, widget=HIDDENINPUT())
    lastrun = BooleanField(required=False, initial=False, widget=HIDDENINPUT())


class SelectProcess(Select):
    template = 'bots/selectform.html'
    action = 'process/'
    select_desc = 'process errors'
    idroute = ChoiceField([], required=False, initial='')
    lastrun = BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super(SelectProcess, self).__init__(*args, **kwargs)
        self.fields['idroute'].choices = models.getroutelist()


class ViewProcess(View):
    template = 'bots/process.html'
    action = 'process/'
    idroute = CharField(required=False, widget=HIDDENINPUT())
    lastrun = BooleanField(required=False, initial=False, widget=HIDDENINPUT())


class SelectConfirm(Select):
    template = 'bots/selectform.html'
    action = 'confirm/'
    select_desc = 'confirmations'
    confirmtype = ChoiceField(models.CONFIRMTYPELIST, required=False, initial='0')
    confirmed = ChoiceField(
        [
            ('0', "All runs"),
            ('1', "Current run"),
            ('2', "Last run")
        ],
        required=False,
        initial='0'
    )
    idroute = ChoiceField([], required=False, initial='')
    editype = ChoiceField(models.EDITYPESLIST, required=False)
    messagetype = ChoiceField([], required=False)
    frompartner = ChoiceField([], required=False)
    topartner = ChoiceField([], required=False)
    fromchannel = ChoiceField([], required=False)
    tochannel = ChoiceField([], required=False)

    def __init__(self, *args, **kwargs):
        super(SelectConfirm, self).__init__(*args, **kwargs)
        self.fields['idroute'].choices = models.getroutelist()
        self.fields['messagetype'].choices = models.getallmessagetypes()
        self.fields['frompartner'].choices = models.getpartners()
        self.fields['topartner'].choices = models.getpartners()
        self.fields['fromchannel'].choices = models.getfromchannels()
        self.fields['tochannel'].choices = models.gettochannels()


class ViewConfirm(View):
    template = 'bots/confirm.html'
    action = 'confirm/'
    confirmtype = CharField(required=False, widget=HIDDENINPUT())
    confirmed = CharField(required=False, widget=HIDDENINPUT())
    idroute = CharField(required=False, widget=HIDDENINPUT())
    editype = CharField(required=False, widget=HIDDENINPUT())
    messagetype = CharField(required=False, widget=HIDDENINPUT())
    frompartner = CharField(required=False, widget=HIDDENINPUT())
    topartner = CharField(required=False, widget=HIDDENINPUT())
    fromchannel = CharField(required=False, widget=HIDDENINPUT())
    tochannel = CharField(required=False, widget=HIDDENINPUT())


class UploadFileForm(Form):
    file = FileField(label='Plugin to read', required=True, widget=FileInput(attrs={'size': '100'}))


class PlugoutForm(Form):
    databaseconfiguration = \
        BooleanField(required=False, initial=True, label='Database configuration',  help_text='Routes, channels, translations, partners, etc. from the database.')
    umlists = \
        BooleanField(required=False, initial=True, label='User code lists',         help_text='Your user code data from the database.')
    fileconfiguration = \
        BooleanField(required=False, initial=True, label='Script files',            help_text='[bots/usersys] Grammars, mapping scrips, routes scripts, etc.')
    infiles = \
        BooleanField(required=False, initial=True, label='Input files',             help_text='[botssys/infile] Example/test edi files.')
    charset = \
        BooleanField(required=False, initial=False, label='Edifact character sets', help_text='[bots/usersys/charsets] Seldom needed, only if changed.')
    databasetransactions = \
        BooleanField(required=False, initial=False, label='Database transactions',  help_text='Transaction details of all bots runs from the database. Only for support purposes, on request. May generate a very large plugin!')
    data = \
        BooleanField(required=False, initial=False, label='All transaction files',  help_text='[botssys/data] Copies of all incoming, intermediate and outgoing files. Only for support purposes, on request. May generate a very large plugin!')
    logfiles = \
        BooleanField(required=False, initial=False, label='Log files',              help_text='[botssys/logging] Log files from engine, webserver etc. Only for support purposes, on request.')
    config = \
        BooleanField(required=False, initial=False, label='Configuration files',    help_text='Your customised configuration files. Only for support purposes, on request.')
    database = \
        BooleanField(required=False, initial=False, label='SQLite database', help_text='Entire database file. Only for support purposes, on request. (Only works on Django websites using the SQLite backend)')


class DeleteForm(Form):
    delacceptance = \
        BooleanField(required=False, initial=True,  label='Delete transactions in acceptance testing', help_text='Delete runs, reports, incoming, outgoing, data files from acceptance testing.')
    deltransactions = \
        BooleanField(required=False, initial=True,  label='Delete transactions',                       help_text='Delete runs, reports, incoming, outgoing, data files.')
    deloutfile = \
        BooleanField(required=False, initial=False, label='Delete botssys/outfiles',                   help_text='Delete files in botssys/outfile.')
    delcodelists = \
        BooleanField(required=False, initial=False, label='Delete user code lists',                    help_text='Delete user code lists.')
    deluserscripts = \
        BooleanField(required=False, initial=False, label='Delete all user scripts',                   help_text='Delete all scripts in usersys (grammars, mappings etc) except charsets.')
    delinfile = \
        BooleanField(required=False, initial=False, label='Delete botssys/infiles',                    help_text='Delete files in botssys/infile.')
    delconfiguration = \
        BooleanField(required=False, initial=False, label='Delete configuration',                      help_text='Delete routes, channels, translations, partners etc.')
    delpersist = \
        BooleanField(required=False, initial=False, label='Delete persist',                            help_text='Delete the persist information.')
