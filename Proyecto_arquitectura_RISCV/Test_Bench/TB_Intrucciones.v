`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 30.10.2025 20:06:21
// Design Name: 
// Module Name: TB_Intrucciones
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


module TB_Intrucciones;
    reg [31:0] A; 
    wire [31:0] read; 
    
    Intrucciones prueba(A,read); 
    
initial begin
    A = 32'd148;// se inicializa la direccion del codigo 
    forever #5 A = A + 4'd4;  // periodo de 10 ns -> frecuencia de 100 MHz
 end

endmodule
