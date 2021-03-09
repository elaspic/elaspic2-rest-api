#!/usr/bin/env python
import sys
from pathlib import Path

from ruamel.yaml import YAML


def main(meta_filename: Path) -> None:
    yaml = YAML()
    yaml.indent(sequence=4, offset=2)
    meta = yaml.load(meta_filename)

    env = {}
    env["dependencies"] = meta["requirements"]["run"]
    yaml.dump(env, sys.stdout)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help="Location of the meta.yaml file.")
    args = parser.parse_args()

    meta_filename = Path(args.filename).resolve(strict=True)

    main(meta_filename)
