# responsible: yunhui.zhang@thalesgroup.com
# location: Beijing
# TC0093092.001 - TpAtSindUsimIdentity

"""
Check ^SIND: "iccid" and ^SIND: "imsi" -URC
Note: there is not ^SIND: "imsi" -URC in Viper
Please use sim card with different length(12/18/19/20) of ICCID to test this case.
"""


import unicorn
import time
import re
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.auxiliary import check_urc
from dstl.security import lock_unlock_sim
from dstl.auxiliary.devboard import *
from dstl.status_control import extended_indicator_control


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        time.sleep(2)

    def run(test):
        test.log.info('**** TpAtSindUsimIdentity - Start ****')

        test.log.info('*** 1: check the URC CIEV: iccid ****')
        test.log.info('**** init: get iccid with at^scid ****')
        test.expect(test.dut.at1.send_and_verify("AT^SCID", ".*OK*."))
        iccid_sim = re.search("\^SCID: \w{12,20}", test.dut.at1.last_response).group(0)[7:]
        test.log.info('**** init: get euiccid with at^sind ****')
        test.expect(test.dut.dstl_check_indicator_value("euiccid", 0))

        groups = re.search(".*\w{16,32}.*", test.dut.at1.last_response)
        if groups is None:
            test.expect(False, critical=True,
                        msg="SIM does not support EUICCID field with content, perform test with another SIM card! " \
                            "- ABORTING")
        euiccid_sind = groups.group(0)[17:]
        test.log.info('*** check default values of at^sind? for iccid ****')
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK*."))

        test.log.info('*** check test command of at^sind ****')
        if not test.expect(test.dut.at1.send_and_verify("at^sind=?", "\^SIND:.*\(iccid,\(20\)\).*OK")):
            test.log.info("parameter <indDescr>=iccid does not exist")

        test.log.info('*** check read command of at^sind ****')
        if not test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND:.*iccid,0,\"\w{12,20}\".*OK")):
            test.log.info("parameter <indDescr>=iccid does not show correct value")
        test.log.info('*** enable iccid ****')
        test.expect(test.dut.dstl_enable_one_indicator("iccid"))
        test.expect(test.dut.dstl_check_indicator_value("iccid", 1))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK*."))

        test.log.info('*** check default values of at^sind? for iccid ****')
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK*."))
        if not test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND:.*iccid,0,\"\w{12,20}\".*OK")):
            test.log.info("parameter <indDescr>=iccid is not set to correct default value (<>0)")
        test.expect(test.dut.dstl_check_indicator_value("iccid", 0))
        test.expect(test.dut.at1.send_and_verify("ATZ", ".*OK*."))

        test.log.info('*** check read command of at^sind ****')
        if not test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND:.*iccid,1,\"\w{12,20}\".*OK")):
            test.log.info("parameter <indDescr>=iccid is not set to correct default value (<>1)")
        test.expect(test.dut.dstl_check_indicator_value("iccid", 1))

        test.log.info('*** 1.1: check the URC CIEV: iccid after restart ****')
        test.dut.dstl_restart()
        test.log.info('*** check URC: +CIEV: iccid after restart ****')
        test.log.info('**** Waiting for "iccid" URC ****')
        if test.expect(test.dut.dstl_check_urc(iccid_sim)):
            test.log.info('**** URC CIEV: iccid occurs *******')
            test.log.info('**** URC CIEV: iccid  is same with the value from at^scid *******')
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK*."))

        test.log.info('*** 1.2: check the URC CIEV: iccid after SIM deactivation/activation ****')
        test.expect(test.dut.at1.send_and_verify("AT^SCKS=1", ".*OK*."))
        test.dut.dstl_remove_sim()
        test.log.info('**** Waiting for "iccid" URC ****')
        test.expect(test.dut.dstl_check_urc("+CIEV: iccid,\"\""))
        time.sleep(2)
        test.dut.dstl_insert_sim()
        test.log.info('**** Waiting for "iccid" URC ****')
        if test.expect(test.dut.dstl_check_urc(iccid_sim)):
            test.log.info('**** URC CIEV: iccid occurs *******')
            test.log.info('**** URC CIEV: iccid  is same with the value from at^scid *******')

        test.log.info('*** 2: check the URC CIEV: euiccid ****')
        test.dut.dstl_lock_sim()
        test.log.info('*** check default values of at^sind? for euiccid ****')
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK*."))

        test.log.info('*** check test command of at^sind ****')
        if not test.expect(test.dut.at1.send_and_verify("at^sind=?", "\^SIND:.*\(euiccid,\(16\)\).*OK")):
            test.log.info("parameter <indDescr>=euiccid does not exist")

        test.log.info('*** check read command of at^sind ****')
        if not test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND:.*euiccid,0,\"\w{16,32}\".*OK")):
            test.log.info("parameter <indDescr>=euiccid does not show correct value")
        test.log.info('*** enable euiccid ****')
        test.expect(test.dut.dstl_enable_one_indicator("euiccid"))
        test.expect(test.dut.dstl_check_indicator_value("euiccid", 1))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK*."))

        test.log.info('*** check default values of at^sind? for euiccid ****')
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK*."))
        if not test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND:.*euiccid,0,\"\w{16,32}\".*OK")):
            test.log.info("parameter <indDescr>=iccid is not set to correct default value (<>0)")
        test.expect(test.dut.dstl_check_indicator_value("euiccid", 0))
        test.expect(test.dut.at1.send_and_verify("ATZ", ".*OK*."))

        test.log.info('*** check read command of at^sind ****')
        if not test.expect(test.dut.at1.send_and_verify("at^sind?", "\^SIND:.*euiccid,1,\"\w{18,32}\".*OK")):
            test.log.info("parameter <indDescr>=euiccid is not set to correct default value (<>1)")
        test.expect(test.dut.dstl_check_indicator_value("euiccid", 1))

        test.log.info('*** 2.1: check the URC CIEV: euiccid after restart ****')
        test.dut.dstl_restart()
        test.log.info('*** check URC: +CIEV: euiccid after restart ****')
        test.log.info('**** Waiting for "euiccid" URC ****')
        if test.expect(test.dut.dstl_check_urc(euiccid_sind)):
            test.log.info('**** URC CIEV: euiccid occurs *******')
            test.log.info('**** URC CIEV: euiccid  is same with the value from at^sind *******')
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK*."))

        test.log.info('*** 2.2: check the URC CIEV: euiccid after SIM deactivation/activation ****')
        test.expect(test.dut.at1.send_and_verify("AT^SCKS=1", ".*OK*."))
        test.dut.dstl_remove_sim()
        test.log.info('**** Waiting for "euiccid" URC ****')
        test.expect(test.dut.dstl_check_urc("+CIEV: euiccid,\"\""))
        time.sleep(2)
        test.dut.dstl_insert_sim()
        test.log.info('**** Waiting for "euiccid" URC ****')
        if test.expect(test.dut.dstl_check_urc(euiccid_sind)):
            test.log.info('**** URC CIEV: euiccid occurs *******')
            test.log.info('**** URC CIEV: euiccid  is same with the value from at^sind *******')

        test.log.info('**** Test end ***')

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK*."))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK*."))


if __name__ == "__main__":
    unicorn.main()
