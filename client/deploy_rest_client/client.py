#!/usr/bin/python
# -*- coding: utf-8 -*-

from  requests.packages import urllib3
# cure: Certificate for localhost has no `subjectAltName`
urllib3.disable_warnings()
from requests import put, get, delete, post
import os, sys
import imp
from opster import command
from cPickle import dump, load

import constant
from localization import get_to_text as _

# localdir
rootdir = os.path.dirname(constant.__file__)
# config file
conf = imp.load_source("conf", rootdir+"/client.conf")
# REST link
Rurl = "https://{host}:{port}".format(host=conf.RHost, port=conf.RPort)
# pem for https
cafile = rootdir+"/"+conf.RKey


class Pickle(object):

    def __init__(self):
        self.__pickdir = rootdir+"/pickle"
        self.__pickfile = "login.pickle"

    def pload(self):
        if self.__pickfile in os.listdir(self.__pickdir):
            _file = open("%s/%s"%(self.__pickdir, self.__pickfile), "r")
            _out = load(_file)
            _file.close()
            return _out
        else:
            return False

    def pdump(self, _data):
        _file = open("%s/%s"%(self.__pickdir, self.__pickfile), "w")
        dump(_data, _file, 2)
        _file.close()


class Json2text(object):

    def __init__(self, _list):
        self.inlist = _list

    def text(self):
        all_num = 0
        for _str in self.inlist:
            all_num += 1
            print "___________________"
            print _("Position N {}").format(str(all_num))
            print "___________________"
            _keys = [_key for _key in _str.keys()]
            _keys.sort()
            for _key in _keys:
                if type(_str[_key]) is not list and \
                        _str[_key] and \
                        _key != "log" and \
                        _key != "jobs":
                    print "%s: %s"%(constant.j2t[_key], _str[_key])
                elif type(_str[_key]) is list and\
                          _str[_key] != [] and\
                          _key != "jobs":
                    print "%s:"%(constant.j2t[_key])
                    print "---------------"
                    for _substr in _str[_key]:
                        print _substr
                elif _key == "log" and _str[_key] != "":
                    print "%s:"%(constant.j2t[_key])
                    print "---------------"
                    print _str[_key]
                    print "---------------"
                elif _str[_key] and _key == "jobs":
                    print "%s:"%(constant.j2t[_key])
                    print "------------------------------------"
                    Json2text(_str[_key]).text()
                    print "------------------------------------"


@command(usage='%name <args>',
        options=[
            ('C', 'Create', False, _('Create new login and password to client')),
            ('U', 'Update', False, _('Update password to server dataase for auth user')),
            ('I', 'Info', False, _('Info from all jobs')),
            ('l', 'login', u"", _('Set user login')),
            ('p', 'passwd', u"", _('Set user password')),
            ('j', 'job', 0, _('Set job number for info in base of auth user'))])
def user_comms(Create, Update, Info, login, passwd, job):
    plogin = Pickle().pload()
    if Create and not Update and not Info and login and passwd:
        # create user and password
        try:
            _rest = put(Rurl+'/user', verify=cafile,
                        data={"name": login,
                              "key": passwd})
        except:
            print _("REST ERR: Server not available")
        else:
            if _rest.status_code == 201:
                Pickle().pdump({"uname": login, "ukey": passwd})
                print _("REST OK: Login and password added")
            else:
                print _("REST ERR {}: Create user false").format(_rest.status_code)
    elif not Create and Update and not Info and passwd:
        # update user and password
        if plogin:
            try:
                _rest = put(Rurl+'/user', verify=cafile,
                            data={"name": plogin["uname"],
                                  "key": plogin["ukey"],
                                  "newkey": passwd})
            except:
                print _("REST ERR: Server not available")
            else:
                if _rest.status_code == 201:
                    Pickle().pdump({"uname": plogin["uname"], "ukey": passwd})
                    print _("REST OK: Password update")
                elif _rest.status_code == 401:
                    print _("REST ERR {}: Authorization failed").format(_rest.status_code)
                else:
                    print _("REST ERR {}: Password update failed").format(_rest.status_code)
        else:
            print _("User name and password not found, authorization please")
    elif not Create and not Update and Info:
        # job(s) info from user
        if plogin:
            try:
                _rest = get(Rurl+'/user', verify=cafile,
                            data={"name": plogin["uname"],
                                "jnum": job})
            except:
                print _("REST ERR: Server not available")
            else:
                if _rest.status_code == 200:
                    Json2text(_rest.json()).text()
                else:
                    print _("REST ERR {}: Request error").format(_rest.status_code)
        else:
            print _("User name and password not found, authorization please")
    else:
        print _("Please select: Create(-C) or Update(-U) or Info(-I) only")


