`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 16.10.2025 08:24:41
// Design Name: 
// Module Name: TB_ALU
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


module TB_ALU; 
    reg[31:0] A, B;
    reg [1:0] control;
    wire[31:0] salida; 
ALU prueba(A,B,control,salida); 
initial begin 
    A = 32'd50; 
    B = 32'd100;
    control = 2'b00; //suma 
    #10;
    A = 32'd1; 
    B = 32'd3;
    control = 2'b01;//dezplazamiento arimetico
    #10;
    A = 32'd11; 
    B = 32'd5;
    control = 2'b10;//and 
    #10;
    A = 32'd10; 
    B = 32'd5;
    control = 2'b11;//dezplazamiento arimetico
end 
endmodule
