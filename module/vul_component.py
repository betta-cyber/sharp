# -*- coding: utf-8 -*-

import os


def check_component(data):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(current_dir + '/component.md') as f:
        components = [x.strip() for x in f.readlines()]

        # if data in components:
        for c in components:
            if c in data:
                return c

    return "unknown"

if __name__ == '__main__':
    check_component("1111")
