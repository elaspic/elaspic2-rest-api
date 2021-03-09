#!/usr/bin/env python
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from ruamel.yaml import YAML


def main(meta_filename: Path):
    yaml = YAML()
    yaml.indent(sequence=4, offset=2)
    meta = yaml.load(meta_filename)

    package_versions = load_conda_env()
    packages_new = []
    for package in meta["requirements"]["run"][:]:
        package_name = package.split("=")[0].strip()
        package_version = package_versions[package_name]
        packages_new.append(f"{package_name} ={package_version}")
    meta["requirements"]["run"] = packages_new

    yaml.dump(meta, meta_filename)


def load_conda_env() -> Dict[str, str]:
    proc = subprocess.run(
        shlex.split("conda env export --no-builds --ignore-channels"), capture_output=True
    )
    result = YAML().load(proc.stdout.decode())
    package_versions = _extract_package_versions(result["dependencies"])
    return package_versions


def _extract_package_versions(dependencies: List[Any]) -> Dict[str, str]:
    package_versions = {}
    for package in dependencies:
        if not isinstance(package, str):
            continue
        name, version = package.split("=")
        versions = version.split(".")
        if tuple(versions[:2]) not in [("0", "0"), ("0", "1")]:
            version = ".".join(versions[:2])
        package_versions[name] = version
    return package_versions


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help="Location of the meta.yaml file.")
    args = parser.parse_args()

    meta_filename = Path(args.filename).resolve(strict=True)

    main(meta_filename)
