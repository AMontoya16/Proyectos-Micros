`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 17.10.2025 15:07:11
// Design Name: 
// Module Name: TB_Data_memory
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


module TB_Data_memory;
reg clk,MemW; 
reg [31:0]A1;
reg [31:0] write; 
wire [31:0] R1; 
Data_memory prueba(clk, MemW,A1,write,R1); 

initial begin
    clk = 0;
    forever #5 clk = ~clk;  // periodo de 10 ns -> frecuencia de 100 MHz
 end
 
initial begin 
    MemW= 1'b0; 
    A1 = 32'd0; 
    write = 32'd50; 
    #10; 
    MemW = 1'b1;  
    #15; 
    MemW = 1'b0; 
    A1 = 32'd4;
    write = 32'd80;  
    #15; 
    MemW  = 1'b1;
    #18;
    MemW  = 1'b0; 
    A1 = 32'd0;
    #18; 
    A1 = 32'd4;  
end 
endmodule
