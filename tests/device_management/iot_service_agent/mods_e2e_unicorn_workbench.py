# responsible: karsten.labuske@thalesgroup.com
# location: Berlin
# test case: UNISIM01-376

import unicorn
from core.basetest import BaseTest
from core import interface_serial
import csv
import platform
import subprocess
from datetime import datetime
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient, LogLevel
from dstl.auxiliary.write_json_result_file import *
from dstl.miscellaneous.mods_e2e_unicorn_support import *
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
from dstl.miscellaneous.mods_e2e_unicorn_support import *
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
from dstl.auxiliary import init
from dstl.identification import get_imei
from dstl.usim import get_imsi
from dstl.auxiliary import restart_module
from dstl.hardware import set_real_time_clock
from dstl.auxiliary import check_urc
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result

testkey = "UNISIM01-376"


class Workbench(BaseTest):
    """
    Class to call workbench, do over-the-wire provisioning and evaluate results
    """

    def setup(test):
        global env
        global iccid_dict
        global mods_subs
        global ac_file
        global lpa_debug_file
        global result_file
        global start_time

        iccid_dict = {}
        start_time = datetime.datetime.now()

        test.log.com('***** Testcase: ' + test.test_file + ' (UNISIM01-???) - Start *****')

        test.require_parameter('es9_url', default='thales3-livelab.prod.ondemandconnectivity.com')
        test.require_parameter('iccid_file', default='iccids_3gpp_rohde_schwarz_gcp.txt')
        test.require_parameter('no_of_profiles', default=1)
        test.require_parameter('lpa_debug_info', default=True)

        test.rest_client = IotSuiteRESTClient()
        test.src = SmdpRESTClient()

        # read all subscriptions from MODS
        test.log.step("Step 0: reading all subscriptions from Cinterion IoT Suite")
        r = get_subscriptions()
        test.expect(r, critical=True)
        mods_subs = r.json()
        test.expect(mods_subs, critical=True)
        test.log.info("Subscriptions Cinterion IoT Suite:\n " + json.dumps(mods_subs, indent=4, sort_keys=True))

        env = platform.system()
        ac_file = "actioncode.txt"
        lpa_debug_file = "lpa.log"
        result_file = "result.csv"

    def create_actioncode_file(self, test):
        iccid_file = test.get('iccid_file')
        apn = test.get('apn')
        pdn = test.get('pdn')
        no_of_profiles = test.get('no_of_profiles')
        no_of_profiles_added = 0

        result = False

        base_path, _ = os.path.split(test.test_file)
        file_path = os.path.join(base_path, f'{iccid_file}')

        # assemble platform specific path to actioncode.txt
        ac = base_path + "/workbench/" + str(env) + "/" + ac_file

        # read iccid file
        test.log.info(">>> actioncode.txt: " + ac)

        # open actioncode.txt for writing
        ac_fd = open(ac, "w")

        # read all iccid's from file
        result, iccid_list = test.dut.dstl_get_all_iccids_from_file(file_path)
        if result is False:
            dstl.log.error("ICCID file: " + iccid_file + " could not be found - test abort")

        test.expect(result, critical=True)
        for iccid in iccid_list:
            if no_of_profiles_added < no_of_profiles:
                # check subscription status from server
                for sub in mods_subs:
                    if sub["iccid"] == iccid:
                        # test.log.info("Found icc_id: " + sub["iccid"])
                        break

                test.expect(sub, critical=True)

                # if available and not connected to any job: add it to file and delete it from server (remember iccid and pool in global structure)
                job_present = "jobId" in sub

                if sub["status"] == "available" and not job_present and no_of_profiles_added < no_of_profiles:

                    # - read matchingID from SM-DP+ server
                    profile_info = test.dut.dstl_get_profile_info_from_smdp(iccid)
                    if 'matchingId' in str(profile_info):
                        matching_id = profile_info['matchingId']
                    test.expect(matching_id)
                    if not matching_id:
                        break

                    test.log.info("matchingId: " + matching_id + " for iccid: " + iccid)

                    # read pool to get apnName and pdnType
                    pool = test.rest_client.get_pool(sub['poolId'], to_json=True, log_level=LogLevel.QUIET)
                    test.expect(pool)
                    # test.log.info("PoolID: " + str(sub['poolId']))
                    # test.log.info("Subscription:\n " + json.dumps(sub, indent=4, sort_keys=True))
                    # test.log.info("Pool:\n " + json.dumps(pool, indent=4, sort_keys=True))

                    apn = pool['apnName']
                    pdn = pool['pdnType']
                    test.log.info('adding to ' + ac_file + ': "' + str(matching_id) + ", " + apn + ", " + pdn + '" for ICCID ' + iccid)
                    ac_fd.write(str(matching_id) + ", " + apn + ", " + pdn + "\n")
                    no_of_profiles_added += 1

                    # delete subscription from MODS as long as there's no 'workbench reservation' state
                    test.log.info("###########################################################################################")
                    test.log.info("# DELETING subscription - later on there will be a new IoT Suite reserved state to be set #")
                    test.log.info("###########################################################################################")
                    r = delete_subscription(sub['id'])
                    test.expect(r, critical=False)

                    # remember iccid and poolId
                    iccid_dict[iccid] = sub["poolId"]

        ac_fd.close()
        test.expect(no_of_profiles_added > 0, critical=True)
        test.log.info("Added subscriptions" + str(iccid_dict))
        result = True

        return result

    def create_wb_parameter_list(self, test):
        # assemble platform specific path to workbench executable
        base_path, _ = os.path.split(test.test_file)
        wb_base_path = base_path + "/workbench/" + str(env)
        wb_executable = wb_base_path + "/workbench"
        test.log.info(">>> workbench path: " + wb_base_path)
        test.log.info(">>> workbench executable: " + wb_executable)

        result = False

        # - assemble parameters for workbench call: -p /dev/ttySx -b <speed>
        serial_port = interface_serial.SerialInterface
        if not isinstance(serial_port, interface_serial.SerialInterface):
            serial_port = test.dut.at1
        port_name = str(serial_port.port)
        port_speed = str(serial_port.settings['baudrate'])

        if env == "Windows":
            port_no_start = port_name.find("COM") + 3
            test.expect(port_no_start > 2, critical=True)
            test.log.info(">>> serial port Windows: " + port_name)
            test.log.info(">>> serial port #" + port_name[port_no_start:])
            port_no = int(port_name[port_no_start:])
            port_name = "/dev/ttyS" + str(port_no - 1)

        test.log.info(">>> serial port: " + port_name + ", " + port_speed)

        args = [wb_executable, '-p', port_name, '-b', port_speed]
        # args = [wb_executable, '-h']
        result = True

        return result, args, wb_base_path

    def read_wb_result_file(self, test):
        #   format:
        #       BEGIN, END, STATUS, HW-ID, HW-REV, IMEI, EID, ICCID, PROFILE NAME, APN, PDN, SW VER
        #       Fri Nov 19 15:55:47 2021 , Fri Nov 19 15:55:52 2021 , FAIL 4: no actioncode file available, EXS62-W, REVISION 01.200, "004401083488383", "89033023424320000000006585856733", "", "",, , SERVAL_300_048F RELEASE. Thu 04.11.2021. 15:41. "jenkins"
        #       Fri Nov 19 15:57:34 2021 , Fri Nov 19 15:57:40 2021 , FAIL 3: actioncode file is empty, EXS62-W, REVISION 01.200, "+CEREG: 2", "89033023424320000000006585856733", "", "",, , SERVAL_300_048F RELEASE. Thu 04.11.2021. 15:41. "jenkins"
        base_path, _ = os.path.split(test.test_file)

        result = False

        # assemble platform specific path to result.csv
        res = base_path + "/workbench/" + str(env) + "/" + result_file

        # read result file
        test.log.info(">>> result.csv: " + res)
        with open(res, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)

            # empty list
            res_csv = []

            for row in reader:
                # create list
                one_entry = []
                for entry in row:
                    one_entry.append(str(entry).strip())

                # add list to list
                res_csv.append(one_entry)

        result = True

        return result, res_csv

    def read_lpa_debug_file(self, test):

        base_path, _ = os.path.split(test.test_file)
        result = False

        # assemble platform specific path to result.csv
        res = base_path + "/workbench/" + str(env) + "/Logs/" + lpa_debug_file

        # read result file
        test.log.info(">>> LPA debug file: " + res)
        with open(res) as f:
            lines = f.readlines()
        test.expect(lines)

        # find first entry with matching date/time and print out the rest of the file
        output = False
        for l in lines:
            if output:
                test.log.info(">>> LPA debug file: " + l)
            else:
                check = l[0:18]
                if check and len(check) > 17:
                    # Format: "19/11/2021 15:55:49 |  | DEB | _atCommandResponseToApdu(): Extracted APDU response: 019000"
                    try:
                        datetime_object = datetime.datetime.strptime(check, '%d/%m/%Y %H:%M:%S')
                        if datetime_object >= start_time:
                            output = True
                    except ValueError as v:
                        if output:
                            test.log.info(">>> LPA debug file: " + str(l))
                        # 2021-12-02 07:58:29,715 INFO: >>> LPA debug file: date/time: time data '+CSIM: 6,"019000"\n' does not match format '%d/%m/%Y %H:%M:%S'
                        # if len(v.args) > 0 and v.args[0].startswith('unconverted data remains: '):

        # test.log.info(">>> LPA debug file: " + str(len(lines)) + " lines")

        result = True

        return result

    def validate_data(self, test, profile_list, ctx_settings, cm_settings, csv_data, imei):
        result = False
        test.log.info("TC start time: " + str(start_time))
        test.log.info("Profile list: " + str(profile_list))
        test.log.info("CM settings: " + str(cm_settings))
        test.log.info("PDP context settings: " + str(ctx_settings))

        # ['BEGIN', 'END', 'STATUS', 'HW-ID', 'HW-REV', 'IMEI', 'EID', 'ICCID', 'PROFILE NAME', 'APN', 'PDN', 'SW VER']
        #     0       1        2        3         4        5      6       7         8             9     10       11
        # ['Fri Nov 26 15:57:34 2021', 'Fri Nov 26 15:57:40 2021', 'FAIL 3: actioncode file is empty', 'EXS62-W', 'REVISION 01.200', '"351562110230990"', '"89033023424320000000006585856733"', '""', '""', '', '', 'SERVAL_300_048F RELEASE. Thu 04.11.2021. 15:41. "jenkins"']
        device_csv_data = []
        for csv_entry in csv_data:
            # test.log.info("Workbench csv data: " + str(csv_entry))
            if csv_entry[0] != "BEGIN":
                # Fri Nov 19 15:55:47 2021
                datetime_object = datetime.datetime.strptime(csv_entry[0], '%a %b %d %H:%M:%S %Y')

                # filter out entries which are in the past or have different IMEI
                if datetime_object < start_time:
                    test.log.info("Filtered out entry due to time: " + str(csv_entry))
                elif csv_entry[5] != '"' + imei + '"':
                    test.log.info("Filtered out entry due to different IMEI: " + str(csv_entry))
                else:
                    device_csv_data.append(csv_entry)

        # checks
        # - active profile != provisioning profile
        # - active profile in profile list
        # - active profile in cm_settings
        # - APN and PDN from CSV set in ctx_settings
        # - APN and PDN from CSV set in cm_settings
        # - active ICCID in profile_list, ctx_settings, cm_settings
        test.log.step("Step 5.2.1: valid CSV entries available (start time, IMEI matching)")
        test.expect(device_csv_data)
        test.expect(len(device_csv_data) > 0)
        for csv_entry in device_csv_data:
            start = datetime.datetime.strptime(csv_entry[0], '%a %b %d %H:%M:%S %Y')
            end = datetime.datetime.strptime(csv_entry[1], '%a %b %d %H:%M:%S %Y')
            duration = end - start
            status = csv_entry[2]
            eid = csv_entry[6]
            iccid = csv_entry[7]
            apn = csv_entry[9]
            pdn = csv_entry[10]
            test.log.info("workbench result: start " + str(start) + ", end: " + str(end) + ", status: " + str(
                status) + ", eid: " + str(eid) + ", iccid: " + str(iccid) + ", apn: " + str(apn) + ", pdn: " + str(pdn))
            test.log.info("    calculated duration (*OPEN* --- add as KPI?!): " + str(duration))

        test.log.step("Step 5.2.2: active profile and active profile != provisioning profile")
        test.log.info("Not yet implemented")

        test.log.step("Step 5.2.3: active profile in profile list")
        test.log.info("Not yet implemented")

        test.log.step("Step 5.2.4: active profile in cm_settings")
        test.log.info("Not yet implemented")

        test.log.step("Step 5.2.5: APN and PDN from CSV set in ctx_settings")
        test.log.info("Not yet implemented")

        test.log.step("Step 5.2.6: APN and PDN from CSV set in cn_settings")
        test.log.info("Not yet implemented")

        test.log.step("Step 5.2.7: active ICCID in profile_list, ctx_settings, cm_settings")
        test.log.info("Not yet implemented")

        test.log.step("Step 5.2.8: check PRID on device side")
        test.log.info("Not yet implemented")

        result = True

        return result

    def run(test):
        # TODO
        # adapt Config/lpa_config.ini ?????????????
        #   deviceDefaultSMDPAddress=thales3-livelab.prod.ondemandconnectivity.com
        es9_url = test.get('es9_url')
        lpa_debug = test.get('lpa_debug_info')

        test.log.info(">>> Platform (Windows/Linux): " + env)

        #
        # generate actioncode.txt
        #
        test.log.step("Step 1: generate actioncode.txt")
        result = test.create_actioncode_file(test)
        test.expect(result)

        #
        # - call workbench with parameters
        #
        test.log.step("Step 2: generate workbench parameters")
        result, args, cwd = test.create_wb_parameter_list(test)
        test.expect(result)
        test.expect(args)

        # disconnect from VPN as long as ES9+ URL is not whitelisted (Ticket #S211203_000378)
        test.log.step("Step 3: call workbench")
        test.log.step("*** IF RUNNING WITH VPN IT'S TIME TO DISCONNECT (WAITING 1 minute)")
        test.sleep(60)

        test.log.info(">>> calling workbench " + str(args) + " in cwd " + cwd)
        rc = subprocess.call(args, cwd=str(cwd))
        test.log.info(">>> workbench return code " + str(rc))

        # Connect to VPN again
        test.log.step("*** IF RUNNING WITH VPN IT'S TIME TO CONNECT AGAIN (WAITING 1 minute)")
        test.sleep(60)

        if lpa_debug:
            result = test.read_lpa_debug_file(test)
            test.expect(result)

        #
        # read device state
        #
        # first start the module as the workbench switches off device after processing
        test.log.step("Step 4: read device state after workbench processing")
        serial_port = interface_serial.SerialInterface
        if not isinstance(serial_port, interface_serial.SerialInterface):
            serial_port = test.dut.at1

        test.log.info(">>> trying to open Port: " + str(serial_port.port) + " / " + str(serial_port.settings))
        serial_port.open()
        test.sleep(10)
        test.log.info(">>> Port settings: " + str(serial_port.settings))
        test.log.info(">>> Port connection: " + str(serial_port.connection))
        test.expect("open=True" in str(serial_port.connection))

        test.dut.dstl_detect()
        test.dut.dstl_set_radio_band_settings()
        test.dut.dstl_restart()
        test.dut.dstl_set_real_time_clock()
        imei = test.dut.dstl_get_imei()

        test.log.step("Step 4.1: get LPA profile list")
        result, profile_list = test.dut.dstl_get_profile_info()
        test.expect(result)
        test.expect(profile_list)
        test.expect(len(profile_list) > 0)

        test.log.step("Step 4.2: list PDP context configuration")
        result = test.dut.at1.send_and_verify('at+cgdcont?;+cgact?;+cgpaddr', ".*OK.*")
        test.expect(result)
        ctx_config = test.dut.at1.last_response
        test.expect(ctx_config)

        test.log.step("Step 4.3: list connection manager status")
        test.dut.dstl_show_cm_table()
        cm_config = test.dut.at1.last_response
        test.expect(cm_config)

        # - evaluate results from result.csv
        test.log.step("Step 5: evaluate data")
        test.log.step("Step 5.1: read result.csv")
        result, res_csv = test.read_wb_result_file(test)
        test.expect(result)
        test.expect(res_csv, critical=True)
        test.expect(len(res_csv) > 0, critical=True)

        #
        # match result.csv contents against device data (profile_list, cm_config, ctx_config)
        #
        test.log.step("Step 5.2: validate data")
        result = test.validate_data(test, profile_list, ctx_config, cm_config, res_csv, imei)
        test.expect(result)

        #
        # TODO
        # new KPI's provisioning over-the-wire?
        #

        test.log.step("Step 6: cleanup device")
        # delete subscriptions from device
        # - enable bootstrap
        # - delete operational profiles
        # - send notifications
        # - bring back device in factory default configuration

        test.log.step("Step 6.1: enable bootstrap and get connectivity")
        result = test.dut.dstl_init_all_mods_settings()
        test.expect(result)

        result = test.dut.dstl_activate_bootstrap_and_apns()
        test.expect(result)

        result = test.dut.dstl_check_network_registration()
        test.expect(result)

        test.log.step("Step 6.2: delete operational profiles")
        result = test.dut.dstl_delete_all_subscriptions_on_module(profile_list)
        test.expect(result)

        test.log.step("Step 6.3: send notifications")
        result = test.dut.dstl_send_pending_notifications()
        test.expect(result)

        test.log.step("Step 6.4: set initial module configuration again")
        test.dut.dstl_stop_mods_agent()
        test.dut.dstl_set_prid_wo_agent(prid_name='""')
        test.dut.dstl_set_download_mode_wo_agent(download_mode=0)
        test.dut.dstl_activate_lpa_engine()
        test.dut.dstl_deactivate_bootstrap()
        test.dut.dstl_set_apns()
        test.dut.dstl_delete_cm_table()

    def cleanup(test):
        # re-create used subscriptions on MODS
        test.log.step("Step 7: re-create subscriptions on Cinterion IoT Suite")
        for sub in iccid_dict:
            result, status = test.dut.dstl_create_single_subscription(test.rest_client, sub, iccid_dict[sub])
            test.log.info(">>> creating sub on MODS: " + str(result) + ", status " + str(status))

        # test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
        #                                testkey, str(test.test_result), test.campaign_file,
        #                                test.timer_start, test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')
        pass


if "__main__" == __name__:
    unicorn.main()
