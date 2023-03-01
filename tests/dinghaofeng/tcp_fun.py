# responsible hongwei.yin@thalesgroup.com
# location Dalian

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.generate_data import dstl_generate_data

address_0 = 'socktcp://114.55.6.216:50000'
data_500 = dstl_generate_data(500)
times = 2


class Test(BaseTest):
    """
     test cases describe
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()

    def run(test):
        test.log.step("connect tcp server.")
        set_apn(test)
        config_service_0_type_tcp(test)
        config_service_0_conid(test)
        config_service_0_address(test)
        active_sica(test)
        open_service_0(test)
        test.expect(check_sisw_urc(test), msg='check_sisw_urc')
        test.expect(send_data(test, times), msg='send datas')
        check_sisi_0(test, times)
        close_service_0(test)
        test.log.step("deregister and register network.")
        deregister_network(test)
        register_to_network(test)
        check_if_registered(test)

    def cleanup(test):
        pass


def set_apn(test):
    if test.dut.sim.apn_v4 == 'None':
        apn = 'airtelgprs.com'
    else:
        apn = test.dut.sim.apn_v4
    return test.expect(test.dut.at1.send_and_verify(f'AT+CGDCONT=1,IPV4V6,{apn}', 'OK',
                                                    timeout=20, handle_errors=True))


def config_service_0_type_tcp(test):
    return test.expect(test.dut.at1.send_and_verify('AT^SISS=0,"srvType","socket"', 'OK', timeout=20,
                                                    handle_errors=True))


def config_service_0_conid(test):
    return test.expect(test.dut.at1.send_and_verify('AT^SISS=0,"conid","1"', 'OK', timeout=20,
                                                    handle_errors=True))


def config_service_0_address(test):
    return test.expect(test.dut.at1.send_and_verify(f'AT^SISS=0,"address","{address_0}"', 'OK', timeout=20,
                                                    handle_errors=True))


def active_sica(test):
    return test.expect(test.dut.at1.send_and_verify('AT^SICA=1,1', 'OK', timeout=20, handle_errors=True))


def open_service_0(test, force_abnormal_flow=False):
    test.dut.at1.send_and_verify('AT^SISC=0', 'OK', timeout=20, handle_errors=True)
    return test.expect(test.dut.at1.send_and_verify('AT^SISO=0', 'OK', timeout=20, handle_errors=True))


def check_sisw_urc(test):
    result = test.dut.dstl_check_urc('SISW: 0,1', timeout=20)
    if result:
        return True
    else:
        max_retry = 10
        i = 0
        while i < max_retry:
            test.log.info(f'Start reopen socket the {i + 1}th time')
            test.dut.at1.send_and_verify('AT^SISC=0')
            test.sleep(1)
            test.dut.at1.send_and_verify('AT^SISO=0')
            result = test.dut.dstl_check_urc('SISW: 0,1')
            if result:
                return True
            else:
                i = i + 1
        return False


def send_data(test, times):
    result = True
    for i in range(times):
        r1 = test.expect(test.dut.at1.send_and_verify('AT^SISW=0,500', 'SISW:', wait_for='SISW:', timeout=20,
                                                      handle_errors=True))
        r2 = test.expect(test.dut.at1.send_and_verify(data_500, 'OK', wait_for='SISW:', timeout=20,
                                                      handle_errors=True))
        result = result & r1 & r2
        test.sleep(3)
    return result


def check_sisi_0(test, times):
    data_length = 500 * times
    return test.expect(
        test.dut.at1.send_and_verify_retry('AT^SISI=0', f'SISI: 0,4,0,{data_length}', retry=2, timeout=5, sleep=3,
                                           handle_errors=True))


def close_service_0(test):
    return test.expect(test.dut.at1.send_and_verify('AT^SISC=0', 'OK', timeout=20, handle_errors=True))


def deregister_network(test):
    return test.expect(test.dut.at1.send_and_verify('AT+COPS=2', 'OK', timeout=20, handle_errors=True))


def register_to_network(test):
    return test.expect(test.dut.at1.send_and_verify('AT+COPS=0', 'OK', timeout=20, handle_errors=True))


def check_if_registered(test):
    return test.expect(test.dut.at1.send_and_verify_retry('AT+CREG?', 'CREG: \d,1', retry=2,
                                                          wait_after_send=5, handle_errors=True))


if __name__ == "__main__":
    unicorn.main()
