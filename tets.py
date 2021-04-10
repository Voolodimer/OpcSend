from pprint import pprint
from enum import Enum
from pathlib import Path
import yaml


class CheckResult(Enum):
    OK = 1
    HIGHER = 2
    LOWER = 3


def read_config():
    config = Path('config.yaml').read_text(encoding='utf-8')
    return yaml.safe_load(config)


class ThresholdChecker:

    def __init__(self, cfg):
        # for k in cfg.keys():
        #     self.__dict__[k] = cfg[k]

        self.parameter_name = cfg['name']
        self.opc_data_index = cfg['opc_data_index']
        self.base_value = cfg['base_value']
        self.deviation = cfg['deviation']
        self.lower_message_template = cfg['lower_message_template']
        self.upper_message_template = cfg['upper_message_template']

        self.upper_limit = self.base_value + self.deviation
        self.lower_limit = self.base_value - self.deviation
        self.result = None

    def check_threshold(self, opc_data):
        opc_value = opc_data[self.opc_data_index]
        if opc_value > self.upper_limit:
            self.result = CheckResult.HIGHER
        elif opc_value < self.lower_limit:
            self.result = CheckResult.LOWER
        else:
            self.result = CheckResult.OK

    def _lower_limit_message(self, opc_data):
        return self.lower_message_template.format(opc_data[self.opc_data_index])

    def _upper_limit_message(self, opc_data):
        return self.upper_message_template.format(opc_data[self.opc_data_index])

    def message(self, opc_data):
        if self.result == CheckResult.LOWER:
            return self._lower_limit_message(opc_data)
        elif self.result == CheckResult.HIGHER:
            return self._upper_limit_message(opc_data)
        else:
            return None


app_config = read_config()
thresholds_config = app_config['thresholds']

thresholds = []
for (threshold_key) in thresholds_config:
    #print(threshold_key)
    thresholds.append(ThresholdChecker(threshold_key))

opc_fake_data = [1, 42, 3, 4, 5, 6]


for t in thresholds:
    t.check_threshold(opc_fake_data)
    #pprint(t.__dict__)
    pprint(t.message(opc_fake_data))

# TODO notes:
# - validation: https://docs.python-cerberus.org/en/stable/schemas.html, https://pypi.org/project/pykwalify/,
# https://stackoverflow.com/a/46626418
# - close OPC client
# - use .gitignore
# - use requirements.txt


