`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 16.10.2025 20:28:07
// Design Name: 
// Module Name: Data_memory
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


module Data_memory(input clk, input reset, input MemWrite, input[31:0] A,W,output [31:0]Read);
//A == la direccion de memoria 
//w == la informacion que se escribe en la direccion de memoria A 
reg[31:0] Demomory[63:0]; //se crea el espacio de memori

integer i;
initial begin//se inicaliza todos los espacios en memoria con 0 
   for (i = 0; i < 64; i = i + 1)
      Demomory[i] = 32'b0;
end
//como se leen palabras y la direccion se entrega en Bytes 
//Se hace un desplazamiento de 2 a la derecha 
//para pasar de byte a palabras 
//note que la lectura es asincrona. 
assign Read = Demomory[A>>2'd2]; 

always @(posedge clk) begin 
    if (reset == 1'b1) begin  //se coloca una señal de reset 
       for (i = 0; i < 64; i = i + 1)
          Demomory[i] = 32'b0;
    end else if(MemWrite == 1'b1) begin 
    //se escribe en memoria cuando memwrite esta en 1
        Demomory[A>>2'd2]=W; 
    end 
end 
endmodule
