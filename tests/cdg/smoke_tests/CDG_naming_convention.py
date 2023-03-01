#responsible agata.mastalska@globallogic.com
#Wroclaw

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service import register_to_network
import re

class Test(BaseTest):
    """
    Aim of this test is checking if software or midlet
    version is correctly named with CDG standard.

    1. check software version
    2. check currently running MIDlets
    3. check revision
    4. check a-revision
    5. check c-revision

    author: agata.mastalska@globallogic.com
    """

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("sw_type: {}, jrc_version: {}, c_revision_number: {}".format(test.sw_type, test.jrc_version, test.c_revision_number))
        #test.do_not_detete_midlets

    def run(test):
        module_with_midlet = ["JAKARTA", "BOXWOOD", "GINGER", "ODESSA"]
        module_with_siekret_command = ["WIRTANNEN", "ODESSA", "DAHLIA", "COUGAR", "KINGSTON"]
        types = ["RELEASE", "TRIAL", "CDG"]

        test.log.step("Test CDG naming convention")

        if test.sw_type in types:
            test.log.info("Software version parameter correct.")
            test.expect(True)
        else:
            test.log.error("Software version parameter wrong")
            test.log.error("Should be sw_type: RELEASE or TRIAL or CDG")
            test.expect(False, critical=True)

        if test.jrc_version in types:
            test.log.info("Midlet version parameter correct")
            test.expect(True)
        else:
            test.log.error("Midlet version parameter wrong")
            test.log.error("Should be jrc_version: RELEASE or TRIAL or CDG")
            test.expect(False, critical=True)

        if test.dut.project not in module_with_siekret_command:
            test.expect(test.dut.at1.send_and_verify("at^cicret=\"swn\""))
            software_version_response = test.dut.at1.last_response
        else:
            test.expect(test.dut.at1.send_and_verify("at^siekret=0"))
            software_version_response = test.dut.at1.last_response

        if test.dut.project in module_with_midlet:
            test.expect(test.dut.at1.send_and_verify("AT^SJAM=5"))
            midlet_version_response = test.dut.at1.last_response

        test.dut.at1.send_and_verify("ATI1", ".*OK.*")
        revision_number_response = test.dut.at1.last_response

        test.dut.at1.send_and_verify("ATI8", ".*OK.*")
        c_revision_number_response = test.dut.at1.last_response

        #######################################################################

        if "CDG" in test.jrc_version and "CDG" in test.sw_type:
            test.log.info("1.1) Changes in both software version and midlet.")
            if not check_CDG_software_version(software_version_response):
                test.log.error("Software version name is wrong with CDG standard")
                test.expect(False, critical=True)

            if test.dut.project in module_with_midlet:
                if not check_CDG_midlet_version(midlet_version_response):
                    test.log.error("JRC version name is wrong with CDG standard")
                    test.expect(False, critical=True)

            if not check_CDG_revision_number(revision_number_response):
                test.log.error("Revision number is wrong with CDG standard")
                test.expect(False, critical=True)

            if not check_CDG_c_revision_number(c_revision_number_response):
                test.log.error("C-Revision number is wrong with CDG standard")
                test.expect(False, critical=True)

        ########################################################################
        elif "CDG" not in test.jrc_version and "CDG" in test.sw_type:
            test.log.info("1.2) Changes only in software version.")
            if not check_CDG_software_version(software_version_response):
                test.log.error("Software version name is wrong with CDG standard. Software version response: \n {}".format(software_version_response))
                test.expect(False, critical=True)

            if test.dut.project in module_with_midlet:
                if not check_RELEASE_midlet_version(midlet_version_response):
                    test.log.error("JRC version name is wrong with CDG standard. Midlet version response: \n {}".format(midlet_version_response))
                    test.expect(False, critical=True)

            if not check_CDG_revision_number(revision_number_response):
                test.log.error("Revision number is wrong with CDG standard. Revision number response: \n {}".format(revision_number_response))
                test.expect(False, critical=True)

            if not check_CDG_c_revision_number(c_revision_number_response):
                test.log.error("C-Revision number is wrong with CDG standard. C-revision number response \n {}".format(c_revision_number_response))
                test.expect(False, critical=True)

        ########################################################################
        elif "CDG" in test.jrc_version and "CDG" not in test.sw_type:
            test.log.info("1.3) Changes only in midlet.")
            if not check_RELEASE_software_version(software_version_response):
                test.log.error("Software version name is wrong with CDG standard. Software version response: \n {}".format(software_version_response))
                test.expect(False, critical=True)

            if test.dut.project in module_with_midlet:
                if not check_CDG_midlet_version(midlet_version_response):
                    test.log.error("JRC version name is wrong with CDG standard. Midlet version response: \n {}".format(midlet_version_response))
                    test.expect(False, critical=True)

            if not check_CDG_revision_number(revision_number_response):
                test.log.error("Revision number is wrong with CDG standard. Revision number response: \n {}".format(revision_number_response))
                test.expect(False, critical=True)

            if not check_CDG_c_revision_number(c_revision_number_response):
                test.log.error("C-Revision number is wrong with CDG standard. C-revision number response \n {}".format(c_revision_number_response))
                test.expect(False, critical=True)

        ########################################################################
        elif "TRIAL" in test.jrc_version and "TRIAL" in test.sw_type:
            test.log.info("2.1) Changes in both software version and midlet.")
            if test.base_version == "CDG":
                test.log.info("In TRIAL, software version name should be correct with CDG standard.")
                if not check_CDG_software_version(software_version_response):
                    test.log.error("Software version name is wrong with CDG standard. Software version response: \n {}".format(software_version_response))
                    test.expect(False, critical=True)
            else:
                if not check_TRIAL_software_version(software_version_response):
                    test.log.error("Software version name is wrong with TRIAL standard. Software version response: \n {}".format(software_version_response))
                    test.expect(False, critical=True)

            if test.dut.project in module_with_midlet:
                if not check_TRIAL_midlet_version(midlet_version_response):
                    test.log.error("JRC version name is wrong with TRIAL standard. Midlet version response: \n {}".format(midlet_version_response))
                    test.expect(False, critical=True)

            if not check_TRIAL_revision_number(revision_number_response):
                test.log.error("Revision number is wrong with TRIAL standard. Revision number response: \n {}".format(revision_number_response))
                test.expect(False, critical=True)

            if not check_TRIAL_c_revision_number(c_revision_number_response):
                test.log.error("C-Revision number is wrong with TRIAL standard. C-revision number response \n {}".format(c_revision_number_response))
                test.expect(False, critical=True)

        ########################################################################
        elif "TRIAL" not in test.jrc_version and "TRIAL" in test.sw_type:
            test.log.info("2.2) Changes only in software version.")
            if test.base_version == "CDG":
                test.log.info("In TRIAL, software version name should be correct with CDG standard.")
                if not check_CDG_software_version(software_version_response):
                    test.log.error("Software version name is wrong with CDG standard. Software version response: \n {}".format(software_version_response))
                    test.expect(False, critical=True)
            else:
                if not check_TRIAL_software_version(software_version_response):
                    test.log.error("Software version name is wrong with TRIAL standard. Software version response: \n {}".format(software_version_response))
                    test.expect(False, critical=True)

            if test.dut.project in module_with_midlet:
                if not check_RELEASE_midlet_version(midlet_version_response):
                    test.log.error("JRC version name is wrong with TRIAL standard. Midlet version response: \n {}".format(midlet_version_response))
                    test.expect(False, critical=True)

            if not check_TRIAL_revision_number(revision_number_response):
                test.log.error("Revision number is wrong with TRIAL standard. Revision number response: \n {}".format(revision_number_response))
                test.expect(False, critical=True)

            if not check_TRIAL_c_revision_number(c_revision_number_response):
                test.log.error("C-Revision number is wrong with TRIAL standard. C-revision number response \n {}".format(c_revision_number_response))
                test.expect(False, critical=True)

        ########################################################################
        elif "TRIAL" in test.jrc_version and "TRIAL" not in test.sw_type:
            test.log.info("2.3) Changes only in midlet.")
            if not check_TRIAL_software_version(software_version_response):
                test.log.error("Software version name is wrong with TRIAL standard. Software version response: \n {}".format(software_version_response))
                test.expect(False, critical=True)

            if test.dut.project in module_with_midlet:
                if not check_TRIAL_midlet_version(midlet_version_response):
                    test.log.error("JRC version name is wrong with TRIAL standard. Midlet version response: \n {}".format(midlet_version_response))
                    test.expect(False, critical=True)

            if not check_RELEASE_revision_number(revision_number_response):
                test.log.error("Revision number is wrong with TRIAL standard. Revision number response: \n {}".format(revision_number_response))
                test.expect(False, critical=True)

            if not check_TRIAL_c_revision_number(c_revision_number_response):
                test.log.error("C-Revision number is wrong with TRIAL standard. C-revision number response \n {}".format(c_revision_number_response))
                test.expect(False, critical=True)

        ########################################################################
        else:
            test.log.info("No changes in both software version and midlet.")
            if not check_RELEASE_software_version(software_version_response):
                test.log.error("Software version name is wrong with RELEASE standard. Software version response: \n {}".format(software_version_response))
                test.expect(False, critical=True)

            if test.dut.project in module_with_midlet:
                if not check_RELEASE_midlet_version(midlet_version_response):
                    test.log.error("JRC version name is wrong with RELEASE standard. Midlet version response: \n {}".format(midlet_version_response))
                    test.expect(False, critical=True)

            if not check_RELEASE_revision_number(revision_number_response):
                test.log.error("Revision number is wrong with RELEASE standard. Revision number response: \n {}".format(revision_number_response))
                test.expect(False, critical=True)

            if not check_RELEASE_c_revision_number(c_revision_number_response):
                test.log.error("C-Revision number is wrong with RELEASE standard. C-revision number response \n {}".format(c_revision_number_response))
                test.expect(False, critical=True)

        if test.c_revision_number:
            if not check_if_c_revision_number_is_correct(c_revision_number_response, test.c_revision_number):
                test.log.error("C-Revision number is wrong with c_revision_number given from campaign")
                test.expect(False, critical=True)

        test.expect(True)

    def cleanup(test):
        test.dut.at1.close()

