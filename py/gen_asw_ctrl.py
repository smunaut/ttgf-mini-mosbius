#!/usr/bin/env python3

#
# Generate ASW Column Control block
#
# Copyright (c) 2025 Sylvain Munaut
# SPDX-License-Identifier: Apache-2.0
#

import sys
from collections import namedtuple

from common import *


# Operation mode
if len(sys.argv) != 2:
	raise RuntimeError('Need operation mode argument')

OP_MODE = sys.argv[1]

if OP_MODE not in ['decap', 'magic']:
	raise RuntimeError('Invalid operation mode')

# Base grid
grid = Grid(72, 6)

# Taps
grid.add_tap_col(20)
grid.add_tap_col(56)

# Clock/Reset/Enable buffer
grid.add_cell('buf_clk', CELLS['clkbuf_4'],        (6, 5), 0)
grid.add_cell('buf_rst', CELLS['clkbuf_4'],        (6, 4), 0)
grid.add_cell('buf_ena', CELLS['clkbuf_4'],        (6, 3), 0)

# Input data delay
grid.add_cell('dly_dat', CELLS['dlyb_2'], (2, 0), 0)

# FFs + ANDs
for i in range(6):
	grid.add_cell(f'ff[{i:d}]', CELLS['dffrnq_1'], (22, i), 0)
	grid.add_cell(f'and[{i:d}]', CELLS['and2_2'], (58, i), 0)

# Fill the rest
grid.fill()

# Outputs
if OP_MODE == 'magic':
	# Generate main output
	print('\n'.join(grid.gen_script()))

	# Create power rails
	print('\n'.join(grid.gen_rail(  1500, 800, True)))
	print('\n'.join(grid.gen_rail(  2600, 800, False)))

elif OP_MODE == 'decap':
	print('\n'.join(grid.gen_decap()))


# Routing
if OP_MODE == 'magic':
	r = Router()

	# Clock input
	r.start('met1', (7, 5, 3))
	r.via_to('met2')
	r.move_rel( (1, 0, 0) )
	r.via_to('met3')
	r.move_rel( ( 0, 1, 0) )
	r.end()

	# Clock distribution
	r.start('met1', (15, 5, 3))
	r.via_to('met2')
	r.move_to( (22, 5, 3) )
	r.via_to('met3')

	for i in range(6):
		r.move_to( (22, 5-i, 3) )
		r.push()
		r.via_to('met2')
		r.move_to( (23, 5-i, 3) )
		r.via_to('met1')
		r.pop()

	r.end()

	# Reset input
	r.start('met1', (7, 4, 3))
	r.via_to('met2')
	r.move_rel( (2, 0, 0) )
	r.via_to('met3')
	r.move_rel( ( 0, 2, 0) )
	r.end()

	# Reset distribution
	r.start('met1', (15, 4, 3))
	r.via_to('met2')
	r.move_rel( (0, 0, -1) )
	r.move_to( (47, 4, 2) )
	r.via_to('met3')

	for i in range(6):
		r.move_to( (47, 5-i, 2) )
		r.push()
		r.via_to('met2')
		r.move_to( (48, 5-i, 2) )
		r.via_to('met1')
		r.pop()

	# Enable input
	r.start('met1', (7, 3, 3))
	r.via_to('met2')
	r.move_rel( (3, 0, 0) )
	r.via_to('met3')
	r.move_rel( ( 0, 3, 0) )
	r.end()

	# Enable distribution
	r.start('met1', (15, 3, 3))
	r.via_to('met2')
	r.move_rel( (0, 0, -2) )
	r.move_to( (62, 3, 1) )
	r.via_to('met3')

	for i in range(6):
		r.move_to( (62, 5-i, 3) )
		r.push()
		r.via_to('met2')
		r.move_to( (61, 5-i, 3) )
		r.via_to('met1')
		r.pop()

	r.end()

	# Wire FF out to AND input
	for i in range(6):
		r.start('met1', (55, 5-i, 3))
		r.via_to('met2')
		r.move_rel( (4, 0, 0) )
		r.via_to('met1')
		r.end()

	# Input to delay for chaining
	r.start('met1', (5, 0, 2))
	r.via_to('met2')
	r.move_rel( (-6, 0, 0) )
	r.end()

	# Delay to first FF
	r.start('met1', (18 , 0, 2))
	r.via_to('met2')
	r.move_rel( (9, 0, 0) )
	r.move_rel( (0, 0, 1) )
	r.move_rel( (1, 0, 0) )
	r.via_to('met1')
	r.end()

	# For the first 5 FF, wire output to input of next
	for i in range(5):
		r.start('met2', (55, i, 3))
		r.move_rel( (-25+2*i, 0, 0) )
		r.via_to('met3')
		r.move_rel( (0, 1, 0) )
		r.via_to('met2')
		r.move_to( (28, i+1, 3) )
		r.via_to('met1')
		r.end()

	# Wire last FF output to edge for chaining
	r.start('met2', (55, 5, 3) )
	r.via_to('met3')
	r.move_rel( (0, -5, -1) )
	r.via_to('met2')
	r.move_rel( (17, 0, 0) )
	r.end()

	# Control outputs
	for i in range(6):
		r.start('met1', (64, i, 5) )
		r.via_to('met2')
		r.move_to( (16-i, i, 5) )
		r.via_to('met3')
		r.move_to( (16-i, 0, 0) )
		r.via_to('met4')
		r.move_to( (16-i, -1, 0) )
		r.end()


	print('\n'.join(r.gen_script()))
