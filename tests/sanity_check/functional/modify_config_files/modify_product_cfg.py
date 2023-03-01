#responsible: johann.suhr@thalesgroup.com
#location: Berlin

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
import os


class Test(BaseTest):
    """ This test is modifying the bobcat_W.cfg file. """

    def setup(test):
        test.dut.dstl_detect()
        pass

    def run(test):
        test.log.info(test.dut.restart_time)

        if (test.dut.project == "SERVAL"):
            config_file = "serval.cfg"
        elif (test.dut.project == "BOBCAT"):
            config_file = "bobcat.cfg"
        else:
            config_file = "cougar.cfg"

        # string that gets appended to the config file
        test_line = "product_foo=bar"

        # find path to config file
        current_dir = os.path.dirname(__file__)
        print(current_dir)
        base_path = current_dir[:current_dir.rfind("unicorn\\tests") + len("unicorn")]
        config_path = base_path + '\config\\devconfig\\' + config_file

        # append test_line to file
        with open(config_path, 'a') as f:
            f.write("\n" + test_line)

        with open(config_path) as f:
            lines = f.readlines()
            test.expect(test_line in lines)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