if "__main__" == __name__:
    unicorn.main()

def check_CDG_software_version(response):
    pattern = re.compile(r'.+-CDG-\d\d\d\d\d-\d\d RELEASE')
    result = pattern.search(response)

    if result is not None:
        return True
    else:
        return False

def check_CDG_midlet_version(response):
    pattern = re.compile(r':/JRC-[0-9.]+_crn\d{5}[.]\d{2}[.]jad')
    result = pattern.search(response)

    if result is not None:
        return True
    else:
        return False

def check_CDG_revision_number(response):
    return check_RELEASE_revision_number(response)

def check_CDG_c_revision_number(response):
    return check_TRIAL_c_revision_number(response)

def check_TRIAL_software_version(response):
    return check_RELEASE_software_version(response)

def check_TRIAL_midlet_version(response):
    pattern = re.compile(r':/JRC-[0-9.]+_crn\d{5}[.]\d{2}-trial[.]jad')
    result = pattern.search(response)

    if result is not None:
        return True
    else:
        return False

def check_TRIAL_revision_number(response):
    pattern = re.compile(r'REVISION \d\d[.]\d\d\d-TRIAL\s+A-REVISION \d\d[.]\d\d\d[.]\d\d\s+OK')
    result = pattern.search(response)

    if result is not None:
        return True
    else:
        return False

