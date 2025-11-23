`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 23.11.2025 11:06:20
// Design Name: 
// Module Name: TB_MicroArquitectura_RISCV1
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


module TB_MicroArquitectura_RISCV1;
reg clk, reset; 

MicroArquitectura_RISCV1 prueba(clk, reset); 

initial begin
    clk = 0;
    forever #5 clk = ~clk;  // periodo de 10 ns -> frecuencia de 100 MHz 
end
initial begin
    reset = 1'b0; 
    #545 reset = 1'b1;//una vez ejecutado todo el codigo se activa el reset
end

endmodule
