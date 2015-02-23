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
        # The one-mile step options would be from the end of any range to the
        # beginning of any range that starts after
        range_ends = set([0])
        for start, list_of_stream_ends in self.jetstreams.items():
            range_ends.update([d['finish'] for d in list_of_stream_ends])
        range_starts = self.jetstreams.keys()
        for range_end in range_ends:
            for range_start in [s for s in range_starts if s > range_end]:
                self.jetstreams.setdefault(range_end, []).append(
                    {'finish': range_start,
                     'cost': self.base_cost * (range_start - range_end),
                     'no_stream': True}
                )

    def find_optimal_path(self):
        self.pad_jetstream_with_base_steps()
        # Our upper bound is ignoring all jetstreams and just going one mile
        # at a time.
        self.optimal_path_cost = self.path_length * self.base_cost
        self.optimal_path = []
        # Keep track of the lowest costs to get to a particular distance.
        # Any path which hits the exact same distance at a greater cost can't
        # be the most efficient.
        lowest_costs_at_milestone = {i: i * self.base_cost + 1 for i in range(0, self.path_length)}

        def take_a_step(current_place, jetstream_trail, running_cost):
            # Termination clauses
            if current_place == self.path_length:
                if running_cost < self.optimal_path_cost:
                    # We've found a more efficient path! Yay us.
                    # FIXME: NOT THREAD SAFE!!!!
                    self.optimal_path_cost = running_cost
                    self.optimal_path = jetstream_trail
                return []
            if running_cost >= self.optimal_path_cost:
                # This path is fail. Fail early.
                return []
            if running_cost >= lowest_costs_at_milestone[current_place]:
                # We've already found an efficient path to this distance
                return []
            optional_next_steps = self.jetstreams[current_place]
            return [(step['finish'],
                    jetstream_trail
                    if 'no_stream' in step
                    else jetstream_trail + [(current_place, step['finish'])],
                    running_cost + step['cost'])
                    for step in optional_next_steps]

        # Kick off the pathfinder
        steps = take_a_step(0, [], 0)
        while steps:
            step = steps.pop(0)
            steps += take_a_step(*step)

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
