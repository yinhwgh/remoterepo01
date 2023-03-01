# responsible: karsten.labuske@thalesgroup.com, johann.suhr@thalesgroup.com
# location: Berlin
# test case: UNISIM01-250

import unicorn
from core.basetest import BaseTest

import os
import subprocess
import json
import unicorn
from dstl.miscellaneous.mods_e2e_unicorn_support import *
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
import tests.device_management.iot_service_agent.mods_e2e_unicorn_server_config as server_config


class SubscriptionReport(BaseTest):
    """
    Class to call the REST API of SMDP+
    """

    def setup(test):
        test.require_parameter('iot_suite_organization', default='Unicorn')
        test.require_parameter('iccid_lists', default=['iccids_siminn_gcp.txt',
                                                       'iccids_siminn-1_gcp.txt',
                                                       'iccids_siminn_gcp_dev.txt',
                                                       'iccids_transatel_gcp.txt',
                                                       'iccids_3gpp_rohde_schwarz_gcp.txt'])
        test.src = SmdpRESTClient()

        # setup proxy dict
        global proxy_dict
        proxy_dict = dict(os.environ)
        proxy_dict["https_proxy"] = "proxy-fr-croissy.gemalto.com:8080"

        # read all subscriptions from Cinterion IoT Suite
        global mods_subs
        r = get_subscriptions()
        mods_subs = r.json()
        # test.log.info("Subscriptions Cinterion IoT Suite:\n " + json.dumps(mods_subs, indent=4, sort_keys=True))

        # read all devices from Cinterion IoT Suite
        global mods_devices
        r = get_devices()
        mods_devices = r.json()
        # test.log.info("Devices Cinterion IoT Suite:\n " + json.dumps(mods_devices, indent=4, sort_keys=True))

        # assemble an EID/IMEI dict from the device long listing
        global eid_dict
        eid_dict = dict()
        for i in range(len(mods_devices)):
            dev = mods_devices[i]
            r = get_device_long(dev['id'])
            info = r.json()

            try:
                eid = info['shadow']['reportedState']['instances']['33096']['0']['0']
                eid_dict[info['shadow']['reportedState']['instances']['33096']['0']['0']] = dev[
                    'imei']
            except KeyError:
                pass

        test.log.info("EID/IMEI Dict: " + str(len(eid_dict)) + " entries")
        test.log.info(eid_dict.items())

        pass

    def run(test):
        test.log.com("")
        test.log.com(
            '*************************************************************************************************************************')
        test.log.com("* Devices on Cinterion IoT Suite: " + str(len(mods_devices)))
        test.log.com("* Subscriptions on Cinterion IoT Suite: " + str(len(mods_subs)))
        test.log.com(
            '*************************************************************************************************************************')
        test.log.com("")

        # create subscription reports
        iccid_lists = test.get('iccid_lists')
        for iccid_list in iccid_lists:
            test.log.info("iccid_list:" + iccid_list )
            test.read_status_from_file(test, iccid_list, iccid_list)

        # create EID report
        test.create_eid_report(test)

    def create_eid_report(self, test):
        test.log.com("")
        test.log.com(
            '*************************************************************************************************************************')
        test.log.com("* SM-DP+ subscriptions per EID (EID's found on Cinterion IoT Suite)")
        test.log.com(
            '*************************************************************************************************************************')
        test.log.com("* IMEI            / EID\t\t\t\t\t\t\t\t\t# of profiles")
        test.log.com(
            '*************************************************************************************************************************')

        for key in eid_dict:
            result = test.src.get_eid_info(key, log_status=False)

            # convert to JSON object
            out_json = result.json()
            # test.log.info("response: " + json.dumps(out_json, indent=4, sort_keys=True))
            status = out_json['header']['functionExecutionStatus']['status']
            if (status == "Failed"):
                test.log.com("* " + str(eid_dict[key]) + " / " + str(key) + "\t" +
                             out_json['header']['functionExecutionStatus']['statusCodeData'][
                                 'message'])
                # test.log.com("* " + str(eid_dict[key]) + " / " + str(key) + "\tNo Profiles")
            else:
                profiles = out_json['profiles']
                test.log.com("* " + str(eid_dict[key]) + " / " + str(key) + "\tProfiles: " + str(
                    len(profiles)))
                for profile in profiles:
                    test.log.com("*\t\tICCID: " + profile['iccid'] + " / Status: " + profile[
                        'profileStatus'] + " / Last Modified: " + str(profile['lastModified']))
                test.log.com("*\t\tDevice Owner:" + test.get_device_label(test, eid_dict[key]))

    def read_status_from_file(self, test, file_name, operator):
        iccid_list = test.get_iccids_from_file(test, file_name)
        test.log.com(' ')
        test.log.com(
            '*************************************************************************************************************************')
        test.log.com('* ' + operator + ' (' + str(
            len(iccid_list)) + ' subscriptions)\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t*')
        test.log.com(
            '*************************************************************************************************************************')
        test.log.com(
            '* ICCID:                Status SM-DP+:\tprofileOwner/EID SM-DP+:\t\t\tCinterion IoT Suite (' + test.iot_suite_organization + ')\t*')
        test.log.com(
            '*************************************************************************************************************************')

        sub_stat_available = sub_stat_downloaded = sub_stat_installed = sub_stat_released = sub_stat_error = 0
        mods_stat_available = mods_stat_enabled = mods_stat_disabled = mods_stat_not_found = 0
        sub_stat = ""
        mods_stat = ""

        for i in range(len(iccid_list)):
            sub_stat, mods_stat = test.read_status_by_iccid(test, str(iccid_list[i]))
            if (sub_stat == 'Available'):
                sub_stat_available += 1
            elif (sub_stat == 'Installed'):
                sub_stat_installed += 1
            elif (sub_stat == 'Released'):
                sub_stat_released += 1
            elif (sub_stat == 'Downloaded'):
                sub_stat_downloaded += 1
            else:
                sub_stat_error += 1

            if (mods_stat == 'available'):
                mods_stat_available += 1
            elif (mods_stat == 'enabled'):
                mods_stat_enabled += 1
            elif (mods_stat == 'disabled'):
                mods_stat_disabled += 1
            else:
                mods_stat_not_found += 1

        test.log.com(
            '*************************************************************************************************************************')
        test.log.com('* SM-DP+:    Available ' + str(sub_stat_available) + ' / Downloaded ' + str(
            sub_stat_downloaded) + ' / Installed ' + str(sub_stat_installed) + ' / Released ' + str(
            sub_stat_released) + ' / Error ' + str(sub_stat_error))
        test.log.com('* IoT Suite: Available ' + str(mods_stat_available) + ' / Enabled ' + str(
            mods_stat_enabled) + ' / Disabled ' + str(mods_stat_disabled) + ' / Not found ' + str(
            mods_stat_enabled))
        test.log.com(
            '*************************************************************************************************************************')

    def read_status_by_iccid(self, test, iccid):
        mods_stat = ""
        sub_stat = ""

        # execute the command
        result = test.src.get_profile_info(iccid, log_status=False)

        # convert to JSON object
        out_json = result.json()
        status = out_json['header']['functionExecutionStatus']['status']

        if (status == "Executed-Success"):
            # test.log.info(">>> matchingId: " + out_json['matchingId'])

            # lookup subscription state on Cinterion IoT Suite, read device label if possible
            mods_status = ""
            sub_stat = out_json['profileStatus']

            for i in range(len(mods_subs)):
                sub = mods_subs[i]

                if sub['iccid'] == iccid:
                    mods_status += sub['status']
                    mods_stat = sub['status']

                    if (sub['status'] != "available"):
                        mods_status += ", IMEI: " + sub['imei'] + test.get_device_label(test,
                                                                                        sub['imei'])

                        mods_status += ", bookedSince: " + sub['bookedSince']
                        mods_status += ", enabledSince: " + sub['enabledSince']
                        if ('eid' in sub):
                            mods_status += ", EID: " + sub['eid']

            if (mods_status == ""):
                mods_status = "*** SUBSCRIPTION NOT FOUND! ***"
                mods_stat = mods_status

                # try to find the device with the EID if possible
                if (len(out_json['profileOwner']) == 32):
                    mods_status += " (lookup by EID: " + test.find_device_by_eid(test, out_json[
                        'profileOwner']) + ")"

            if (out_json['profileStatus'] == 'Available') or (
                    out_json['profileStatus'] == 'Released'):
                mods_status = "\t\t\t\t\t\t\t\t" + mods_status

            test.log.com(str(iccid) + "    " + out_json['profileStatus'] + "\t\t" + out_json[
                'profileOwner'] + "\t" + mods_status)
        else:
            test.log.com(str(iccid) + " Error: " +
                         out_json['header']['functionExecutionStatus']['statusCodeData']['message'])
            sub_stat = "Error"

        return sub_stat, mods_stat

    def find_device_by_eid(self, test, eid):
        dev = ""
        if eid in eid_dict:
            dev = "found IMEI " + eid_dict[eid] + test.get_device_label(test, eid_dict[eid])
        else:
            dev = "no IMEI found for EID"

        return dev

    def get_device_label(self, test, imei):
        label = ""
        for i in range(len(mods_devices)):
            dev = mods_devices[i]

            if dev['imei'] == imei:
                if ('label' in dev):
                    label = " (" + str(dev['label']) + ")"
                else:
                    label = " (no label)"

        if (label == ""):
            label = " (device not labeled)"

        return label

    def get_iccids_from_file(self, test, file_name):
        iccid_list = []
        test.log.info("Input file: " + str(file_name))

        base_path, _ = os.path.split(test.test_file)
        file_path = os.path.join(base_path, f'{file_name}')

        result, iccid_list = test.dut.dstl_get_all_iccids_from_file(file_path)

        if result is False:
            dstl.log.error("ICCID file: " + file_name + " could not be found - test abort")

        test.expect(result, critical=True)
        return iccid_list

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
