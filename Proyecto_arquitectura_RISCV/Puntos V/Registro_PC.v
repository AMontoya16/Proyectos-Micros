`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 17.10.2025 19:35:57
// Design Name: 
// Module Name: Registro_PC
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


module Registro_PC(input clk,input reset, input[31:0] D, output reg [31:0] Q);



initial begin
    Q = 32'h114; // se inicializa con este valor con el objetivo de que 
                 // se comeince en la line 114 del codigo suministrado
end

   always @(posedge clk)
      if (reset) begin
         Q <= 32'd0;// se tiene un reset
      end else begin
         Q <= D;// cdada vez que hay un clk la entrada pasa a la salida 
      end

endmodule