@command(usage='%name <args>',
        options=[
            ('J', 'Jobs', False, _('Get info from all jobs')),
            ('S', 'Sources', False, _('Get info from all sources')),
            ('P', 'Packages', False, _('Get info from all packages')),
            ('v', 'verbose', False, _('Get verbose info'))])
def info_comms(Jobs, Sources, Packages, verbose):
    if Sources and not Packages and not Jobs:
        _domain = "src"
    elif not Sources and Packages and not Jobs:
        _domain = "pkg"
    elif not Sources and not Packages and Jobs:
        _domain = "user"
    else:
        _domain = False
        print _("Please select: Jobs(-J) or Sources(-S) or Packages(-P) only")

    if _domain:
        try:
            _rest = get(Rurl+'/info', verify=cafile,
                        data={"domain": _domain, "detail": int(verbose)})
        except:
            print _("REST ERR: Server not available")
        else:
            if _rest.status_code == 200:
                Json2text(_rest.json()).text()
            else:
                print _("REST ERR {}: Request error").format(_rest.status_code)


@command(usage='%name <args>',
        options=[
            ('C', 'Create', False, _('Create new source from git clone or update')),
            ('D', 'Delete', False, _('Delete source catalog and packages derictories')),
            ('I', 'Info', False, _('Version info from this source')),
            ('n', 'name', u"", _('Set name as git link or source name'))])
def src_comms(Create, Delete, Info, name):
    plogin = Pickle().pload()
    if Create and not Delete and not Info and name:
        # create source
        if plogin:
            try:
                _rest = put(Rurl+'/domain/src', verify=cafile,
                            data={"name": name,
                                  "uname": plogin["uname"],
                                  "ukey": plogin["ukey"]})
            except:
                print _("REST ERR: Server not available")
            else:
                if _rest.status_code == 201:
                    print _("REST OK: Task queued")
                elif _rest.status_code == 401:
                    print _("REST ERR {}: Authorization failed").format(_rest.status_code)
                else:
                    print _("REST ERR {}: Request error").format(_rest.status_code)
        else:
            print _("User name and password not found, authorization please")
    elif not Create and Delete and not Info and name:
        # delete source
        if plogin:
            try:
                _rest = delete(Rurl+'/domain/src', verify=cafile,
                            data={"name": name,
                                  "uname": plogin["uname"],
                                  "ukey": plogin["ukey"]})
            except:
                print _("REST ERR: Server not available")
            else:
                if _rest.status_code == 204:
                    print _("REST OK: Task queued")
                elif _rest.status_code == 401:
                    print _("REST ERR {}: Authorization failed").format(_rest.status_code)
                else:
                    print _("REST ERR {}: Request error").format(_rest.status_code)
        else:
            print _("User name and password not found, authorization please")
    elif not Create and not Delete and Info and name:
        # info source versions
        try:
            _rest = get(Rurl+'/domain/src', verify=cafile,
                        data={"name": name})
        except:
            print _("REST ERR: Server not available")
        else:
            if _rest.status_code == 200:
                Json2text(_rest.json()).text()
            else:
                print _("REST ERR {}: Request error").format(_rest.status_code)
    else:
        # opster error
        print _("Please select: Create(-C) or Delete(-D) or Info(-I) only and use name(-n)")


@command(usage='%name <args>',
        options=[
            ('B', 'Build', False, _('Build packages from name, version and digit')),
            ('D', 'Delete', False, _('Delete all file from name, digit (and version)')),
            ('I', 'Info', False, _('Files info from name, version and digit')),
            ('F', 'File', u"", _('File view from file name, version and digit')),
            ('n', 'name', u"", _('Set programm name')),
            ('v', 'version', u"", _('Set programm version')),
            ('d', 'digit', 0, _('Set programm digit'))])
