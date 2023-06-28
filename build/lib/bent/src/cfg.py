#!/usr/bin/env python
import pkg_resources

def get_package_root(package_name):
    package = pkg_resources.get_distribution(package_name)
    return package.location

package_name = 'bent'
root_path = get_package_root(package_name) + '/bent'

data_dir = '{}data/'.format(root_path)

tmp_dir = '.tmp/'