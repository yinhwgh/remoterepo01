#responsible: tomasz.witka@thalesgroup.com
#location: Wroclaw


import unicorn
import os
import subprocess
from core.basetest import BaseTest

class Test(BaseTest):
    """ To check if all adb interfaces can be handled if multiple are configured...
    """

    def setup(test):
        test.require_plugin('adb')
        from plugins.adb.interface_adb import AdbInterface
        test.adb_devices = []
        for a in dir(test):
            att = getattr(test, a)
            if isinstance(att, AdbInterface):
                test.adb_devices.append(att)

        test.testdir = os.path.realpath(os.path.dirname(__file__))
        test.testfile = os.path.realpath(os.path.join(os.path.dirname(__file__), "testfile"))
        test.log.info(test.testfile)
        with open(test.testfile, "wb") as f:
            f.seek((1024 * 1024) - 1)
            f.write(b'\0')
        
        test.testfile_size = os.path.getsize(test.testfile)
        test.log.info(test.testfile_size) 

    def run(test):
        for a in test.adb_devices:
            test.log.step('Checking send_and_verify on {}'.format(a))
            res = a.send_and_verify("ls")
            test.expect(res)
        
        for a in test.adb_devices:
            test.log.step('Checking send_and_verify with handle errors on {}'.format(a))
            test.dut.adb.send_and_verify('faultycommandxyz', handle_errors=True)
            test.expect('not found' in test.dut.adb.last_response)
        
        for a in test.adb_devices:
            test.log.step('Checking mkdir on {}'.format(a))
            res = test.dut.adb.mkdir('/tmp/demo')
            test.expect(res)
            res = test.dut.adb.send_and_receive('ls -la /tmp/demo')
            test.expect('total' in test.dut.adb.last_response)
        
        for a in test.adb_devices:
            test.log.step('Checking mkdir with handle errors on {}'.format(a))
            test.dut.adb.mkdir('/err', handle_errors=True)
            test.expect('can\'t create directory' in test.dut.adb.last_response)
        
        for a in test.adb_devices:
            test.log.step('Checking push/pull on {}'.format(a))
            a.push(test.testfile, '/tmp/demo')
            a.pull('/tmp/demo/testfile', test.workspace)


    def cleanup(test):
        for a in test.adb_devices:
            test.log.step('Removing files on {}'.format(a))
            res = test.dut.adb.send_and_verify('rm -rf /tmp/demo')
            test.expect(res)
        os.remove(test.testfile)

if "__main__" == __name__:
    unicorn.main()
