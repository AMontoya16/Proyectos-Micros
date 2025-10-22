`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 17.10.2025 19:35:57
// Design Name: 
// Module Name: Registro_PC
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


module Registro_PC(input clk, input[31:0] D, output reg [31:0] Q);

initial begin
    Q = 32'd0; 
end

always @(posedge clk)begin 
    Q <= D; 
end 

endmodule
