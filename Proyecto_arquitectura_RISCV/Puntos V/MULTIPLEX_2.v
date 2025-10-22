`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 16.10.2025 19:12:24
// Design Name: 
// Module Name: MULTIPLEX_2
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


module MULTIPLEX_2(input[31:0]entrada_A,entrada_B,input Control,output reg [31:0] salida);


always @(*) begin //Siempre que una entrada cambie 
        case (Control)
            1'b0: salida = entrada_A ;   // Suma
            1'b1: salida = entrada_B;  // Desplazamiento a la derecha
            default: salida  = 32'd0;
        endcase
end
endmodule
