`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 17.10.2025 19:41:24
// Design Name: 
// Module Name: TB_Registro_PC
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


module TB_Registro_PC;
reg clk; 
reg [31:0] entrada; 
wire [31:0] salida; 
Registro_PC prueba(clk,entrada,salida); 

initial begin
    clk = 0;
    forever #5 clk = ~clk;  // periodo de 10 ns -> frecuencia de 100 MHz 
 end
initial begin 
entrada = 32'd1; 
#10; 
entrada = 32'd10;
#10; 
entrada = 32'd15; 
end 
endmodule
