`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 17.10.2025 15:37:19
// Design Name: 
// Module Name: Extend_unit
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


module Extend_unit(input [31:7] inst, input [1:0] immsrc, output reg [31:0] salida );
always @(*)begin 
    case(immsrc) 
    //tipo I 
        2'b00: salida = {{20{inst[31]}},inst[31:20]};
    //tipo S 
        2'b01: salida = {{20{inst[31]}}, inst[31:25], inst[11:7]};
    //tipo U
        2'b10: salida = {inst[31:12], 12'b0};
    //tipo j 
        2'b11: salida = {{12{inst[31]}}, inst[19:12], inst[20], inst[30:21], 1'b0};
        default: salida = 32'd0; 
    endcase 
end 

endmodule
