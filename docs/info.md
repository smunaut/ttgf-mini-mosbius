## How it works

The original [MOSbius project](https://mosbius.org/) by Peter Kinget et al. is
a custom chip with basic MOS devices and building blocks interconnected by
a reconfigurable array of analog switches to be able to build circuits and
experiment with analog circuit design.

Matthew Venn commissioned an adaptation of the concept to fit on Tiny Tapeout
SKY130 shuttles and a proposal by Andrew Kang was accepted. See the
[attached document](./Mini_Mosbius_Proposal_Kang_Andrew_v2.pdf).

Andrew completed the schematic design along with simulation end of August 2025
but before he started the layout, I decided to use this as a base to build my
own variant also targetting SKY130.

I left the design of the analog part pretty much unchanged, only made minor
adaptations. Some of those were guided by layout constraints, some other in an
attempt to make more circuits possible. I did rewrite most of the digital control
logic. And of course the layout is entirely mine.

Later when Tiny Tapeout gained analog support for GF180mcu shuttles, Tiny Tapeout
sponsored me to port my variant to the GF180mcu shutles. This is the result of
that work.


## How to test

A configuration bitstream needs to be loaded serially to control all the analog
switches on-board. The software suite to generate this is yet to be written.


## External hardware

Depends on what circuit you want to build and how you want to test it ...
