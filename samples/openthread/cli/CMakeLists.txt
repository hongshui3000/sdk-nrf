#
# Copyright (c) 2020 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: LicenseRef-BSD-5-Clause-Nordic
#
cmake_minimum_required(VERSION 3.13.1)

list(INSERT OVERLAY_CONFIG 0 ../common/overlay-ot-defaults.conf)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})

project(openthread_cli)

target_sources(app PRIVATE src/main.c)

target_sources_ifdef(CONFIG_BT app PRIVATE src/ble.c)
