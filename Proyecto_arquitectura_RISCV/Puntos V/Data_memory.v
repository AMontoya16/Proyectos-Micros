`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 16.10.2025 20:28:07
// Design Name: 
// Module Name: Data_memory
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


module Data_memory(input clk, MemWrite, input[31:0] A,W,output [31:0]Read);
reg[31:0] Demomory[63:0]; //se crea el espacio de memori

integer i;
initial begin
   for (i = 0; i < 64; i = i + 1)
      Demomory[i] = 32'b0;
end

assign Read = Demomory[A>>2'd2]; 
always @(posedge clk) begin 
    if(MemWrite == 1'b1) begin 
        Demomory[A>>2'd2]=W; 
    end 
end 
endmodule
