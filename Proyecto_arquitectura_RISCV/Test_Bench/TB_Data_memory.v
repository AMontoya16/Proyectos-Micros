`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 17.10.2025 15:07:11
// Design Name: 
// Module Name: TB_Data_memory
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


module TB_Data_memory;
reg clk,reset,MemW; 
reg [31:0]A1;
reg [31:0] write; 
wire [31:0] R1; 
Data_memory prueba(clk,reset ,MemW,A1,write,R1); 

initial begin
    clk = 0;
    forever #5 clk = ~clk;  // periodo de 10 ns -> frecuencia de 100 MHz
 end
 
initial begin 
    MemW= 1'b0; //se inicializan todas las variables 
    A1 = 32'd0;
    reset = 1'b0; 
    write = 32'd50; 
    #10; 
    MemW = 1'b1;  // se escribe en memoria
    #15; 
    MemW = 1'b0; //se desactiva la escritura
    A1 = 32'd4;//se cambia la direccion
    write = 32'd80;  //se coloca otro valor de escritura 
    #15; 
    MemW  = 1'b1;// se escribe 
    #18;
    MemW  = 1'b0;//se desactiva  
    A1 = 32'd0;// se coloca otra direccion 
    #18; 
    A1 = 32'd8;// se coloca otra direccion 
    write = 32'd80; //se coloca otro valor de escritura 
    MemW  = 1'b1;//se escribe 
    #18; 
    MemW  = 1'b0;//se desactova la escritura 
    reset = 1'b1; //se reinicia la memoria
end 
endmodule
