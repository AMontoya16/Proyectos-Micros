`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 20.10.2025 15:57:41
// Design Name: 
// Module Name: Prueba_Sin_intrucciones
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


module Prueba_Sin_intrucciones(input MemWrite,ALUSrc,RegWrite,clk,
                               input[1:0]ALUControl,ImmSrc,ResultScr,PCSrc,
                               input [31:0] intruccion,
                               output [31:0] ALU_Result_debug,result_debug,A3,operando_B,
                               ImmExt_debug,PC_debug);

wire[31:0]SrcA, SrcB,write_data,ImmExt,PC,PC_plus_four,PC_target,PC_Next
          ,Next_PC,ALU_Result,read_data,result; 
//Se colocan los registros
Registros Register_File(clk, RegWrite, intruccion[19:15],intruccion[24:20],intruccion[11:7],result,
                        SrcA,write_data); 
//Mux para seleccionar operando B de la ALU
MULTIPLEX_2 ALU_Select(write_data,ImmExt,ALUSrc,SrcB); 
//ALU rediseñada para solo 4 operaciones
ALU ALU_MOD(SrcA,SrcB,ALUControl,ALU_Result); 
//Se inicializar la memoria
Data_memory memoria(clk, MemWrite, ALU_Result,write_data, read_data); 
//Mux para seleccionar los resultados de la ALU o la salida de memoria 
MULTIPLEX_4 Result_select(ALU_Result,read_data,ImmExt,PC_plus_four,ResultScr,result);
//Mux para seleccionar el PC+4 o el nuevo PC 
MULTIPLEX_4 PC_select(PC_plus_four,PC_target,{ALU_Result[31:1], 1'b0},32'd0,PCSrc,PC_Next);
//Registro que guarda el estado actual de PC hasta el proximo ciclo de reloj 
Registro_PC PC_register(clk,PC_Next,PC); 
//Unidad de extensión, recibe los imediatos de la intrucción y segun la operación los extiende 
Extend_unit Extensor (intruccion[31:7],ImmSrc,ImmExt); 
//Sumador que suma 4 al PC 
Sumador Sum_PC_Four (PC, 32'd4, PC_plus_four); 
//Sumador que suma PC mas el imediato. 
Sumador Sum_B (PC, ImmExt,PC_target); 

assign ALU_Result_debug = ALU_Result;
assign result_debug     = result;
assign A3               = intruccion[11:7];
assign operando_B       = SrcB; 
assign ImmExt_debug     = ImmExt;
assign PC_debug         = PC; 

endmodule
