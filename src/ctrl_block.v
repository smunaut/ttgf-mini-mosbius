/*
 * Copyright (c) 2025 Sylvain Munaut
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module ctrl_block #(
	parameter integer DELAY_PRE  = 1,
	parameter integer DELAY_POST = 0,
	parameter integer N = 6
)(
	input  wire         VGND,
	input  wire         VDPWR,
	input  wire         clk,
	input  wire         rst_n,
	input  wire         enable,
	input  wire         data_in,
	output wire         data_out,
	output wire [N-1:0] ctrl_out,
);

	// Signals
	// -------

	wire l_clk;
	wire l_rst_n;
	wire l_enable;

	wire [N:0] shift;


	// Input buffers
	// -------------

	// Optional input delay
	generate

		if (DELAY_PRE)
		begin
			gf180mcu_fd_sc_mcu7t5v0__dlyb_2 in_dly (
				.I    (data_in),
				.Z    (shift[0]),
				.VDD  (VDPWR),
				.VSS  (VGND),
				.VNW  (VDPWR),
				.VPW  (VGND)
			);
		end
		else
		begin
			assign shift[0] = data_in;
		end

	endgenerate

	// Local buffer for clk / rst_n / enable
	gf180mcu_fd_sc_mcu7t5v0__clkbuf_4 buf_I[2:0] (
		.I    ({   clk,   rst_n,   enable }),
		.Z    ({ l_clk, l_rst_n, l_enable }),
		.VDD  (VDPWR),
		.VSS  (VGND),
		.VNW  (VDPWR),
		.VPW  (VGND)
	);


	// Shift register
	// --------------

	gf180mcu_fd_sc_mcu7t5v0__dffrnq_1 ff_I[N-1:0] (
		.CLK  (l_clk),
		.D    (shift[N-1:0]),
		.RN   (l_rst_n),
		.Q    (shift[N:1]),
		.VDD  (VDPWR),
		.VSS  (VGND),
		.VNW  (VDPWR),
		.VPW  (VGND)
	);

	gf180mcu_fd_sc_mcu7t5v0__and2_2 mask_I[N-1:0] (
		.A1   (shift[N:1]),
		.A2   (l_enable),
		.Z    (ctrl_out),
		.VDD  (VDPWR),
		.VSS  (VGND),
		.VNW  (VDPWR),
		.VPW  (VGND)
	);


	// Output
	// ------

	generate

		if (DELAY_POST)
		begin
			gf180mcu_fd_sc_mcu7t5v0__dlyb_2 out_dly (
				.I    (shift[N]),
				.Z    (data_out),
				.VDD  (VDPWR),
				.VSS  (VGND),
				.VNW  (VDPWR),
				.VPW  (VGND)
			);
		end
		else
		begin
			assign data_out = shift[N];
		end

	endgenerate

endmodule /* ctrl_block */
