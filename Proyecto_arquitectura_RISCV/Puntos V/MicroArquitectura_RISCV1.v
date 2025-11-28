`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 23.11.2025 10:46:19
// Design Name: 
// Module Name: MicroArquitectura_RISCV1
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


module MicroArquitectura_RISCV1(input clk, input reset);
//Se utilizan distintos cables para el datapath
wire[31:0]SrcA, SrcB,write_data,ImmExt,PC,PC_plus_four,PC_target,PC_Next
          ,Next_PC,ALU_Result,read_data,result,instruccion; 
          
// se inicializan los cables de la unidad de control. 
wire MemWrite,ALUSrc,RegWrite; 
wire [1:0] ALUControl,ImmSrc,ResultScr,PCSrc;       

// se define la unidad de control:
// se entregan el opcode, el funct3 y funt7 y se generan todas las señales de control
ControlUnit control (instruccion[6:0], instruccion[31:25],instruccion[14:12],
                     ResultScr, MemWrite, ALUSrc, ImmSrc, RegWrite, 
                     ALUControl, PCSrc); 
//Se colocan los registros
Registros Register_File(clk, reset,RegWrite, instruccion[19:15],instruccion[24:20],instruccion[11:7],result,
                        SrcA,write_data); 
//Mux para seleccionar operando B de la ALU
MULTIPLEX_2 ALU_Select(write_data,ImmExt,ALUSrc,SrcB); 
//ALU rediseñada para solo 4 operaciones
ALU ALU_MOD(SrcA,SrcB,ALUControl,ALU_Result); 
//Se inicializar la memoria
Data_memory memoria(clk,reset,MemWrite, ALU_Result,write_data, read_data); 
//Mux para seleccionar los resultados de la ALU o la salida de memoria 
MULTIPLEX_4 Result_select(ALU_Result,read_data,ImmExt,PC_plus_four,ResultScr,result);
//Mux para seleccionar el PC+4 o el nuevo PC 
MULTIPLEX_4 PC_select(PC_plus_four,PC_target,{ALU_Result[31:1], 1'b0},32'd0,PCSrc,PC_Next);
//Registro que guarda el estado actual de PC hasta el proximo ciclo de reloj 
Registro_PC PC_register(clk,reset,PC_Next,PC); 
//Unidad de extensión, recibe los imediatos de la intrucción y segun la operación los extiende 
Extend_unit Extensor (instruccion[31:7],ImmSrc,ImmExt); 
//Sumador que suma 4 al PC 
Sumador Sum_PC_Four (PC, 32'd4, PC_plus_four); 
//Sumador que suma PC mas el imediato. 
Sumador Sum_B (PC, ImmExt,PC_target);
//Se coloca la memoria de instrucciones.  
Instrucciones inst_R (PC,instruccion);
endmodule
