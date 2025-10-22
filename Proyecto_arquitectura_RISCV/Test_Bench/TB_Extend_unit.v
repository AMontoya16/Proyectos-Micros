`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 17.10.2025 19:14:06
// Design Name: 
// Module Name: TB_Extend_unit
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


module TB_Extend_unit;
reg [31:7] imm; 
reg [1:0] immsrc; 
wire [31:0] salida; 
Extend_unit prueba(imm, immsrc, salida); 

initial begin 
imm = 25'd90;
immsrc= 2'b00; 
#10; 
immsrc= 2'b01;
#10; 
immsrc= 2'b10; 
#10; 
immsrc= 2'b11; 
end 

endmodule
