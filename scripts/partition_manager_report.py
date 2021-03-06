#!/usr/bin/env python3
#
# Copyright (c) 2019 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: LicenseRef-BSD-5-Clause-Nordic

import argparse
import yaml
import platform
import sys
from os import path


def print_region(region, size, pm_config):
    # Prepare colors (color code taken from size_report)
    bcolors_ansi = {
        'HEADER'    : '\033[95m',
        'OKBLUE'    : '\033[94m',
        'OKGREEN'   : '\033[92m',
        'WARNING'   : '\033[93m',
        'FAIL'      : '\033[91m',
        'ENDC'      : '\033[0m',
        'BOLD'      : '\033[1m',
        'UNDERLINE' : '\033[4m'
    }
    if platform.system() == 'Windows':
        # Set all color codes to empty string on Windows
        bcolors = dict.fromkeys(bcolors_ansi, '')
    else:
        bcolors = bcolors_ansi

    # Print header
    print(bcolors['OKBLUE'] + f'{region} ({hex(size)} - {size/1024}kB):' + bcolors['ENDC'])

    # Sort partitions three times:
    #  1. On whether they are a container (has a 'span'), containers first.
    #  2. On size, descending.
    #  3. On address, ascending.
    sorted_pm_config = sorted(pm_config.keys(), key=lambda x: int('span' in pm_config[x]), reverse=True)
    sorted_pm_config = sorted(sorted_pm_config, key=lambda x: pm_config[x]['size'], reverse=True)
    sorted_pm_config = sorted(sorted_pm_config, key=lambda x: pm_config[x]['address'])

    # Create text lines
    lines = ['{}{}: {} ({}){}'.format(
                '| '+bcolors['WARNING'] if 'span' not in pm_config[name] else '+---'+bcolors['OKBLUE'],
                hex(pm_config[name]['address']),
                name,
                hex(pm_config[name]['size']),
                bcolors['ENDC'])
            for name in sorted_pm_config]
    maxlen = max(map(len, lines)) + 1

    # Add top and bottom of frame. Add dummy color so alignment always works.
    top_bottom = '+' + bcolors['OKBLUE'] + bcolors['ENDC']
    lines = [top_bottom, *lines, top_bottom]

    # Print left-justified, framed lines
    list(map(lambda s: print(s.ljust(maxlen, ' ') + '|' if s[0] != '+' else s.ljust(maxlen, '-') + '+'), lines))


def parse_args():
    parser = argparse.ArgumentParser(
        description='Parse given Partition Manager output YAML file and print a pretty report',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    # This argument has nargs set to '*' even though it is required. This is because of the logic associated with the
    # '--quiet' argument, which makes the script quit immediately. Hence we verify that this is set after 'quiet' is
    # checked.
    parser.add_argument('-i', '--input', required=True, type=str, nargs='*',
                        help='Path to the domain specific YAML files from Partition Manager')
    parser.add_argument('-q', '--quiet', required=False, action='store_true',
                        help="Don't print anything")

    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    if args.quiet:
        sys.exit(0)

    if not args.input:
        raise RuntimeError('No input files provided')

    for i in args.input:
        fn = path.basename(i)
        if '_' in fn:
            domain_name = fn[fn.index('partitions_') + len('partitions_'):fn.index('.yml')]
        else:
            domain_name = ''
        with open(i, 'r') as f:
            pm_config_primary = {k: v for k, v in yaml.safe_load(f).items() if v['region'] == 'flash_primary'}
        min_address = min((part['address'] for part in pm_config_primary.values() if 'address' in part))
        max_address = max((part['address'] + part['size'] for part in pm_config_primary.values() if 'address' in part))
        print_region(domain_name, max_address - min_address, pm_config_primary)


if __name__ == '__main__':
    main()
