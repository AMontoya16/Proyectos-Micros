`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 16.10.2025 08:08:23
// Design Name: 
// Module Name: ALU
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


module ALU(input[31:0]Operando_A,Operando_B,input[1:0]Control,output reg [31:0] salida);

    always @(*) begin //Siempre que una entrada cambie 
        case (Control)
            2'b00: salida = Operando_A  + Operando_B ;   // Suma
            2'b01: salida = Operando_A  >>> Operando_B ;  // Desplazamiento a la derecha
            2'b10: salida = Operando_A  & Operando_B ;   // AND
            2'b11: salida  = Operando_A  ^ Operando_B ;   // XOR
            default: salida  = 32'b0;
        endcase
    end
endmodule
