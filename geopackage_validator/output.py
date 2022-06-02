import json
from datetime import datetime
from typing import Dict, List
from collections import OrderedDict

import yaml

from geopackage_validator import __version__


def represent_ordereddict(dumper, data):
    """
    Represent method for pyyaml.
    Shamelessly copied from the python3 part of this answer:
     https://stackoverflow.com/questions/16782112/can-pyyaml-dump-dict-items-in-non-alphabetical-order#answer-16782282
    """
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode("tag:yaml.org,2002:map", value)


yaml.add_representer(OrderedDict, represent_ordereddict)


def log_output(
    results: List[Dict[str, List[str]]],
    success: bool,
    filename: str = "",
    validations_executed: List[str] = None,
    start_time: datetime = datetime.now(),
    duration_seconds: float = 0,
    as_yaml: bool = False,
) -> None:
    if validations_executed is None:
        validations_executed = []

    print_output(
        OrderedDict(
            [
                ("geopackage_validator_version", __version__),
                ("start_time", start_time.strftime("%Y-%m-%dT%H:%M:%S.%f")),
                ("duration_seconds", round(duration_seconds)),
                ("geopackage", filename),
                ("success", success),
                ("validations_executed", validations_executed),
                ("results", results),
            ]
        ),
        as_yaml,
    )


def print_output(python_object, as_yaml, yaml_indent=2):
    if as_yaml:
        content = yaml.dump(python_object, indent=yaml_indent)
    else:
        content = json.dumps(python_object, indent=4)
    print(content)
