#responsible: johann.suhr@thalesgroup.com
#location: Berlin

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
import os


class Test(BaseTest):
    """ This test is modifying the local.cfg file. """

    def setup(test):
        test.dut.dstl_detect()
        pass

    def run(test):
        config_file = "local.cfg"

        # string appending the config file
        test_line = "local_foo=bar"

        # find path to config file
        current_dir = os.path.dirname(__file__)
        test.log.info("cur dir: " + current_dir)
        base_path = current_dir[:current_dir.rfind(os.path.join("unicorn", "tests")) + len("unicorn")]
        config_path = os.path.join(base_path, "config", config_file)
        local_local = os.path.join(base_path, "config", "local_local.cfg")

        # copy local.cfg to new file local_local.cfg
        with open(config_path) as f:
            lines = f.readlines()
            with open(local_local, 'w') as new_local_cfg:
                for line in lines:
                    new_local_cfg.write(line)

        # append test_line to file
        with open(local_local, 'a') as f:
            f.write("\n" + test_line)

        with open(local_local) as f:
            lines = f.readlines()
            test.expect(test_line in lines)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
