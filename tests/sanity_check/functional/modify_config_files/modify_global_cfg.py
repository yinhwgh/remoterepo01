#responsible: johann.suhr@thalesgroup.com
#location: Berlin

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
import os

class Test(BaseTest):
    """ This test is modifying the global.cfg file. """

    def setup(test):
        test.dut.dstl_detect()
        pass

    def run(test):
        config_file = "global.cfg"

        # string appending the config file
        test_line = "global_foo=bar"

        # find path to config file
        current_dir = os.path.dirname(__file__)
        base_path = current_dir[:current_dir.rfind(os.path.join("unicorn", "tests")) + len("unicorn")]
        config_path = os.path.join(base_path, "config", config_file)
        global_global = os.path.join(base_path, "config", "global_global.cfg")

        # copy global.cfg to new file global_global.cfg
        with open(config_path) as f:
            lines = f.readlines()
            with open(global_global, 'w') as new_global_cfg:
                for line in lines:
                    new_global_cfg.write(line)

        # append test_line to file
        with open(global_global, 'a') as f:
            f.write("\n" + test_line)

        with open(global_global) as f:
            lines = f.readlines()
            test.expect(test_line in lines)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
