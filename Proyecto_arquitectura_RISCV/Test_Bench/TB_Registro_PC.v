`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 17.10.2025 19:41:24
// Design Name: 
// Module Name: TB_Registro_PC
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


module TB_Registro_PC;
reg clk,reset; 
reg [31:0] entrada; 
wire [31:0] salida; 
Registro_PC prueba(clk,reset,entrada,salida); 

initial begin
    clk = 0;
    forever #5 clk = ~clk;  // periodo de 10 ns -> frecuencia de 100 MHz 
 end
initial begin//se inicializan las variables
reset = 1'b0; 
entrada = 32'd1; //se entrega un valor y se espera 1 ciclo de reloj
#10; 
entrada = 32'd10;//se cambia el valor y es vuelve esperar 
#10; 
entrada = 32'd15;// se cambia el valor de entrada 
reset = 1'b1;  //pero se reinicia el sistema. 
end 
endmodule
