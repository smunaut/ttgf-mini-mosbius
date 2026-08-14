#!/usr/bin/env python3

#
# Generate Input Control block
#
# Copyright (c) 2025 Sylvain Munaut
# SPDX-License-Identifier: Apache-2.0
#

import sys
from collections import namedtuple

from common import *


def main(argv0, op_mode, ctrl_type, ctrl_cnt):
	# Arguments
	if op_mode not in ['decap', 'magic']:
		raise RuntimeError('Invalid operation mode')

	if ctrl_type not in ['begin', 'mid', 'end', 'pass', 'first']:
		raise RuntimeError('Invalid type')

	if ctrl_cnt not in ['1', '2']:
		raise RuntimeError('Invalid count')

	ctrl_cnt = int(ctrl_cnt)

	# Base grid
	grid = Grid(72, 2)

	# Handle passthrough specially
	if ctrl_type == 'pass':
		# Taps
		grid.add_tap_col(0)
		grid.add_tap_col(36)
		grid.add_tap_col(70)

	# And also the 'first'
	elif ctrl_type == 'first':
		# Taps
		grid.add_tap_col(0)
		grid.add_tap_col(36)
		grid.add_tap_col(70)

		# Input buffer
		grid.add_cell('buf_dat', CELLS['clkbuf_4'], (56, 1), 1)

		# Delay
		grid.add_cell('dly_dat', CELLS['dlyb_2'], (38, 1), 1)

	# Normal ones
	else:
		# Taps
		grid.add_tap( 0, 0)
		grid.add_tap(20, 0)
		grid.add_tap(70, 0)
		grid.add_tap( 0, 1)
		grid.add_tap(36, 1)

		# If we're at beginning:
		if ctrl_type == 'begin':
			# Clock/Reset/Enable buffer
			grid.add_cell('buf_clk', CELLS['clkbuf_4'], (56, 0), 1)
			grid.add_cell('buf_rst', CELLS['clkbuf_4'], (42, 0), 1)
			grid.add_cell('buf_ena', CELLS['clkbuf_4'], (28, 0), 1)

		# Add the FF and AND buffers
		for i in range(ctrl_cnt):
			grid.add_cell(f'ff[{i:d}]',  CELLS['dffrnq_1'], (38-36*i, 1), 1)
			grid.add_cell(f'and[{i:d}]', CELLS['and2_2'],   (11- 9*i, 0), 1)

		# If we're at the end:
		if ctrl_type == 'end':
			grid.add_cell('dly_dat', CELLS['dlyb_2'], (22, 0), 1)

	# Fill the rest
	grid.fill()

	# Outputs
	if op_mode == 'magic':
		# Generate main output
		print('\n'.join(grid.gen_script()))

		# Create power rails
		print('\n'.join(grid.gen_rail(  1500, 800, True)))
		print('\n'.join(grid.gen_rail(  2600, 800, False)))

	elif op_mode == 'decap':
		print('\n'.join(grid.gen_decap()))

	# Pass through has no routing
	if ctrl_type == 'pass':
		return

	# Routing
	if op_mode == 'magic':
		r = Router()

		# Handle the 'first' type specially
		if ctrl_type == 'first':
			# For input just create m2 stub
			r.start('met1', (67, 1, 3))
			r.via_to('met2')
			r.move_to( (72, 1, 3) )
			r.end()

			# Buffer -> Delay
			r.start('met1', (60, 1, 3))
			r.via_to('met2')
			r.move_rel( (-5, 0, 0) )
			r.move_rel( ( 0, 0, -1) )
			r.move_rel( (-4, 0, 0) )
			r.via_to('met1')
			r.end()

			# Put delay output where it'll be expected
			r.start('met1', (40, 1, 5))
			r.via_to('met2')
			r.move_to( (-1, 1, 5) )
			r.end()

			# Generate script
			print('\n'.join(r.gen_script()))

			return

		# Input buffers for 'begin' type
		if ctrl_type == 'begin':
			# Create m3 to bus
			for x in [38,52,66]:
				r.start('met1', (x, 0, 3))
				r.via_to('met2')
				r.move_rel( (1, 0, 0) )
				r.via_to('met3')
				r.move_rel( (0, -1, 0) )
				r.end()

		# Clock connection
		if ctrl_type == 'begin':
			# Begin at the output of the buffer
			r.start('met1', (60, 0, 3))
			r.via_to('met2')
			r.move_rel( (-1, 0, 0) )
			r.via_to('met3')
			r.move_rel( (0, 1, -1) )
			r.via_to('met2')

		else:
			# Begin on met1 on previous block
			r.start('met2', (141, 1, 2))

		for i in range(ctrl_cnt):
			r.move_to( (69-i*36, 1, 2) )
			r.push()
			r.move_rel( (0, 0, 1) )
			r.move_rel( (1, 0, 0) )
			r.via_to('met1')
			r.pop()

		# Reset connection
		if ctrl_type == 'begin':
			# Begin at the output of the buffer
			r.start('met1', (46, 0, 3))
			r.via_to('met2')
			r.move_rel( (-1, 0, 0) )
			r.via_to('met3')
			r.move_rel( (0, 1, -2) )
			r.via_to('met2')

		else:
			# Begin on met1 on previous block
			r.start('met2', (116, 1, 1))

		for i in range(ctrl_cnt):
			r.move_to( (44-i*36, 1, 1) )
			r.push()
			r.via_to('met1')
			r.pop()

		# "Enable" connection
		if ctrl_type == 'begin':
			# Begin at the output of the buffer
			r.start('met1', (32, 0, 3))
			r.via_to('met2')
			r.move_rel( (-1, 0, 0) )
			r.via_to('met3')
			r.move_rel( (0, 0, 2) )
			r.via_to('met2')

		else:
			# Begin on met1 on previous block
			r.start('met2', (88, 0, 5))

		for i in range(ctrl_cnt):
			r.move_to( (16-i*9, 0, 5) )
			r.push()
			r.via_to('met1')
			r.pop()

		# FF output to AND2
		r.start('met1', (38, 1, 5))
		r.via_to('met2')
		r.move_to( (19, 1, 5) )
		r.via_to('met3')
		r.move_rel( (0, -1, -2))
		r.via_to('met2')
		r.move_rel( (-1, 0, 0))
		r.via_to('met1')
		r.end()

		if ctrl_cnt == 2:
			r.start('met1', (2, 1, 5))
			r.via_to('met2')
			r.move_to( (8, 1, 5) )
			r.via_to('met3')
			r.move_rel( (0, -1, -2))
			r.via_to('met2')
			r.move_rel( (1, 0, 0))
			r.via_to('met1')
			r.end()

		# Data input
		r.start('met1', (65, 1, 3))
		r.via_to('met2')
		r.move_rel( ( 1, 0, 0))
		r.via_to('met3')
		r.move_rel( ( 0, 0, 2) )
		r.via_to('met2')
		r.move_rel( ( 6, 0, 0) )
		r.end()

		# Data chaining ?
		if ctrl_cnt == 2:
			r.start('met1', (29, 1, 3))
			r.via_to('met2')
			r.move_rel( ( 1, 0,  0) )
			r.via_to('met3')
			r.move_rel( ( 0, 0,  2) )
			r.via_to('met2')
			r.end()

		# Data output
		if ctrl_type == 'end':
			# Start a route at the A1 input of the last AND2
			r.start('met2', (27-ctrl_cnt*9, 0, 3))

			# Bring that route to the input of delay
			r.move_rel( (0, 0, -1) )
			r.move_to( (34, 0, 2) )
			r.via_to('met1')
			r.end()

			# Then from delay output to where next block will expect it
			r.start('met1', (24, 0, 4))
			r.via_to('met2')
			r.move_to( (0, 0, 4) )
			r.via_to('met3')
			r.move_rel( (0, 1, 1) )
			r.via_to('met2')
			r.move_rel( (-1, 0, 0) )
			r.end()

		else:
			# Start a route at the output of the last FF
			r.start('met2', (74-ctrl_cnt*36, 1, 5))

			# Bring that route to where it will be expected by the next block
			r.move_to( (-1, 1, 5) )
			r.end()

		# Final Control outputs
		for i in range(ctrl_cnt):
			r.start('met1', (13-i*9, 0, 1))
			r.via_to('met2')
			r.move_to( (12-i*2, 0, 1) )
			r.via_to('met3')
			r.move_rel( (0, 2, 0) )
			r.end()

		# Generate script
		print('\n'.join(r.gen_script()))


if __name__ == '__main__':
	main(*sys.argv)

