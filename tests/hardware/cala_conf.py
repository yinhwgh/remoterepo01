# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0095294.002


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration import set_alarm
from dstl.hardware import set_real_time_clock
from dstl.hardware import get_real_time_clock
import datetime


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.expect(test.dut.dstl_set_real_time_clock(time="21/05/10,07:00:00"))
        test.log.info('1. Try to set alarm only with time parameter. Clear alarm.')
        test.expect(test.dut.dstl_set_alarm_time("21/05/10,08:30:00"))
        test.expect(test.dut.dstl_clear_alarm())
        test.log.info('2. Try to set alarm only with time,type parameter. Clear alarm.')
        test.expect(test.dut.dstl_set_alarm_time("21/05/10,08:30:00", type='0'))
        test.expect(test.dut.dstl_clear_alarm())
        test.log.info('3. Try to set alarm only with time,text parameter. Clear alarm.')
        test.expect(test.dut.dstl_set_alarm_time("21/05/10,08:30:00", text='abcd'))
        test.expect(test.dut.dstl_clear_alarm())
        test.log.info('4. Try to set all alarm only with time,n parameter. Clear alarm.')
        max_index = test.dut.dstl_get_max_alarm_index()
        test.log.info('5. Try to set all alarm only with time,n,text parameter. Clear alarm.')
        for i in range(0, max_index + 1):
            test.expect(test.dut.dstl_set_alarm_time("21/05/10,08:30:00", index=i, text='test'))
        for i in range(0, max_index + 1):
            test.expect(test.dut.dstl_clear_alarm(i))
        test.log.info('6. Try to set all alarm only with time,n,type parameter. Clear alarm.')
        for i in range(0, max_index + 1):
            test.expect(test.dut.dstl_set_alarm_time("21/05/10,08:30:00", index=i, type='0'))
        for i in range(0, max_index + 1):
            test.expect(test.dut.dstl_clear_alarm(i))
        test.log.info('7. Try to set all alarm only with time,n,type,text parameter. Clear alarm.')
        for i in range(0, max_index + 1):
            test.expect(test.dut.dstl_set_alarm_time("21/05/10,08:30:00", index=i, type='0',
                                                     text='test'))
        for i in range(0, max_index + 1):
            test.expect(test.dut.dstl_clear_alarm(i))
        test.log.info('8. Try to set all alarm with 16 characters long text. Clear alarm.')
        for i in range(0, max_index + 1):
            test.expect(test.dut.dstl_set_alarm_time("21/05/10,08:30:00", index=i,
                                                     text='test012345678901'))
        for i in range(0, max_index + 1):
            test.expect(test.dut.dstl_clear_alarm(i))
        test.log.info('9. Try to set all alarm time,n,text parameter.Wait for all alarms.')
        current_time = test.dut.dstl_get_real_time_clock()
        for i in range(0, max_index + 1):
            alarmtime = test.add_min(current_time, i + 1)
            test.expect(test.dut.dstl_set_alarm_time(alarmtime, index=i,
                                                     text=f'TEST ALARM {i + 1}'))
        for i in range(0, max_index + 1):
            test.expect(test.dut.dstl_wait_for_alarm(text=f'TEST ALARM {i + 1}',
                                                     wait_time=62))

        test.log.info('10. Try to set all alarm with time,n,text parameter.Try to override all'
                      ' alarms with new data.')
        for i in range(0, max_index + 1):
            test.expect(test.dut.dstl_set_alarm_time("21/05/10,08:30:00", index=i,
                                                     text='test012345678901'))
        for i in range(0, max_index + 1):
            test.expect(test.dut.dstl_set_alarm_time("21/05/11,09:30:00", index=i,
                                                     text='abcdefghi'))
        for i in range(0, max_index + 1):
            test.expect(test.dut.dstl_clear_alarm(i))

    def cleanup(test):
        pass

    def add_min(test, origin_time, delta_min):

        sss = datetime.datetime.strptime(origin_time, "%y/%m/%d,%H:%M:%S")
        res1 = sss + datetime.timedelta(minutes=delta_min)
        t = res1.strftime('%y/%m/%d,%H:%M:%S')
        return t


if "__main__" == __name__:
    unicorn.main()
