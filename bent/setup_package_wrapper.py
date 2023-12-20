#!/usr/bin/env python
import subprocess
import bent.src.cfg as cfg

def main():
    subprocess.call(['{}/setup_package.sh'.format(cfg.root_path)])

if __name__ == '__main__':
    main()