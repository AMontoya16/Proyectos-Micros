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
reg  MemWrite,ALUSrc,RegWrite,clk; 
reg [1:0]ALUControl,ImmSrc,ResultScr,PCSrc; 
reg [31:0] intruccion; 
wire [31:0] ALU_Result_debug,result_debug,A3,operando_B,ImmExt_debug,PC_debug; 

Prueba_Sin_intrucciones prueba(MemWrite, ALUSrc, RegWrite, clk, ALUControl, ImmSrc, ResultScr, PCSrc, intruccion, ALU_Result_debug,result_debug,
                               A3,operando_B, ImmExt_debug,PC_debug); 

initial begin
    clk = 0;
    forever #5 clk = ~clk;  // periodo de 10 ns -> frecuencia de 100 MHz 
end
initial begin //Se realiza un ADDI, se busca que el registro 1 tenga un valor de 5 
intruccion = {12'd5,5'd0,3'b000,5'd1,7'b0010011}; // imm|rs1|funct3|rd|opcode
PCSrc = 2'b00; 
ALUSrc = 1'b1; 
RegWrite = 1'b1; 
ResultScr = 2'b00; 
MemWrite = 1'b0; 
ALUControl= 2'd0; 
ImmSrc = 2'd0; 
 
#6; //Otro ADDI, se busca que el registro 2 tenga valor de 7 
intruccion = {12'd8,5'd0,3'b000,5'd2,7'b0010011}; // imm|rs1|funct3|rd|opcode 

#10; //Se hace una suma de registros 1 y 2 se guarda en registro 3 
intruccion = {7'd0,5'd2,5'd1,3'd0,5'd3,7'b0110011};//funct7|rs2|rs1|funct3|rd|opcode 
PCSrc = 2'b00;
ALUSrc = 1'b0; 
RegWrite = 1'b1; 
ResultScr = 2'b00; 
MemWrite = 1'b0; 
ALUControl= 2'd0; 
ImmSrc = 2'd0;

#10;//se hace un SW, guardando la información del registro 1 en direccion 0X00; 
intruccion = {7'd0,5'd1,5'd0,3'd2,5'd0,7'b0100011};//imm|rs2|rs1|funct3|imm|opcode 
PCSrc = 2'b00;
ALUSrc = 1'b1; 
RegWrite = 1'b0; 
ResultScr = 2'b01; 
MemWrite = 1'b1; 
ALUControl= 2'd0; 
ImmSrc = 2'b01;

#10;//se hace un LW, guardando la información del registro 4; 
intruccion = {12'd0,5'd0,3'b000,5'd4,7'b0010011}; // imm|rs1|funct3|rd|opcode  
PCSrc = 2'b00;
ALUSrc = 1'b1; 
RegWrite = 1'b1; 
ResultScr = 2'b01; 
MemWrite = 1'b0; 
ALUControl= 2'd0; 
ImmSrc = 2'b00;

#10;//se hace un lui, guardando la información del registro 5; 
intruccion = {20'd1,5'd5,7'b0110111}; //imm|Rd|opcode
PCSrc = 2'b00;
ALUSrc = 1'b1; 
RegWrite = 1'b1; 
ResultScr = 2'b10; 
MemWrite = 1'b0; 
ALUControl= 2'd0; 
ImmSrc = 2'b10;

#10;//se hace un jal, pc = pc + 8 y se guarda en registro 6 los datos de posicion pasada
intruccion = {20'b00000000100000000000,5'd6,7'b1101111}; //imm|Rd|opcode
PCSrc = 2'b01;
ALUSrc = 1'b1; 
RegWrite = 1'b1; 
ResultScr = 2'b11; 
MemWrite = 1'b0; 
ALUControl= 2'd0; 
ImmSrc = 2'b11;

#10;//se hace un jalr, pc = rs2 + imm y se guarda en registro 7 los datos de posicion pasada   
intruccion = {12'd4,5'd2,3'b000,5'd7,7'b0010011}; // imm|rs1|funct3|rd|opcode 
PCSrc = 2'b10;
ALUSrc = 1'b1; 
RegWrite = 1'b1; 
ResultScr = 2'b11; 
MemWrite = 1'b0; 
ALUControl= 2'd0; 
ImmSrc = 2'b00;

#10; 
PCSrc = 2'b00;
ALUSrc = 1'b1; 
RegWrite = 1'b0; 
ResultScr = 2'b00; 
MemWrite = 1'b0; 
ALUControl= 2'd0; 
ImmSrc = 2'b00;
end 

endmodule
