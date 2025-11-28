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
immsrc= 2'b00; //tipo I, resultado -32
imm = 25'hFE0 << 13;//se inicializan las variables 
#10;
immsrc= 2'b01;//Tipo S, resultado 28 
imm = 25'b0000000000010001001011100; 
#10; 
immsrc= 2'b10; //Tipo U, resultado 49152
imm = 25'b0000000000000000110001111; 
#10; 
immsrc= 2'b11; //Tipo J, resultado -192
imm = 25'b1111010000011111111100001; 

end 

endmodule
