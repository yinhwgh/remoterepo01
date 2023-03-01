#responsible: shuang.liang@thalesgroup.com
#location: Beijing
#TC0092084.001

import unicorn
from core.basetest import BaseTest
import re
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.network_service.register_to_network import dstl_register_to_network


class Test(BaseTest):

    """"
    Prove the correct implementation of the AT command +CGCMOD
    """

    def setup(test):
        test.dut.dstl_restart()
        test.dut.dstl_detect()

    def run(test):

        test.log.step("1. Register to the network")
        test.expect(dstl_register_to_network(test.dut))
        test.sleep(5)
        if (test.dut.product == 'cougar'):
            test.expect(test.dut.at1.send_and_verify("AT+CEREG?", r".*\+CEREG:.*[012],[15].*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CREG?", r".*\+CREG:.*[012],[15].*OK.*"))

        test.log.step("2. Check setting of CGCMOD.")
        test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=?', '.*\+CGCMOD:.*OK.*'))

        test.log.step("3. Define for each PDP context QOS settings.")
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=?", ".*OK.*"))
        max_pdp = int(re.search(r'(CGDCONT: \(\d-)(\d{1,2})', test.dut.at1.last_response).group(2))

        for cid in range(1, max_pdp + 1):
            test.log.info('Delete PDP contexts')
            test.expect(test.dut.at1.send_and_verify('AT+CGEQOS={}'.format(cid), '.*\+CGCQOS:.*OK.*'))

            test.log.info('Setting valid APN for next step')
            test.expect(test.dut.at1.send_and_verify('AT+CGDCONT={0},"IP","{1}"'
                                                     .format(cid, test.dut.sim.apn_v4), '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(
                'AT+CGEQOS=' + str(cid) + ',5,' + str(50 + cid) + ',' + str(50 + cid) + ',' + str(
                    100 + cid) + ',' + str(100 + cid)
                , '.*OK.*'))

        test.log.step("4. Check if context definitions and QOS parameter are set")
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT?', '.*\+CGDCONT:.*,.*,.*,.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CGEQOS?', '.*\+CGEQOS:.*,.*,.*,.*,.*,.*.*OK.*'))

        test.log.step("5. Activate, modify QOS and deactivate all PDP contexts one by one.")

        for cid in range(1, max_pdp + 1):
            test.log.info('Activate context no.' + str(cid) + ":")
            test.expect(test.dut.at1.send_and_verify('AT+CGACT=1,{}'.format(cid), '.*OK.*'))

            test.log.info('Change QOS settings of profile no.' + str(cid) + ':')
            test.expect(test.dut.at1.send_and_verify(
                'AT+CGEQOS=' + str(cid) + ',7,' + str(70 + cid) + ',' + str(70 + cid) + ',' + str(
                    140 + cid) + ',' + str(140 + cid), '.*OK.*'))

            test.log.info('Check state of current activated QOS settings:')
            test.expect(test.dut.at1.send_and_verify('AT+CEEQOSRDP',
                                                     '.*[+]CGEQOSRDP:' + str(cid) + ',7,' + str(70 + cid) + ',' + str(
                                                         70 + cid) + ',' + str(140 + cid) + ',' + str(140 + cid)
                                                     + '.*OK.*'))

            test.log.info('Activate new QOS settings via AT+CGCMOD write command:')
            test.expect(test.dut.at1.send_and_verify('AT+CGCMOD=' + str(cid), '.*\+CGCMOD:.*'))
            test.log.info('Check state of current activated QOS settings:')
            test.expect(test.dut.at1.send_and_verify('AT+CEEQOSRDP',
                                                     '.*[+]CGEQOSRDP:' + str(cid) + ',7,' + str(70 + cid) + ',' + str(
                                                         70 + cid) + ',' + str(140 + cid) + ',' + str(140 + cid)
                                                     + '.*OK.*'))

            test.log.info('Deactivate context no.' + str(cid) + ':')
            test.expect(test.dut.at1.send_and_verify('AT+CGACT=0,' + str(cid), '.*\+CGACT:.*'))

        test.log.step("6. Delete all context definitions and QOS profiles")
        for cid in range(1, max_pdp + 1):
            test.log.info('Delete PDP contexts')
            test.expect(test.dut.at1.send_and_verify('AT+CGEQOS={}'.format(cid), '.*\+CGCQOS:.*'))

        test.log.info("7. Define PDP context")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version="IPV4V6", ip_public=False)
        test.expect(connection_setup_dut.dstl_define_pdp_context())

    def cleanup(test):

        pass


if "__main__" == __name__:
    unicorn.main()
