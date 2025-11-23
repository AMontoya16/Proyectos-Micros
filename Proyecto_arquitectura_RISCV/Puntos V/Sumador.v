`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 16.10.2025 19:04:42
// Design Name: 
// Module Name: Sumador
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


module Sumador(input[31:0]Operando_A,Operando_B,output reg [31:0] salida);
//se inicializan 2 entradas y una salida de 32 bits 
    always @(*) begin //cada vez que hay un cambio
        salida = Operando_A + Operando_B ; //se suma las dos entradas y se entrega a la salida
    end 
endmodule
