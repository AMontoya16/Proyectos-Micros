`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 16.10.2025 19:35:53
// Design Name: 
// Module Name: Registros
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


module Registros(input clk, RegWrite, input[4:0] A1,A2,A3, input[31:0] write, output [31:0] R1,R2);
//todas las A se refiere direcciones (ejemplo dirección 1 = A1) 
//Todo las R se refiere a leido (ejemplo leido direccion 1 = R1) 
reg [31:0] Register [31:0]; //se crea 32 registros de 32 bits. 

integer i;//Se le entrega un valor inicial a los registros de 0
initial begin
    for (i = 0; i < 32; i = i + 1)
        Register[i] = 32'b0;
end

always @(posedge clk) begin 
    if(RegWrite == 1'b1) begin 
        Register[A3] <= write; 
    end 
end 

assign R1 = Register[A1];//Se asigna a cada salida de lectura la dirección de los registros
assign R2 = Register[A2];

endmodule
