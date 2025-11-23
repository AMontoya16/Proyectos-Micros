`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 24.10.2025 08:21:03
// Design Name: 
// Module Name: MULTIPLEX_4
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


module MULTIPLEX_4(input[31:0]Operando_A, Operando_B,Operando_C,Operando_D,
                   input [1:0] control,
                   output reg [31:0] salida);
// se tienen 4 señales de entrada de 32 bits                    
// una señal de control de 2 bits
// se define para cuando cualquier señal cambie             
always @(*) begin 
    case (control) //se crean los casos segun el valor de la señal de control
    // al ser un multiplex de 4, cada combinacion de la señal de control representa 
    // una salida relacionada con su debida entrada 
        2'b00: salida = Operando_A; 
        2'b01: salida = Operando_B; 
        2'b10: salida = Operando_C; 
        2'b11: salida = Operando_D; 
        default: salida = 32'd0; // se define un caso default 
    endcase 
end 
endmodule
