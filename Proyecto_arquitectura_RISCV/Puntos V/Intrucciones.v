`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 30.10.2025 19:57:54
// Design Name: 
// Module Name: Intrucciones
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


module Intrucciones(
    input  [31:0] A,
    output [31:0] Read
);
// se realiza una direccion y una lectura 
    reg [31:0] Demomory[0:127];//se define el espacio en memoria
    integer i;

    initial begin
        for (i = 0; i < 128; i = i + 1)//se inicializan toda la memoria en 0
            Demomory[i] = 32'b0;
        //se entrega la direccion y la intruccion correspondiente
        Demomory[37] = 32'hfe010113;
        Demomory[38] = 32'h00112e23;
        Demomory[39] = 32'h00812c23;
        Demomory[40] = 32'h02010413;
        Demomory[41] = 32'hfea42623;
        Demomory[42] = 32'hfeb42423;
        Demomory[43] = 32'hfec42223;
        Demomory[44] = 32'hfec42703;
        Demomory[45] = 32'hfe842783;
        Demomory[46] = 32'h00f70733;
        Demomory[47] = 32'hfe442783;
        Demomory[48] = 32'h00e7a023;
        Demomory[49] = 32'hfe842783;
        Demomory[50] = 32'hfec42703;
        Demomory[51] = 32'h40f75733;
        Demomory[52] = 32'hfe442783;
        Demomory[53] = 32'h00e7a023;
        Demomory[54] = 32'hfec42703;
        Demomory[55] = 32'hfe842783;
        Demomory[56] = 32'h00f77733;
        Demomory[57] = 32'hfe442783;
        Demomory[58] = 32'h00e7a023;
        Demomory[59] = 32'hfec42703;
        Demomory[60] = 32'hfe842783;
        Demomory[61] = 32'h00f74733;
        Demomory[62] = 32'hfe442783;
        Demomory[63] = 32'h00e7a023;
        Demomory[64] = 32'h00000013;
        Demomory[65] = 32'h01c12083;
        Demomory[66] = 32'h01812403;
        Demomory[67] = 32'h02010113;
        Demomory[68] = 32'h00008067;
        Demomory[69] = 32'hfe010113;
        Demomory[70] = 32'h00112e23;
        Demomory[71] = 32'h00812c23;
        Demomory[72] = 32'h02010413;
        Demomory[73] = 32'h0000c7b7;
        Demomory[74] = 32'h7df78793;
        Demomory[75] = 32'hfef42623;
        Demomory[76] = 32'h00700793;
        Demomory[77] = 32'hfef42423;
        Demomory[78] = 32'h00a00793;
        Demomory[79] = 32'hfef42223;
        Demomory[80] = 32'hfe042023;
        Demomory[81] = 32'hfe040793;
        Demomory[82] = 32'h00078613;
        Demomory[83] = 32'hfe442583;
        Demomory[84] = 32'hfe842503;
        Demomory[85] = 32'hf41ff0ef;
        Demomory[86] = 32'h00000793;
        Demomory[87] = 32'h00078513;
        Demomory[88] = 32'h01c12083;
        Demomory[89] = 32'h01812403;
        Demomory[90] = 32'h02010113;
        Demomory[91] = 32'h00008067;
    end

    assign Read = Demomory[A >> 2];

endmodule