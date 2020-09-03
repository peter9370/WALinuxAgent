# Copyright 2018 Microsoft Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Requires Python 2.6+ and Openssl 1.0+
#


from distutils.version import LooseVersion as Version

import azurelinuxagent.common.logger as logger
from azurelinuxagent.common.version import DISTRO_NAME, DISTRO_CODE_NAME, DISTRO_VERSION, DISTRO_FULL_NAME
from .alpine import AlpineOSUtil
from .arch import ArchUtil
from .bigip import BigIpOSUtil
from .clearlinux import ClearLinuxUtil
from .coreos import CoreOSUtil
from .debian import DebianOSBaseUtil, DebianOSModernUtil
from .devuan import Devuan21OSUtil
from .default import DefaultOSUtil
from .freebsd import FreeBSDOSUtil
from .gaia import GaiaOSUtil
from .iosxe import IosxeOSUtil
from .nsbsd import NSBSDOSUtil
from .openbsd import OpenBSDOSUtil
from .openwrt import OpenWRTOSUtil
from .redhat import RedhatOSUtil, Redhat6xOSUtil
from .suse import SUSEOSUtil, SUSE11OSUtil
from .ubuntu import UbuntuOSUtil, Ubuntu12OSUtil, Ubuntu14OSUtil, \
    UbuntuSnappyOSUtil, Ubuntu16OSUtil, Ubuntu18OSUtil
from azurelinuxagent.common.extralib.check_debian_plain import check_debian_plain


def get_osutil(distro_name=DISTRO_NAME,
               distro_code_name=DISTRO_CODE_NAME,
               distro_version=DISTRO_VERSION,
               distro_full_name=DISTRO_FULL_NAME):

    # We are adding another layer of abstraction here since we want to be able to mock the final result of the
    # function call. Since the get_osutil function is imported in various places in our tests, we can't mock
    # it globally. Instead, we add _get_osutil function and mock it in the test base class, AgentTestCase.
    return _get_osutil(distro_name, distro_code_name, distro_version, distro_full_name)


def _get_osutil(distro_name, distro_code_name, distro_version, distro_full_name):

    if distro_name == "arch":
        return ArchUtil()

    if "Clear Linux" in distro_full_name:
        return ClearLinuxUtil()

    if distro_name == "ubuntu":
        if Version(distro_version) in [Version("12.04"), Version("12.10")]:
            return Ubuntu12OSUtil()
        elif Version(distro_version) in [Version("14.04"), Version("14.10")]:
            return Ubuntu14OSUtil()
        elif Version(distro_version) in [Version('16.04'), Version('16.10'), Version('17.04')]:
            return Ubuntu16OSUtil()
        elif Version(distro_version) in [Version('18.04'), Version('18.10'),
                                         Version('19.04'), Version('19.10'),
                                         Version('20.04')]:
            return Ubuntu18OSUtil()
        elif distro_full_name == "Snappy Ubuntu Core":
            return UbuntuSnappyOSUtil()
        else:
            return UbuntuOSUtil()

    if distro_name == "alpine":
        return AlpineOSUtil()

    if distro_name == "kali":
        return DebianOSBaseUtil()

    if distro_name == "coreos" or distro_code_name == "coreos":
        return CoreOSUtil()

    if distro_name in ("suse", "sles", "opensuse"):
        if distro_full_name == 'SUSE Linux Enterprise Server' \
                and Version(distro_version) < Version('12') \
                or distro_full_name == 'openSUSE' and Version(distro_version) < Version('13.2'):
            return SUSE11OSUtil()
        else:
            return SUSEOSUtil()

    if distro_name == "debian":
# check if this is really devuan:
        protodistinfo = {
          'ID' : distro_name,
          'RELEASE' : distro_version,
          'CODENAME' : distro_code_name,
          'DESCRIPTION' : distro_full_name,
        }
        checkeddistinfo = check_debian_plain(protodistinfo)
        if checkeddistinfo['ID'] == "devuan":
# (Currently not checking release - at the moment, the only thing that
# we need to know is that it's devuan, so no systemd)
            return Devuan21OSUtil()
        else:            
            if "sid" in distro_version or Version(distro_version) > Version("7"):
                return DebianOSModernUtil()
            else:
                return DebianOSBaseUtil()

    if distro_name == "devuan":
        return Devuan21OSUtil()

    if distro_name == "redhat" \
            or distro_name == "centos" \
            or distro_name == "oracle":
        if Version(distro_version) < Version("7"):
            return Redhat6xOSUtil()
        else:
            return RedhatOSUtil()

    if distro_name == "euleros":
        return RedhatOSUtil()

    if distro_name == "freebsd":
        return FreeBSDOSUtil()

    if distro_name == "openbsd":
        return OpenBSDOSUtil()

    if distro_name == "bigip":
        return BigIpOSUtil()

    if distro_name == "gaia":
        return GaiaOSUtil()

    if distro_name == "iosxe":
        return IosxeOSUtil()

    if distro_name == "nsbsd":
        return NSBSDOSUtil()

    if distro_name == "openwrt":
        return OpenWRTOSUtil()

    else:
        logger.warn("Unable to load distro implementation for {0}. Using "
                    "default distro implementation instead.",
                    distro_name)
        return DefaultOSUtil()
