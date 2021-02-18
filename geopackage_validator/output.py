import json
from datetime import datetime
from typing import Dict, List

import pkg_resources  # part of setuptools


def log_output(
    results: List[Dict[str, List[str]]],
    success: bool,
    filename: str = "",
    validations_executed: List[str] = None,
    start_time: datetime = datetime.now(),
    duration_seconds: float = 0,
) -> None:
    if validations_executed is None:
        validations_executed = []

    script_version = pkg_resources.get_distribution("pdok_geopackage_validator").version
    print(
        json.dumps(
            {
                "geopackage_validator_version": script_version,
                "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "duration_seconds": round(duration_seconds),
                "geopackage": filename,
                "success": success,
                "validations_executed": validations_executed,
                "results": results,
            },
            indent=4,
        )
    )
