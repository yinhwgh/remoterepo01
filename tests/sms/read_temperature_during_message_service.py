#responsible: dan.liu@thalesgroup.com
#location: Dalian
#TC0096440.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory
from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory


class Test(BaseTest):
    """
    TC0096440.002 - ReadTemperatureDuringMessageService
    """

    def setup(test):
        dstl_detect(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        dstl_get_imei(test.dut)
        test.expect(dstl_delete_all_sms_messages(test.dut))

    def run(test):
            test.log.step('1. read the room temperature, at^sctm?')
            test.expect(test.dut.at1.send_and_verify('at^sctm=1,1', '.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('at^sctm?', '.*OK.*'))
            temp_list=[]
            temp_gap = 0
            test.log.info('write message to memory')
            test.expect(test.dut.dstl_select_sms_message_format(sms_format='Text'))
            sms_index_in_memory= test.dut.dstl_write_sms_to_memory\
                (sms_text="test message", return_index=True,
                                                          phone_num=test.dut.sim.nat_voice_nr)
            test.log.step('2. send one message, wait for 1 minutes and check temperature, at^sctm?')
            for i in range(1, 101):
                test.expect(test.dut.dstl_send_sms_message_from_memory
                            (message_index=sms_index_in_memory[0]))
                test.expect(test.dut.at1.send_and_verify('at^sctm?', '.*OK.*'))
                temperature_every_loop = test.dut.at1.last_response.split(',')[2].split('\r\n')[0]
                temp_list.append(temperature_every_loop)
                print(temp_list)
                if i > 1:
                    temp_gap = int(temp_list[i-1]) - int(temp_list[i-2])
                else:
                    pass
                test.log.info('temp_gap ={}'.format(temp_gap))
                test.expect(temp_gap < 2)


    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))


if "__main__" == __name__:
    unicorn.main()
