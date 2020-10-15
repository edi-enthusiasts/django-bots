# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required, user_passes_test
from functools import partial
from . import views

login_required = partial(login_required, login_url='login')
admin.autodiscover()
staff_required = user_passes_test(lambda u: u.is_staff)
superuser_required = user_passes_test(lambda u: u.is_superuser)
run_permission = user_passes_test(lambda u: u.has_perm('bots.change_mutex'))

urlpatterns = patterns(
    '',
    url(r'^login.*', 'django.contrib.auth.views.login', {'template_name': 'bots/login.html'}, name='login'),
    url(r'^logout.*', 'django.contrib.auth.views.logout', {'next_page': 'home'}, name='logout'),
    url(r'^password_change/$', 'django.contrib.auth.views.password_change', name='password_change'),
    url(r'^password_change/done/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
    # login required
    url(r'^home.*', login_required(views.home), name='home'),
    url(r'^incoming.*', login_required(views.incoming), name='incoming'),
    url(r'^detail.*', login_required(views.detail), name='detail'),
    url(r'^process.*', login_required(views.process), name='process'),
    url(r'^outgoing.*', login_required(views.outgoing), name='outgoing'),
    url(r'^document.*', login_required(views.document), name='document'),
    url(r'^reports.*', login_required(views.reports), name='reports'),
    url(r'^confirm.*', login_required(views.confirm), name='confirm'),
    url(r'^filer.*', login_required(views.filer), name='filer'),
    url(r'^srcfiler.*', login_required(views.srcfiler), name='srcfiler'),
    # only staff
    url(r'^admin/$', login_required(views.home), name='admin'),  # do not show django admin root page
    url(r'^admin/bots/$', login_required(views.home), name='admin-bots'),  # do not show django admin root page
    url(r'^admin/', include(admin.site.urls)),
    url(r'^runengine.+', run_permission(views.runengine), name='runengine'),
    # only superuser
    url(r'^delete.*', superuser_required(views.delete), name='delete'),
    url(r'^plugin/index.*', superuser_required(views.plugin_index), name='plugin-index'),
    url(r'^plugin.*', superuser_required(views.plugin), name='plugin'),
    url(r'^plugout/index.*', superuser_required(views.plugout_index), name='plugout-index'),
    url(r'^plugout/backup.*', superuser_required(views.plugout_backup), name='plugout-backup'),
    url(r'^plugout.*', superuser_required(views.plugout), name='plugout'),
    url(r'^sendtestmail.*', superuser_required(views.sendtestmailmanagers), name='sendtestmail'),
    # catch-all
    url(r'^.*', 'bots.views.index', name='index'),
    )

handler500 = 'bots.views.server_error'
