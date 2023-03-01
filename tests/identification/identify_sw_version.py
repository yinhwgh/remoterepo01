
import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.devboard import devboard

class IdentifySWVersion(BaseTest):
    """Example test: Send AT command
    """
    def setup(test):
        try:
            test.log.info("expected FW version: %s\n" % (test.expected_fw_version))
        except AttributeError:
            test.log.info("missing expected FW version\n")
            test.fail()
        pass

    def run(test):
        # query product version with ati
        res = test.dut.at1.send_and_verify("ati", ".*OK")

        # log the message that module returned (last_response) as info
        test.log.info(test.dut.at1.last_response)

        # query product version with at^cicret
        res = test.dut.at1.send_and_verify("at^cicret=\"swn\"", ".*%s.*OK" % (test.expected_fw_version), critical=True)

        if res:
            # log the message that module returned (last_response) as info
            test.log.info(test.dut.at1.last_response)
        else:
            # cannot find the FW version in the answer

            # log the message that module returned (last_response) as info
            test.log.error(test.dut.at1.last_response)

            # log the message that module returned (last_response) as error
            test.log.info("invalid FW in device under test")
            test.fail()

    def cleanup(test):
        # nothing to do ...
        # ... if wrong FW version => turn off device, i.e. VBAT off ???
        pass

if "__main__" == __name__:
    unicorn.main()
