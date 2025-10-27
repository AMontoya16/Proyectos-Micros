`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 27.10.2025 14:48:28
// Design Name: 
// Module Name: Control_unit_TB
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

module tb_ControlUnit;
    reg  [6:0] opcode;
    reg  [6:0] funct7;
    reg  [2:0] funct3;
    wire ResultSrc;
    wire MemWrite;
    wire ALUSrc;
    wire [1:0] ImmSrc;
    wire RegWrite;
    wire [1:0] ALUControl;
    wire [1:0] PCSRC;

    ControlUnit uut (
        .opcode(opcode),
        .funct7(funct7),
        .funct3(funct3),
        .ResultSrc(ResultSrc),
        .MemWrite(MemWrite),
        .ALUSrc(ALUSrc),
        .ImmSrc(ImmSrc),
        .RegWrite(RegWrite),
        .ALUControl(ALUControl),
        .PCSRC(PCSRC)
    );

    initial begin
        $display("Time | Opcode    | Funct7  | Funct3 | ALUControl | ALUSrc | MemWrite | RegWrite | ResultSrc | ImmSrc | PCSRC");
        $display("----------------------------------------------------------------------------------------------------------");

        opcode = 7'b0110011; funct7 = 7'b0000000; funct3 = 3'b000; #10; // ADD
        $display("%4t | ADD   | %b | %b | %b | %b | %b | %b | %b | %b | %b", $time, funct7, funct3, ALUControl, ALUSrc, MemWrite, RegWrite, ResultSrc, ImmSrc, PCSRC);

        opcode = 7'b0110011; funct7 = 7'b0000000; funct3 = 3'b100; #10; // XOR
        $display("%4t | XOR   | %b | %b | %b | %b | %b | %b | %b | %b | %b", $time, funct7, funct3, ALUControl, ALUSrc, MemWrite, RegWrite, ResultSrc, ImmSrc, PCSRC);

        opcode = 7'b0110011; funct7 = 7'b0000000; funct3 = 3'b111; #10; // AND
        $display("%4t | AND   | %b | %b | %b | %b | %b | %b | %b | %b | %b", $time, funct7, funct3, ALUControl, ALUSrc, MemWrite, RegWrite, ResultSrc, ImmSrc, PCSRC);

        opcode = 7'b0110011; funct7 = 7'b0100000; funct3 = 3'b101; #10; // SRA
        $display("%4t | SRA   | %b | %b | %b | %b | %b | %b | %b | %b | %b", $time, funct7, funct3, ALUControl, ALUSrc, MemWrite, RegWrite, ResultSrc, ImmSrc, PCSRC);

        opcode = 7'b0010011; funct7 = 7'b0000000; funct3 = 3'b000; #10; // ADDI
        $display("%4t | ADDI  | %b | %b | %b | %b | %b | %b | %b | %b | %b", $time, funct7, funct3, ALUControl, ALUSrc, MemWrite, RegWrite, ResultSrc, ImmSrc, PCSRC);

        opcode = 7'b0000011; funct7 = 7'b0000000; funct3 = 3'b010; #10; // LW
        $display("%4t | LW    | %b | %b | %b | %b | %b | %b | %b | %b | %b", $time, funct7, funct3, ALUControl, ALUSrc, MemWrite, RegWrite, ResultSrc, ImmSrc, PCSRC);

        opcode = 7'b0100011; funct7 = 7'b0000000; funct3 = 3'b010; #10; // SW
        $display("%4t | SW    | %b | %b | %b | %b | %b | %b | %b | %b | %b", $time, funct7, funct3, ALUControl, ALUSrc, MemWrite, RegWrite, ResultSrc, ImmSrc, PCSRC);

        opcode = 7'b1101111; funct7 = 7'b0000000; funct3 = 3'b000; #10; // JAL
        $display("%4t | JAL   | %b | %b | %b | %b | %b | %b | %b | %b | %b", $time, funct7, funct3, ALUControl, ALUSrc, MemWrite, RegWrite, ResultSrc, ImmSrc, PCSRC);

        opcode = 7'b1100111; funct7 = 7'b0000000; funct3 = 3'b000; #10; // JALR
        $display("%4t | JALR  | %b | %b | %b | %b | %b | %b | %b | %b | %b", $time, funct7, funct3, ALUControl, ALUSrc, MemWrite, RegWrite, ResultSrc, ImmSrc, PCSRC);

        opcode = 7'b0110111; funct7 = 7'b0000000; funct3 = 3'b000; #10; // LUI
        $display("%4t | LUI   | %b | %b | %b | %b | %b | %b | %b | %b | %b", $time, funct7, funct3, ALUControl, ALUSrc, MemWrite, RegWrite, ResultSrc, ImmSrc, PCSRC);

        $finish;
    end
endmodule