def check_TRIAL_c_revision_number(response):
    pattern = re.compile(r'C-REVISION \d\d\d\d\d[.]\d\d\s+OK')
    result = pattern.search(response)

    if result is not None:
        return True
    else:
        return False

def check_RELEASE_software_version(response):
    pattern = re.compile(r'CDG|TRIAL')
    result = pattern.search(response)

    if result is None:
        return True
    else:
        return False

def check_RELEASE_midlet_version(response):
    pattern = re.compile(r':/JRC-\d[.]\d\d[.]\d\d[.]jad')
    result = pattern.search(response)

    if result is not None:
        return True
    else:
        return False

def check_RELEASE_revision_number(response):
    pattern = re.compile(r'REVISION \d\d[.]\d\d\d\s+A-REVISION \d\d[.]\d\d\d[.]\d\d\s+OK')
    result = pattern.search(response)

    if result is not None:
        return True
    else:
        return False

def check_RELEASE_c_revision_number(response):
    pattern = re.compile(r'(ati8|ATI8)\s+OK')
    result = pattern.search(response)

    if result is not None:
        return True
    else:
        return False

def check_if_c_revision_number_is_correct(response, c_revision_number):
    pattern = re.compile(r'\d\d\d\d\d[.]\d\d')
    result = pattern.search(c_revision_number)
    if result is None:
        c_revision_number = "000" + c_revision_number

    if c_revision_number in response:
        return True
    else:
        return False
