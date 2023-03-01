#responsible: matthias.reissner@thalesgroup.com
#location: Berlin
#TC

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network

class Test(BaseTest):
    """Example test: Send AT command
    """
    def setup(test):

        # restart the DUT module
        #restart(test.dut)

        # Check SIM Pin and attach DUT to network
        if (not test.dut.dstl_register_to_network()):
            test.log.info("Not able to attach DUT, abort test.")
            test.expect(False, critical=True)


        # Individual setup for DUT module
        test.dut.at1.send_and_verify("at+cmee=2")
        test.dut.at1.send_and_verify("at+creg=2")
        test.dut.at1.send_and_verify("at+cereg=2")
        test.dut.at1.send_and_verify("at^scks=1")
        test.dut.at1.send_and_verify("at^slcc=1")


        # restart the R1 module
        #restart(test.r1)

        # Check SIM Pin and attach R1 to network
        if (not test.r1.dstl_register_to_network()):
            test.log.info("Not able to attach R1, abort test.")
            test.expect(False, critical=True)


        # Individual setup for R1 module
        test.r1.at1.send_and_verify("at+cmee=2")
        test.r1.at1.send_and_verify("at+creg=2")
        test.r1.at1.send_and_verify("at+cereg=2")
        test.r1.at1.send_and_verify("at^scks=1")
        test.r1.at1.send_and_verify("at^slcc=1")

        pass

    def run(test):

        # Configure eCall
        test.dut.at1.send_and_verify("at^sind=ecallda,1")
        test.dut.at1.send_and_verify("at^sind=ecallco,1")
        test.dut.at1.send_and_verify("at^sind=ecaller,1")
        test.dut.at1.send_and_verify("at^sind=audio,1")
        test.dut.at1.send_and_verify("at^sind=call,1")
        test.dut.at1.send_and_verify("at^sind=imsi,1")
        test.dut.at1.send_and_verify("at^sind=simstatus,1")
        test.dut.at1.send_and_verify("at^sind=simlocal,1")
        test.dut.at1.send_and_verify("at^sind=simdata,1")
        test.dut.at1.send_and_verify("at^sind=ceer,1,99")
        test.dut.at1.send_and_verify("at^scfg?")
        test.dut.at1.send_and_verify("at^sind?")
        # Start eCall
        test.expect(test.dut.at1.send_and_verify("at+cecall=0,\"+493038307460\""))
        # Wait for hang up and URC's
        test.dut.at1.wait_for(".*NO CARRIER.*", timeout = 120)
        test.sleep(5)
        test.dut.at1.wait_for(".*", timeout = 1)


        # Start voice call
        test.dut.at1.send_and_verify("atd" + str(test.r1.sim.voice_nr) + ";")
        test.r1.at1.wait_for(".*RING.*", timeout = 60)
        if ("RING" in test.r1.at1.last_response):
            test.r1.at1.send_and_verify("ata")
            test.sleep(10)
            test.dut.at1.send_and_verify("at+clcc")
            test.dut.at1.send_and_verify("at+cpas")
            test.r1.at1.send_and_verify("at+clcc")
            test.r1.at1.send_and_verify("at+cpas")
            test.sleep(5)
            test.dut.at1.send_and_verify("at+chup")
            test.sleep(5)
            test.dut.at1.wait_for(".*", timeout = 1)


        pass

    def cleanup(test):
        # Configure eCall
        test.dut.at1.send_and_verify("at^sind=ecallda,0")
        test.dut.at1.send_and_verify("at^sind=ecallco,0")
        test.dut.at1.send_and_verify("at^sind=ecaller,0")
        test.dut.at1.send_and_verify("at^sind=audio,0")
        test.dut.at1.send_and_verify("at^sind=call,0")
        test.dut.at1.send_and_verify("at^sind=imsi,0")
        test.dut.at1.send_and_verify("at^sind=simstatus,0")
        test.dut.at1.send_and_verify("at^sind=simlocal,0")
        test.dut.at1.send_and_verify("at^sind=simdata,0")
        test.dut.at1.send_and_verify("at^sind=ceer,0")
        test.dut.at1.send_and_verify("at^scfg?")
        test.dut.at1.send_and_verify("at^sind?")
        pass

if "__main__" == __name__:
    unicorn.main()
