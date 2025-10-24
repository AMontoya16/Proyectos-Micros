`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 24.10.2025 08:29:04
// Design Name: 
// Module Name: TB_MULTIPLEX_4
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


module TB_MULTIPLEX_4;
reg [31:0]Operando_A, Operando_B,Operando_C,Operando_D; 
reg [1:0] control;
wire [31:0] salida; 
MULTIPLEX_4 prueba (Operando_A,Operando_B,Operando_C,Operando_D,control, salida); 
initial begin // se definen 4 valores de pruebas
Operando_A = 32'd150; 
Operando_B = 32'd200; 
Operando_C = 32'd250; 
Operando_D = 32'd300; 
//Se varia la señal de control con el tiempo para verificar el funcionamiento 
control = 2'b00; //Operando_A 
#10; 
control = 2'b01;//Operando_B
#10;
control = 2'b10;//Operando_C
#10; 
control = 2'b11; //Operando_D
end 
endmodule
