`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 20.10.2025 19:25:31
// Design Name: 
// Module Name: TB_Prueba_Sin_instrucciones
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


module TB_Prueba_Sin_instrucciones;
reg PCSrc,ResultScr,MemWrite,ALUSrc,RegWrite,clk; 
reg[1:0]ALUControl,ImmSrc;
reg [31:0] intruccion;
wire [31:0] ALU_Result_debug,result_debug,A3,operando_B,ImmExt_debug;

Prueba_Sin_intrucciones prueba(PCSrc,ResultScr,MemWrite, ALUSrc, RegWrite,clk,
ALUControl, ImmSrc, intruccion,ALU_Result_debug,result_debug,A3,operando_B,ImmExt_debug); 

initial begin
    clk = 0;
    forever #5 clk = ~clk;  // periodo de 10 ns -> frecuencia de 100 MHz 
end
initial begin //Se realiza un ADDI, se busca que el registro 1 tenga un valor de 5 
intruccion = 32'b00000000010100000000000010010011; 
PCSrc = 1'b0; 
ALUSrc = 1'b1; 
RegWrite = 1'b1; 
ResultScr = 1'b0; 
MemWrite = 1'b0; 
ALUControl= 2'd0; 
ImmSrc = 2'd0;  
#6; //Otro ADDI, se busca que el registro 2 tenga valor de 7 
intruccion = 32'b00000000011100000000000100010011; 
#10; //Se hace una suma de registros 1 y 2 se guarda en registro 3 
intruccion = 32'b00000000001000001000000110110011; 
PCSrc = 1'b0;
ALUSrc = 1'b0; 
RegWrite = 1'b1; 
ResultScr = 1'b0; 
MemWrite = 1'b0; 
ALUControl= 2'd0; 
ImmSrc = 2'd0;
#10;//se hace un SW, guardando la información del registro 1 en direccion 0X00; 
intruccion = 32'b00000000000100000000000000100011; 
PCSrc = 1'b0;
ALUSrc = 1'b1; 
RegWrite = 1'b0; 
ResultScr = 1'b1; 
MemWrite = 1'b1; 
ALUControl= 2'd0; 
ImmSrc = 2'b01;
#10;//se hace un LW, guardando la información del registro 4; 
intruccion = 32'b00000000000000000000001000000011; 
PCSrc = 1'b0;
ALUSrc = 1'b1; 
RegWrite = 1'b1; 
ResultScr = 1'b1; 
MemWrite = 1'b0; 
ALUControl= 2'd0; 
ImmSrc = 2'b00;
#10; 
intruccion = 32'b00000000010000001000000110110011; 
PCSrc = 1'b0;
ALUSrc = 1'b0; 
RegWrite = 1'b1; 
ResultScr = 1'b0; 
MemWrite = 1'b0; 
ALUControl= 2'd0; 
ImmSrc = 2'd0;


end 

endmodule
