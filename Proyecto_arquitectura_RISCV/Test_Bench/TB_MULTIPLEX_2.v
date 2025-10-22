`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 16.10.2025 19:17:33
// Design Name: 
// Module Name: TB_MULTIPLEX_2
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


module TB_MULTIPLEX_2;
    reg[31:0] A, B;
    reg control;
    wire[31:0] salida; 
MULTIPLEX_2 prueba(A,B,control,salida); 
initial begin
    A = 32'd50; 
    B = 32'd100;
    control = 1'b0;
    #10;
    control = 1'b1;
    #10; 
    A = 32'd90; 
    B = 32'd800;
    control = 1'b0;
    #10;
    control = 1'b1;
end 
endmodule
