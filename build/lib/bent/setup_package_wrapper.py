#!/usr/bin/env python
import subprocess
import bent.src.cfg as cfg


def main():
    subprocess.call([f"{cfg.root_path}/setup_package.sh"])


if __name__ == "__main__":
    main()