def pkg_comms(Build, Delete, Info, File, name, version, digit):
    plogin = Pickle().pload()
    if Build and not Delete and not Info and not File and name and version and digit:
        # build packages
        if plogin:
            try:
                _rest = put(Rurl+'/domain/pkg', verify=cafile,
                            data={"name": name,
                                  "dig": digit,
                                  "ver": version,
                                  "uname": plogin["uname"],
                                  "ukey": plogin["ukey"]})
            except:
                print _("REST ERR: Server not available")
            else:
                if _rest.status_code == 201:
                    print _("REST OK: Task queued")
                elif _rest.status_code == 401:
                    print _("REST ERR {}: Authorization failed").format(_rest.status_code)
                else:
                    print _("REST ERR {}: Request error").format(_rest.status_code)
        else:
            print _("User name and password not found, authorization please")
    elif not Build and Delete and not Info and not File and name and digit:
        # delete package
        if plogin:
            try:
                _rest = delete(Rurl+'/domain/pkg', verify=cafile,
                            data={"name": name,
                                  "dig": digit,
                                  "ver": version,
                                  "uname": plogin["uname"],
                                  "ukey": plogin["ukey"]})
            except:
                print _("REST ERR: Server not available")
            else:
                if _rest.status_code == 204:
                    print _("REST OK: Task queued")
                elif _rest.status_code == 401:
                    print _("REST ERR {}: Authorization failed").format(_rest.status_code)
                else:
                    print _("REST ERR {}: Request error").format(_rest.status_code)
        else:
            print _("User name and password not found, authorization please")
    elif not Build and not Delete and Info and not File and name:
        # info to files in package
        try:
            _rest = get(Rurl+'/domain/pkg', verify=cafile,
                        data={"name": name,
                              "dig": digit,
                              "ver": version})
        except:
            print _("REST ERR: Server not available")
        else:
            if _rest.status_code == 200:
                Json2text(_rest.json()).text()
            else:
                print _("REST ERR {}: Request error").format(_rest.status_code)
    elif not Build and not Delete and not Info and File and name and version and digit:
        try:
            _rest = get(Rurl+'/domain/pkg', verify=cafile,
                        data={"name": name,
                              "dig": digit,
                              "ver": version})
        except:
            print _("REST ERR: Server not available")
        else:
            if _rest.status_code == 200:
                for _str in _rest.json():
                    if _str["fname"] == File:
                        if _str["type"] == "log":
                            try:
                                _srest = post(Rurl+'/out', verify=cafile,
                                              data={"prog": name,
                                                    "dig": digit,
                                                    "ver": version,
                                                    "fname": File})
                            except:
                                print _("REST ERR: Server not available")
                            else:
                                if _srest.status_code == 201:
                                    print _srest.json()
                                elif _srest.status_code == 404:
                                    print _("REST ERR {_state}: File {_file} not found"
                                            ).format(_state=_srest.status_code, _file=File)
                                else:
                                    print _("REST ERR POST {}: Request error"
                                            ).format(_srest.status_code)
                        else:
                            print _("ERR: File {} not log - not view").format(File)
            else:
                print _("REST ERR GET {}: Request error").format(_rest.status_code)
    else:
        # opster error
        print _("Please select: Build(-B) or Delete(-D) or Info(-I) or File(-F)")


def Run(_argv=False):
    if not _argv:
        _argv = sys.argv
    AllComm = {}
    try:
        AllComm['command'] = ''.join(_argv[1])
    except:
        AllComm['command'] = "No command"
    else:
        SysArgs = _argv[2:]

    #enter comstring 1-st command
    if AllComm['command'] == "user":
        user_comms.command(SysArgs)
    elif AllComm['command'] == "info":
        info_comms.command(SysArgs)
    elif AllComm['command'] == "src":
        src_comms.command(SysArgs)
    elif AllComm['command'] == "pkg":
        pkg_comms.command(SysArgs)
    else:
        print _("""
        not valid comm string parameters
        please use:
            client.py user -h
            client.py info -h
            client.py src -h
            client.py pkg -h
        """)


if __name__ == "__main__":
    Run()
