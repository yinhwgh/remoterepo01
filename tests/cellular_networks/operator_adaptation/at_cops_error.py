#responsible: dan.liu@thalesgroup.com
#location: Dalian
#TC0010358.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network

class FfsViaAtFileOpenCloseRemove(BaseTest):

    def setup(test):

        test.log.info("TC0010358.001 - TpCopsError ")
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_enter_pin())


    def run(test):

        test.expect(test.dut.at1.send_and_verify("at+cmee=1", ".*OK.*"))

        test.log.info("1.AT+CMEE=1")
        test.log.info("1.1 mode is invalid")
        test.expect(test.dut.at1.send_and_verify("at+cops=5", ".*ERROR: 21.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=255", ".*ERROR: 21.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=-1", ".*ERROR: 21.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=3.5", ".*ERROR: 21.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=A", ".*ERROR: 21.*"))

        test.log.info("1.2 at+cops=0,with invalid format and poer value")
        test.expect(test.dut.at1.send_and_verify("at+cops=0,3,DSDADA", ".*ERROR: 21.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=0,-1,ddddd", ".*ERROR: 21.*"))

        test.log.info("1.3 at+cops=1,with invalid format and poer value")
        test.expect(test.dut.at1.send_and_verify("at+cops=1,4,ssssss", ".*ERROR: 21.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=1,a,sasasas", ".*ERROR: 21.*"))

        test.log.info("1.4 at+cops=2,with invalid format and poer value")
        test.expect(test.dut.at1.send_and_verify("at+cops=2,4,ssssss", ".*ERROR: 21.*"))
        test.dut.at1.send_and_verify("at+cops=2,a,sasasas", ".*ERROR: 21.*")

        test.log.info("1.5 at+cops=3,with invalid format and poer value")
        test.expect(test.dut.at1.send_and_verify("at+cops=3,-1,ssssss", ".*ERROR: 21.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=3,255,sasasas", ".*ERROR: 21.*"))

        test.log.info("1.6 at+cops=4,with invalid format and poer value")
        test.expect(test.dut.at1.send_and_verify("at+cops=4,s,ssssss", ".*ERROR: 21.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=4,8,sasasas", ".*ERROR: 21.*"))

        test.expect(test.dut.at1.send_and_verify("at+cmee=2", ".*OK.*"))

        test.log.info("2 .AT+CMEE=2")

        test.log.info("2.1 mode is invalid")
        test.expect(test.dut.at1.send_and_verify("at", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=5", ".*invalid.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=255", ".*invalid.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=-1", ".*invalid.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=3.5", ".*invalid.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=A", ".*invalid.*"))

        test.log.info("2.2 at+cops=0,with invalid format and poer value")
        test.expect(test.dut.at1.send_and_verify("at+cops=0,3,DSDADA", ".*invalid.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=0,-1,ddddd", ".*invalid.*"))

        test.log.info("2.3 at+cops=1,with invalid format and poer value")
        test.expect(test.dut.at1.send_and_verify("at+cops=1,4,ssssss", ".*invalid.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=1,a,sasasas", ".*invalid.*"))

        test.log.info("2.4 at+cops=2,with invalid format and poer value")
        test.expect(test.dut.at1.send_and_verify("at+cops=2,4,ssssss", ".*invalid.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=2,a,sasasas", ".*invalid.*")
)
        test.log.info("2.5 at+cops=3,with invalid format and poer value")
        test.expect(test.dut.at1.send_and_verify("at+cops=3,-1,ssssss", ".*invalid.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=3,255,sasasas", ".*invalid.*"))

        test.log.info("2.6 at+cops=4,with invalid format and poer value")
        test.expect(test.dut.at1.send_and_verify("at+cops=4,s,ssssss", ".*invalid.*"))
        test.expect(test.dut.at1.send_and_verify("at+cops=4,8,sasasas", ".*invalid.*"))


    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
