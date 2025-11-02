`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 31.10.2025 15:42:04
// Design Name: 
// Module Name: TB_MicroArquitectura_RISCV
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module TB_MicroArquitectura_RISCV; 
reg clk; 
wire [31:0] ALU_Result_debug,result_debug,A3,operando_B,ImmExt_debug,PC_debug,
            SrcA_debug,read_data_debug,write_data_debug; 

MicroArquitectura_RISCV prueba(clk,ALU_Result_debug,result_debug,
                               A3,operando_B, ImmExt_debug,PC_debug,
                               SrcA_debug,read_data_debug,write_data_debug); 

initial begin
    clk = 0;
    forever #5 clk = ~clk;  // periodo de 10 ns -> frecuencia de 100 MHz 
end
endmodule 
