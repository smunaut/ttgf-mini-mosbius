set layout [readnet spice $project.lvs.spice]
set schem  [readnet verilog /dev/null]
readnet spice $::env(PDK_ROOT)/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/spice/gf180mcu_fd_sc_mcu7t5v0.spice $schem
readnet spice   ../xschem/simulation/mosbius.spice $schem
readnet verilog ../src/ctrl_top.synth.v            $schem
readnet verilog ../src/project.v                   $schem
::netgen::format 60
lvs "$layout $project" "$schem $project" $::env(PDK_ROOT)/$::env(PDK)/libs.tech/netgen/$::env(PDK)_setup.tcl lvs.report -blackbox
