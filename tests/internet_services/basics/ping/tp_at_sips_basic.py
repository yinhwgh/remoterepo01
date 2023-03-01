#responsible marek.kocela@globallogic.com
#Wroclaw
#TC TC0088277.002
import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """Short description:
       Check basic functionality of AT^SIPS.

       Detailed description:
       1. Use AT^SIPS=? to get all supported parameters.
       2. Create Internet socket service profile with those parameters
            -service type (srvType)
            -connection id (conId)
            -alphabet (if supported)
            -address
            -TCP max retransmission (tcpMR)
            -TCP max retransmission (tcpMR)
       3. Save Internet service profiles: AT^SIPS=all,save, then restart module.
       4. Check existence of Internet service profiles.
       5. Load Internet Internet service profiles AT^SIPS=all,load and check its existence.
       6. Delete Internet service profiles with: AT^SIPS=all,reset and check its existence.
       7. Restore saved data with: AT^SIPS=all,load and check its existence."""

    def setup(test):
        dstl_detect(test.dut)

    def run(test):
        test.log.info("Executing script for test case: TC0088277.002 - TpAtSipsBasic")

        test.log.step("1) Use AT^SIPS=? to get all supported parameters.")
        test.dut.at1.send_and_verify('at^sips=?', expect="OK", wait_for="OK", timeout=10)
        sips_split = test.dut.at1.last_response.split("^SIPS: ")
        test.expect(re.search('.*("service").*("all").*("reset").*("save").*("load").*(0-9).*', sips_split[1]))

        test.log.step("2) Create Internet socket service profile with those parameters\n"
            + "-service type (srvType)\n"
            + "-connection id (conId)\n"
            + "-alphabet (if supported)\n"
            + "-address\n"
            + "-TCP max retransmission (tcpMR)\n"
            + "-overall timeout (tcpOT)")

        test.tcp_socket = SocketProfile(test.dut, srv_profile_id=0, con_id=1, port=9999, protocol="tcp", alphabet=1,
                                        host="8.8.8.8", tcp_mr=10, tcp_ot=1000)
        test.tcp_socket.dstl_generate_address()
        test.expect(test.tcp_socket.dstl_get_service().dstl_load_profile())

        test.log.step("3) Save Internet service profiles: AT^SIPS=all,save, then restart module.")
        test.dut.at1.send_and_verify('at^sips="all","save"', expect="OK", wait_for="OK", timeout=10)
        dstl_restart(test.dut)

        test.log.step("4) Check existence of Internet service profiles.")
        test.dut.at1.send_and_verify('at^siss?', expect="OK", wait_for="OK", timeout=10)
        test.expect(re.search('.*0,"srvType","".*', test.dut.at1.last_response))

        test.log.step("5) Load Internet Internet service profiles AT^SIPS=all,load and check its existence.")
        test.dut.at1.send_and_verify('at^sips="all","load"', expect="OK", wait_for="OK", timeout=10)

        test.dut.at1.send_and_verify('at^siss?', expect="OK", wait_for="OK", timeout=10)
        siss_index_0_split = test.dut.at1.last_response.split("^SISS: 0,")
        test.expect(re.search('"srvType","Socket"', siss_index_0_split[1]))
        test.expect(re.search('"conId","1"', siss_index_0_split[2]))
        test.expect(re.search('"alphabet","1"', siss_index_0_split[3]))
        test.expect(re.search('"address","socktcp://8.8.8.8:9999"', siss_index_0_split[4]))
        test.expect(re.search('"tcpMR","10"', siss_index_0_split[5]))
        test.expect(re.search('"tcpOT","1000"', siss_index_0_split[6]))

        test.log.step("6) Delete Internet service profiles with: AT^SIPS=all,reset and check its existence.")
        test.dut.at1.send_and_verify('at^sips="all","reset"', expect="OK", wait_for="OK", timeout=10)
        test.dut.at1.send_and_verify('at^siss?', expect="OK", wait_for="OK", timeout=10)
        test.expect(re.search('.*0,"srvType","".*', test.dut.at1.last_response))

        test.log.step("7) Restore saved data with: AT^SIPS=all,load and check its existence.")
        test.dut.at1.send_and_verify('at^sips="all","load"', expect="OK", wait_for="OK", timeout=10)
        test.dut.at1.send_and_verify('at^siss?', expect="OK", wait_for="OK", timeout=10)
        siss_index_0_split = test.dut.at1.last_response.split("^SISS: 0,")
        test.expect(re.search('"srvType","Socket"', siss_index_0_split[1]))
        test.expect(re.search('"conId","1"', siss_index_0_split[2]))
        test.expect(re.search('"alphabet","1"', siss_index_0_split[3]))
        test.expect(re.search('"address","socktcp://8.8.8.8:9999"', siss_index_0_split[4]))
        test.expect(re.search('"tcpMR","10"', siss_index_0_split[5]))
        test.expect(re.search('"tcpOT","1000"', siss_index_0_split[6]))

    def cleanup(test):
        try:
            test.dut.at1.send_and_verify('at^sips="all","reset"', expect="OK", wait_for="OK", timeout=10)
            test.dut.at1.send_and_verify('at^sips="all","save"', expect="OK", wait_for="OK", timeout=10)
        except AttributeError:
            test.log.error("Object was not created.")

if "__main__" == __name__:
    unicorn.main()