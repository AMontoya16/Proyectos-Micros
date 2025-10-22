`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 16.10.2025 19:50:37
// Design Name: 
// Module Name: TB_Registros
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


module TB_Registros; 
reg clk,RegW; 
reg [4:0]A1,A2,A3;
reg [31:0] write; 
wire [31:0] R1,R2; 

Registros pruebas (clk, RegW, A1,A2,A3,write,R1,R2); 

 initial begin
    clk = 0;
    forever #5 clk = ~clk;  // periodo de 10 ns -> frecuencia de 100 MHz
 end
initial begin 
RegW = 1'b0; 
A1 = 5'b00001; 
A2 = 5'b00010; 
A3 = 5'b00001; 
write = 32'd50; 
#10; 
RegW = 1'b1; 
#6; 
RegW = 1'b0; 
A3 = 5'b00101;
write = 32'd80;  
#15; 
RegW = 1'b1;
#18;
RegW = 1'b0; 
A1 = 5'b00001; 
A2 = 5'b00101;
end 


endmodule
