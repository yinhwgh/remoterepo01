#responsible: thomas.hinze@thalesgroup.com
#location: Berlin

from datetime import datetime

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.devboard import devboard

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart

#from dstl.internet_service.leshan_rest_client import LeshanRESTClient
from tests.device_management.lwm2m_client.lwm2m_dstl_bringup_helper import *

from dstl.security.lock_unlock_sim import dstl_unlock_sim
from dstl.network_service.register_to_network import *
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_defined_identification import dstl_defined_manufacturer
from dstl.identification.get_identification import dstl_collect_ati_information_from_other_commands

class Lwm2mBasicDeviceObjectTest(BaseTest):
    def setup(test):
        # get values for the device to be compared with values queried in the test via LWM2M to compare them
        # depending on the value, it is either a defined value for a product or queried by some method other
        # than LWM2M, e.g. AT cmd or Android API
        test.expected_manufacturer = test.dut.dstl_defined_manufacturer()
        test.expected_model = test_dut_dstl_get_model(test.dut)
        test.expected_imei = test.dut.dstl_get_imei()
        test.expected_fw_version = test_dut_dstl_get_fw_revision(test.dut)
        test.expected_sw_version = test_dut_dstl_get_sw_revision(test.dut)
        test.expected_svn = test_dut_dstl_get_sw_version_number(test.dut)
        test.expected_bindings = test_dut_ep1_dstl_get_defined_lwm2m_binding_modes(test.dut)

        test.dut.dstl_detect()
        #test.dut.dstl_register_to_network()

        # TODO: modify some settings, e.g. LWM2M server to be used, to allow proper testing
        #test_dut_ep1_set_test_env(test.dut)
        test_dut_ep1_dstl_start_client(test.dut)
        test_dut_ep1_dstl_wait_for_registration(test.dut, timeout=5, critical=True)

    def run(test):
        #test.read_device_object()
        test.device_constants()

        test.time_get_lwm2m_compare_with_dut()
        test.time_set_lwm2m_compare_dut_and_lwm2m()

        # TODO: test timezone and UTC
        test.log.warning("TODO: test time zone")
        test.log.warning("TODO: test utc offset")

        # TODO: test observe time - expect: 1 update each second
        test.log.warning("TODO: observe time")

        test.memory_info()
        test.power_source()

        test.error_codes()

        # factory reset will be tested in a separated TC since there is a bootstrap involved

        #test.reboot()

    def read_device_object(test):
        res = test_dut_ep1_dstl_read_object(test.dut, obj_id=lwm2m.OBJ_DEVICE)

        test.expect(res is not False)

        test.log.info(res)

        # single instance object
        test.expect(len(res) == 1)

        val = res[0]
        test.expect(val[lwm2m.RES_DEVICE_MANUFACTURER] == expected.manufacturer)
        test.expect(val[lwm2m.RES_DEVICE_MODEL] == expected.model)
        test.expect(val[lwm2m.RES_DEVICE_SERIAL_NO] == expected.imei)
        test.expect(val[lwm2m.RES_DEVICE_FW_VERSION] == expected.fw_version)
        test.expect(val[lwm2m.RES_DEVICE_SW_REVISION] == expected.sw_version)
        test.expect(val[lwm2m.RES_DEVICE_BINDING_MODES] == expected.bindings)

    def device_constants(test):
        # manufacturer
        val = test_dut_ep1_dstl_get_manufacturer(test.dut)
        test.log.info(f'manufacturer: {val}')
        test.log.info(f'expected: {test.expected_manufacturer}')
        test.expect(val == test.expected_manufacturer)

        # model
        val = test_dut_ep1_dstl_get_model(test.dut)
        test.log.info(f'model: {val}')
        test.log.info(f'expected: {test.expected_model}')
        test.expect(val == test.expected_model)

        # IMEI / serial number
        val = test_dut_ep1_dstl_get_imei(test.dut)
        test.log.info(f'serial/imei: {val}')
        test.log.info(f'expected: {test.expected_imei}')
        test.expect(val == test.expected_imei)

        # FW revision
        val = test_dut_ep1_dstl_get_fw_revision(test.dut)
        test.log.info(f'fw_revision: {val}')
        test.log.info(f'expected: {test.expected_fw_version}')
        test.expect(val == test.expected_fw_version)

        # SW revision
        val = test_dut_ep1_dstl_get_sw_revision(test.dut)
        test.log.info(f'sw_revision: {val}')

        lwm2m_client = test_dut_ep1_dstl_get_endpoint_type(test.dut)
        if lwm2m_client is lwm2m.ENDPOINT_ATT:
            # AT&T expects SVN
            test.log.info(f'expected: {test.expected_svn} (SVN, ATT specific)')
            test.expect(val == test.expected_svn)
        else:
            test.log.info(f'expected: {test.expected_sw_version}')
            test.expect(val == test.expected_sw_version)

        # Binding modes
        val = test_dut_ep1_dstl_get_binding_modes(test.dut)
        test.log.info(f'bindings: {val}')
        test.log.info(f'expected: {test.expected_bindings}')
        test.expect(val == test.expected_bindings)

    def time_get_lwm2m_compare_with_dut(test):
        # get time via LWM2M
        datetime_ep1 = test_dut_ep1_dstl_get_time(test.dut)

        if not datetime_ep1:
            test.log.error(f'datetime_ep1: {datetime_ep1}')
            return False

        test.log.info(f'datetime_ep1: {datetime_ep1}')

        # get time on DUT using some local, non-lwm2m interface, e.g. AT commands
        # TODO: how to get TZ for time on DUT
        # time reported by LWM2M has timezone included, but time on dut not necessarly ...
        # ??? assume same timzone ???
        datetime_dut = test_dut_get_time(test.dut)
        test.log.info(f'datetime_dut: {datetime_dut}')

        if datetime_dut.tzinfo is None:
            test.log.info(f'Use TZ info from LWM2M for time on DUT: {datetime_ep1.tzinfo}')
            datetime_dut = datetime_dut.astimezone(datetime_ep1.tzinfo)

        # delta between DUT time and LWM2M time should not be larger than some seconds
        delta = datetime_ep1 - datetime_dut
        seconds = delta.total_seconds()
        test.log.info(f'delta dut vs lwm2m: {seconds} s')
        test.expect(abs(seconds) < 3)

    def time_set_lwm2m_compare_dut_and_lwm2m(test):
        test_timestamp = "1999-12-27T10:26:56+0100"

        datetime_test = datetime.strptime(test_timestamp, "%Y-%m-%dT%H:%M:%S%z")
        test.log.info(f'datetime_test: {datetime_test}')

        # set time via LWM2M
        test_dut_ep1_dstl_set_time(test.dut, datetime_test)

        # get time via LWM2M
        datetime_ep1 = test_dut_ep1_dstl_get_time(test.dut)
        test.log.info(f'datetime_ep1: {datetime_ep1}')

        delta = datetime_ep1 - datetime_test
        seconds = delta.total_seconds()
        test.log.info(f'delta-ep1: {seconds} s')
        test.expect(abs(seconds) < 3)

        # get time on DUT using some local, non-lwm2m interface, e.g. AT commands
        # TODO: how to get TZ for time on DUT
        # time reported by LWM2M has timezone included, but time on dut not necessarly ...
        # ??? assume same timzone ???
        datetime_dut = test_dut_get_time(test.dut)
        test.log.info(f'datetime_dut: {datetime_dut}')

        if datetime_dut.tzinfo is None:
            test.log.info(f'Use TZ info from LWM2M for time on DUT: {datetime_ep1.tzinfo}')
            datetime_dut = datetime_dut.astimezone(datetime_ep1.tzinfo)

        delta = datetime_dut - datetime_test
        seconds = delta.total_seconds()
        test.log.info(f'delta-dut: {seconds} s')
        test.expect(abs(seconds) < 3)

    def factory_reset(test):
        test.log.info("TODO: test factory reset")
        # TODO implement test case
        # TODO: how to check all default values ???
        #       test.dut.ep1.get_defined_lwm2m_default_values()
        # Note:
        #   might need to restore test settings if not testing in proper MNO
        #   network, e.g. testing ATT in european, asian or test networks
        # test.lwm2m_ep1_test_server
        # TODO: test.dut.ep1.get_client_state() == BOOTSTRAPPING

    def reboot(test):
        test_dut_ep1_reset(test)

        # TODO: expect shutdown urc
        test.dut.at1.close()
        test.sleep(1)

        time_start = datetime.now()
        while True:
            try:
                test.dut.at1.open()
                break

            except ...:
                delta = datetime.now() - time_start
                if delta.total_seconds() > test.max_reopening_time:
                    test.fail('re-opening of AT ports failed')

                test.sleep(1)

        # TODO: expect sys-start urc
        # TODO: if no LWM2M autostart then start client

    def error_codes(test):
        test.log.warning("TODO: test error codes")
        # TODO implement test case

    def memory_info(test):
        test.log.info("test memory info")
        mem_free = test_dut_ep1_dstl_get_free_memory(test.dut)
        mem_total = test_dut_ep1_dstl_get_total_memory(test.dut)
        test.log.info(f"lwm2m free mem: {mem_free}")
        test.log.info(f"lwm2m total mem: {mem_total}")

        # total memory shall be as defined
        exp_total = test_dut_ep1_dstl_get_defined_lwm2m_memory_total_kB(test.dut)
        test.log.info(f"expected total mem: {exp_total}")
        test.expect(mem_total == exp_total)

        # mem free shall not exceed mem total
        test.expect(mem_free <= mem_total)

    def power_source(test):
        test.log.warning("TODO: test power source")
        # TODO implement test case
        
    def cleanup(test):
        pass
