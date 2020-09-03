#!/usr/bin/env python2
import sys
import platform
import os
import re


def check_debian_plain(distinfo={}):
# objectives:
#   - figure out whether we're in debian or devuan
#   - python-version-agnostic
#   - only use basic python facilities (as few
#     external modules/libraries as possible
# Algorithm:
# - if platform.linux_distribution has been run,
#     pass the info via distinfo
# - first read /etc/issue to get the dist id
# - read /etc/apt/sources.list:
#   - find the first non-commented line
#   - construct the base filename for the list
#   - search in /var/lib/apt/lists for [base_filename]*Release
#     (Q: why _Release in debian and _InRelease in devuan?)
#   - take the first file found
#   - extract the required info from the top of the file
# TODO:
#   - what if we can't find the files? Need to return something
#     which won't break what comes after.
#   - possible problem with initial-capitalization of ID
#     for now, stick with whatever we get from the files (which
#     in itself is inconsistent)
#   - general robustification:
#     - dodge cdrom lines in /etc/apt/sources.list
#     - pre-check existence of all files which we need to use
#       (don't assume anything)
#     - figure out how to report an error (waagent has a module to do this)
######################################################################
# Development log:
# ===============
# 2020-08-12:
# -----------
# Start preparing for inclusion in peter9370 WALinuxAgent fork
# Objectives:
#   1) In future.py, ensure that osinfo is only amended if devuan is 
#      detected. In all other cases, osinfo should remain as given.
#   2) Check that the python code is optimal and idiomatic.
######################################################################
    localdistinfo={
        'ID' : '',
        'RELEASE' : '',
        'CODENAME' : '',
        'DESCRIPTION' : '',
    }
# copy in any data which have already been ascertained:
    for k in localdistinfo.keys():
        if k in distinfo:
#            print("distinfo."+k+"="+distinfo[k])
            localdistinfo['ID']=distinfo[k]
    aptdir="/var/lib/apt/lists/"
# what do we do if /etc/issue doesn't exist
# or has been customised?
# maybe /etc/dpkg/origins/default would be a better bet
#    issuefile=open("/etc/issue")
#    issueline=issuefile.read().strip()
#    issuefile.close()
#    distid=issueline.split()[0]
    distid=""
#
# 1) Get the distribution ID from /etc/dpkg/origins/default
#
    if not os.path.isfile("/etc/dpkg/origins/default"):
# can't find the file - give up
# (need to report an error here)
        return localdistinfo
    originsfile=open("/etc/dpkg/origins/default","r")
    sline=""
    for line in originsfile:
        if re.search("^Vendor:",line):
            sline=line
            break
    sline=sline.strip()
    if sline=="":
# didn't find a "Vendor:" line - give up
        return localdistinfo
    originsfile.close()
    distid=sline.split()[1]
#    print("distid="+distid)
#
# 2) Get the release file from /etc/apt/sources.list
# (use the first line starting with "deb")
#
    if not os.path.isfile("/etc/apt/sources.list"):
# no sources.list file - just return what we were given
# 
        return localdistinfo
# FIXME: this causes a problem with python 3 - the test suite throws up 
# "unclosed file" warnings (in spite of the explicit close).
# Allegedly, using "with open('filename') as filehandle" fixes this. But
# how to ensure compatibility with python 2?  
    slfile=open("/etc/apt/sources.list","r")
    sline=""
    for line in slfile:
# skip lines relating to a cdrom
        if re.search("cdrom:",line):
            continue
# NB following will only work for non-commented lines:
        if re.search("^deb",line):
            sline=line
            break

    slfile.close
    sline=sline.strip();
    if sline=="":
# couldn't find an appropriate line - give up
        return localdistinfo
#    print("sline="+sline)
    deb,url,codename,domain=sline.split(' ')
#    print("url="+url+" codename="+codename)
# extract the host and dir from the url:
    parts=re.search('^http:\/\/(.*?)\/(.*)',url)
    host=parts.group(1)
    section=parts.group(2)
    if re.search('\/$',section):
        section=section[:-1]
#    print("host="+host+" section="+section)
# assemble the speculative filename
# apparently if it's devuan, the file will end in _InRelease,
# if debian, _Release. Don't know why.
#
# 3) Get the release from the apt list file
#
    filename=host+'_'+section+'_dists_'+codename+'_'
    if distid=="Devuan":
        filename=filename+'InRelease'
    else:
        filename=filename+'Release'
#    print("filename = "+aptdir+filename)
    if os.path.isfile(aptdir+filename):
#        print("Found file")
# now examine the file to get the release.
# Should be in the first few lines - need a test to avoid having
# to rummage needlessly through what might be a very big file.
# - once we've got the line starting "Version:" - stop reading
# - if we see a line which ends with "Packages" - stop reading
# REVISIT: this test may not work in all cases.
        relfile=open(aptdir+filename,"r")
        version=""
        for line in relfile:
            if re.search('Packages$',line):
                break
            parts = re.search('Version: (.*)',line)
            if parts:
                version=parts.group(1)
                break
        relfile.close()
        if version == "":
            print("ERROR: unable to find version")
#        else:
#            print("Version = '"+version+"'")
    else:
        print("ERROR: cannot find file "+relfile)
#  Update localdistinfo with the results found:
#  REVISIT: what if our search didn't retrieve information, and
#  a key in distinfo was already populated?
    localdistinfo['ID']=distid
    localdistinfo['RELEASE']=version
    localdistinfo['CODENAME']=codename
    localdistinfo['DESCRIPTION']=distid+' GNU/Linux '+version+' ('+codename+')'
    return localdistinfo

def test():
# need to do this using the actual output from platform.linux_distribution
    distinfo_proto={
        'ID' : "",
        'RELEASE' : "",
        'CODENAME' : "",
    }
# get what we can this:
# (format of result is (distname,version,id))
# NB: platform.linux_distribution is deprecated (and will be removed in
# python 3.8. Suggestion is to use the distro package (but the online
# documentation about this is currently a complete mess - JMHO)
    platforminfo=platform.linux_distribution()
    print("platforminfo:")
    print(platforminfo)
# if we got anything vaguely useful, copy it into distinfo_proto
    if platforminfo[0]!='':
        distinfo_proto['ID']=platforminfo[0]
    if platforminfo[1]!='':
        distinfo_proto['RELEASE']=platforminfo[1]
# what about the third element?
    print("(before ***** start ******)")
    print(distinfo_proto)
    print("(before ***** end ******)")
# NB: for actual use, we can construct the dictionary in the
# function call (no need to use a pre-constructed dictionary)
    distinfo_actual=check_debian_plain(distinfo_proto)
    print("(after ***** start ******)")
    print(distinfo_actual)
    print("(after ***** end ******)")

if __name__ == "__main__":
    test()

