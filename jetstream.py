# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

logger = logging.getLogger(__name__)

class JetStream(object):

    # A dictionary of {start: [{'finish': finish, 'cost': cost}]}
    jetstreams = {}
    padded = False

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

    def pad_jetstream_with_base_steps(self):
        """The base jetstream data does not include the steps possible with
        traveling one mile at the base cost. We need to pad the jetstream data
        with those one-mile-steps."""
        if not self.path_length or not self.jetstreams:
            raise RuntimeError('Please initialize the jetstream data first.')
        if self.padded:
            # No need to do this twice.
            return
        for i in xrange(self.path_length):
            self.jetstreams.setdefault(i, []).append(
                {'finish': i+1, 'cost': self.base_cost, 'no_stream': True}
            )

    def find_optimal_path(self):
        self.pad_jetstream_with_base_steps()
        # Our upper bound is ignoring all jetstreams and just going one mile
        # at a time.
        self.optimal_path_cost = self.path_length * self.base_cost
        self.optimal_path = []

        def take_a_step(current_place, jetstream_trail, running_cost):
            # Termination clauses
            if current_place == self.path_length:
                if running_cost < self.optimal_path_cost:
                    # We've found a more efficient path! Yay us.
                    # FIXME: NOT THREAD SAFE!!!!
                    self.optimal_path_cost = running_cost
                    self.optimal_path = jetstream_trail
                return
            if running_cost >= self.optimal_path_cost:
                # This path is fail. Fail early.
                return
            optional_next_steps = self.jetstreams[current_place]
            for step in optional_next_steps:
                take_a_step(step['finish'],
                            jetstream_trail
                            if 'no_stream' in step
                            else jetstream_trail + [(current_place,
                                                     step['finish'])],
                            running_cost + step['cost'])

        # Kick off the pathfinder
        take_a_step(0, [], 0)

if __name__ == '__main__':
    import sys
    try:
        file_path = sys.argv[1]
    except IndexError:
        sys.stderr.write('Please provide the filename containing jetstream data.')
        sys.exit(1)
    js = JetStream.from_file(file_path)
    js.find_optimal_path()
    print 'Minimum energy:', js.optimal_path_cost
    print 'Jetstream steps:', str(js.optimal_path)
