#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0105603.001
#Hints:
#ntp_address should be defined in local.cfg currently,shuch as ntp_address="10.163.27.30"
#apn should be defined in local.cfg currently,shuch as apn="internet"
import unicorn
import re

from core.basetest import BaseTest
from tests.rq6 import smart_meter_init_module_normal_flow
from tests.rq6 import smart_meter_read_status_normal_flow

class Test(BaseTest):
    def setup(test):
        pass

    def run(test):
        test.log.info('***** 1.Init module *****')
        smart_meter_init_module_normal_flow.uc_init_module(test,1,14)
        test.log.info('***** 2.Save some message to SIM card *****')
        send_messages_to_sim(test)
        test.log.info('***** 3.Execute uc_read_status *****')
        smart_meter_read_status_normal_flow.uc_read_status(test)

    def cleanup(test):
        pass
def send_messages_to_sim(test):
    test.expect(test.dut.at1.send_and_verify('AT+CMGS="{}"'.format(test.dut.sim.nat_voice_nr), '.*>.*', wait_for=".*>.*"))
    test.expect(test.dut.at1.send_and_verify('TestMessage1', end="\u001A", expect="\+CMGS:.*0", timeout=3))
    test.expect(test.dut.at1.send_and_verify('AT+CMGS="{}"'.format(test.dut.sim.nat_voice_nr), '.*>.*', wait_for=".*>.*"))
    test.expect(test.dut.at1.send_and_verify('TestMessage2', end="\u001A", expect="\+CMGS:.*0", timeout=3))
    test.expect(test.dut.at1.send_and_verify('AT+CMGS="{}"'.format(test.dut.sim.nat_voice_nr), '.*>.*', wait_for=".*>.*"))
    test.expect(test.dut.at1.send_and_verify('TestMessage3', end="\u001A", expect="\+CMGS:.*0", timeout=3))
    test.expect(test.dut.at1.send_and_verify('AT+CMGS="{}"'.format(test.dut.sim.nat_voice_nr), '.*>.*', wait_for=".*>.*"))
    test.expect(test.dut.at1.send_and_verify('TestMessage4', end="\u001A", expect="\+CMGS:.*0", timeout=3))
    test.expect(test.dut.at1.send_and_verify('AT+CMGS="{}"'.format(test.dut.sim.nat_voice_nr), '.*>.*', wait_for=".*>.*"))
    test.expect(test.dut.at1.send_and_verify('TestMessage5', end="\u001A", expect="\+CMGS:.*0", timeout=3))
    test.expect(test.dut.at1.send_and_verify("AT+CPMS?", "0"))
    result = re.findall(r"\+CPMS: \"\w+\",(\d+),\d+", test.dut.at1.last_response)
    if int(result[0])<5:
        test.log.error('message number should more than 5')

    return True


if "__main__" == __name__:
    unicorn.main()
