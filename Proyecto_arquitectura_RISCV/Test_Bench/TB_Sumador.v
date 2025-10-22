`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 16.10.2025 19:07:52
// Design Name: 
// Module Name: TB_Sumador
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


module TB_Sumador;
    reg[31:0] A, B;
    wire[31:0] salida; 
Sumador prueba (A,B,salida); 
initial begin 
    A = 32'd50; 
    B = 32'd100;
    #10;
    A = 32'd200; 
    B = 32'd1;
    #10;
    A = 32'd1001; 
    B = 32'd5;
end 
endmodule
