# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

class JetStream(object):

    # A dictionary of {start: [{'finish': finish, 'cost': cost}]}
    jetstreams = {}

    def __init__(self, base_cost):
        self.base_cost = base_cost
        self.path_length = 0

    @classmethod
    def from_file(cls, file_path):
        ifs = open(file_path)
        # First line is base cost
        base_cost = int(ifs.readline().strip())
        logger.debug('Base cost is %s', base_cost)
        js = cls(base_cost)
        # Every subsequent line represents a jetstream segment
        for line in ifs:
            line = line.strip()
            if not line:  # probably EOF
                continue
            logger.debug('Line is %s', line)
            start, finish, cost = [int(s) for s in line.split(' ')]
            js.jetstreams.setdefault(start, []).append(
                {'finish': finish, 'cost': cost})
            # Keep track of the furthest jetstream segment finish to find out
            # how far the end point is
            js.path_length = max(js.path_length, finish)
        logger.debug('Max path length is %s', js.path_length)
        logger.debug('Parsed jetstream map is %s', js.jetstreams)
        ifs.close()
        return js
