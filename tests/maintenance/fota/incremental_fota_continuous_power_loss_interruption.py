# responsible: kamil.kedron@globallogic.com
# location: Wroclaw
# TC0105183.001 - IncrementalFotaContinuousPowerLossInterruption1
# TC0105184.001 - IncrementalFotaDurationPowerLossInterruption

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.attach_to_network import attach_to_network
import sys


class Test(BaseTest):
    """Example test: Send AT command
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK", timeout=10))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK", timeout=10))
        dstl_restart(test.dut)

        test.log.info("\n0. Read parameters.")

        try:
            test.url = "http://217.182.72.145:10015"
        except IndexError as ex:
            test.url = "http://217.182.72.145:10015"


        attach_to_network(test.dut)
        test.dut.at2.open()
        test.log.info("Url = " + test.url)

    def run(test):
        """
        author mateusz.strzelczyk@globallogic.com
        Location: Wroclaw
        """

        test.log.info("\n1. Clear memory and check if is empty")
        test.expect(test.dut.at1.send_and_verify("AT^SNFOTA=\"act\",5", ".*OK|ERROR.*", timeout=10))
        test.expect(test.dut.at1.send_and_verify("AT^SNFOTA=\"act\",4", "OK", timeout=10))

        test.log.info("\n2. Set up connection to server")
        test.expect(test.dut.at1.send_and_verify("AT^SNFOTA=\"url\"," + test.url, "OK", timeout=10))
        test.expect(test.dut.at1.send_and_verify("AT^SNFOTA=\"progress\",5", "OK", timeout=10))
        test.expect(test.dut.at1.send_and_verify("AT^SNFOTA=\"urc\",1", "OK", timeout=10))
        test.expect(test.dut.at1.send_and_verify("AT^SNFOTA=\"conId\",1", "OK", timeout=10))
        test.expect(test.dut.at1.send_and_verify("AT^SNFOTA?", "OK", timeout=10))

        test.log.info("\n3. Check if software is available on server")
        test.expect(test.dut.at1.send_and_verify("AT^SNFOTA=\"act\",1", "OK", timeout=10))
        test.expect(test.dut.at1.wait_for(".*SNFOTA: \"act\",1,0*"))

        test.log.info("\n4. Download software")
        test.expect(test.dut.at1.send_and_verify("AT^SNFOTA=\"act\",2", "OK", timeout=10))
        while "SNFOTA: \"act\",2,0,100" not in test.dut.at1.read():
            """Brakuje mechanizmu postępowania w przypadku błędu podczas downloadu softu"""
            test.sleep(30)
        test.expect(test.dut.at1.send_and_verify("AT^SNFOTA=\"act\",4", ".*SNFOTA: \"act\",4,0,1.*OK.*", timeout=10))
        test.expect(test.dut.at1.send_and_verify("AT^SNFOTA=\"act\",3", "OK", timeout=10))

        test.log.info("\n5. Try to update software with power cutting")
        test.expect(test.dut.at1.send_and_verify("AT^SFDL=2", "OK", timeout=10))
        time = 1
        interval = 0.005

        while True:
            result = test.reset_module()
            if result == False:
                return
            else:
                time += interval
                test.log.info(f"Sleep time is: {time}s")
                test.sleep(time)

    def cleanup(test):
        test.log.info("\n6. Clear memory")
        test.expect(test.dut.at1.send_and_verify("AT^SNFOTA=\"act\",4", "OK", timeout=10))
        test.expect(test.dut.at1.send_and_verify("AT^SNFOTA=\"act\",5", "OK", timeout=10))
        test.expect(test.dut.at1.send_and_verify("AT^SNFOTA=\"act\",4", ".*SNFOTA: \"act\",4,.*,0.*OK.*", timeout=10))

        test.log.info("\n7. Check current software")
        dstl_detect(test.dut)

        test.dut.at1.send_and_verify("AT&F", ".*OK.*", timeout=10)

    def reset_module(test):
        test.dut.at1.read()
        test.dut.at2.read()

        if "UPDATER" in test.dut.at2.last_response:
            test.log.info("UPDATER matched. Module will be restarted")
            test.dut.devboard.send_and_verify("CONF:GPIO:PG0 OUTPP", "OK", timeout=10)
            test.dut.devboard.send_and_verify("OUTP:GPIO:PG0 0", "OK", timeout=10)
            test.sleep(2)
            test.dut.devboard.send_and_verify("CONF:GPIO:PG0 OUTPP", "OK", timeout=10)
            test.dut.devboard.send_and_verify("OUTP:GPIO:PG0 1", "OK", timeout=10)
            return True
        if "SYSSTART" in test.dut.at1.last_response:
            test.log.info("SYSSTART matched. Test will finish")
            return False

        # test.log.info("Module does not responding, trying to reconnect.")
        # test.dut.devboard.send("OUTP:EMRG on")
        # test.sleep(5)
        # test.dut.devboard.send("OUTP:EMRG off")
        #
        # if "UPDATER" in test.dut.at2.last_response:
        #     return True
        # if "SYSSTART" in test.dut.at1.last_response:
        #     return False
        #
        # test.dut.devboard.send("MC:IGT=555")

        # if "UPDATER" in test.dut.at2.last_response:
        #     return True
        # if "SYSSTART" in test.dut.at1.last_response:
        #     return False
        # else:
        #     test.log.info("Module does not wake up after power loss!")
        #     test.fail()


if "__main__" == __name__:
    unicorn.main()
