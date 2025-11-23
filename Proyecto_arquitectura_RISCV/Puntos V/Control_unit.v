module ControlUnit(//se definen todas las entradas y salidas que se utilizaran 
    input  [6:0] opcode,
    input  [6:0] funct7,
    input  [2:0] funct3,
    output reg [1:0] ResultSrc,
    output reg MemWrite,
    output reg ALUSrc,
    output reg [1:0] ImmSrc,
    output reg RegWrite,
    output reg [1:0] ALUControl,
    output reg [1:0] PCSRC
);//se define el opcode para cada operación
// se puede denotar que para las 4 funciones arimetricas logicas estas tiene el mismo opconde 
//por lo cual, para cualquier operacion que se necesite identificar se usara el opcode de la 
//ADD 
    localparam ADD   = 7'b0110011;
    localparam XOR_  = 7'b0110011;
    localparam AND_  = 7'b0110011;
    localparam SRA_  = 7'b0110011;
//se define el opcode de las otras operaciones a utilizar
    localparam ADDI  = 7'b0010011;
    localparam LW    = 7'b0000011;
    localparam SW    = 7'b0100011;
    localparam JAL   = 7'b1101111;
    localparam JALR  = 7'b1100111;
    localparam LUI   = 7'b0110111;
//se define el valor del Alu_control, segun la operación que se va a realizar  
    localparam ALU_ADD = 2'b00;
    localparam ALU_XOR = 2'b11;
    localparam ALU_AND = 2'b10;
    localparam ALU_SRA = 2'b01;
    
    reg [1:0] ALUOp;
    always @(*) begin//para cada vez que haya un cambio
    // se inicializan todas las variables. 
        ResultSrc = 2'd0;
        MemWrite  = 0;
        ALUSrc    = 0;
        ImmSrc    = 0;
        RegWrite  = 0;
        ALUOp     = 0;
        PCSRC      = 0;

        case (opcode)
            ADD: begin//caso de las arimetico logicas
                ResultSrc = 2'd0;
                MemWrite  = 0;
                ALUSrc    = 0;
                RegWrite  = 1;
                ALUOp     = 2'b10;
            end
            ADDI: begin//el caso de la ADDI
                ResultSrc = 2'd0;
                MemWrite  = 0;
                ALUSrc    = 1;
                ImmSrc    = 2'b00;
                RegWrite  = 1;
                ALUOp     = 2'b00;
            end
            LW: begin//caso del load 
                ResultSrc = 2'b01;
                MemWrite  = 0;
                ALUSrc    = 1;
                ImmSrc    = 2'b00;
                RegWrite  = 1;
                ALUOp     = 2'b00;
            end
            SW: begin//caso del store
                ResultSrc = 2'b01;
                MemWrite  = 1;
                ALUSrc    = 1;
                ImmSrc    = 2'b01;
                RegWrite  = 0;
                ALUOp     = 2'b00;
            end
            JAL: begin//caso del jal 
                ImmSrc    = 2'b11;
                RegWrite  = 1;
                PCSRC      = 2'b01;
                ResultSrc = 2'b11; 
            end
            JALR: begin//caso del jalr 
                ALUSrc    = 1;
                ImmSrc    = 2'b00;
                RegWrite  = 1;
                PCSRC      = 2'b10;
                ResultSrc = 2'b11;
            end
            LUI: begin//caso del LUI
                ALUSrc    = 1;
                ImmSrc    = 2'b10;
                RegWrite  = 1;
                ResultSrc = 2'b10;
            end
            default: begin//un caso default por si no se identifican los casos anteriores
                ResultSrc = 0;
                MemWrite  = 0;
                ALUSrc    = 0;
                ImmSrc    = 0;
                RegWrite  = 0;
                ALUOp     = 0;
                PCSRC      = 0;
            end
        endcase
    end

    always @(*) begin
        case (opcode)//se identifica el opcode de las operaciones 
            ADD: begin//en caso de ser arimetico logica 
                case ({funct7, funct3})// se busca el funct3 y 7 para identificar el tipo de
                //operacion que se tiene que realizar en la ALU
                    10'h000: ALUControl = ALU_ADD; 
                    10'h004: ALUControl = ALU_XOR;
                    10'h007: ALUControl = ALU_AND;
                    10'h105: ALUControl = ALU_SRA; //SRA en hexa: funct3: 0x5, funct7: 0x20
                    default: ALUControl = 2'b00;
                endcase
            end//en caso de ser cualquier otra operacion, se realiza una ADD 
            ADDI, LW, SW, JAL, JALR, LUI: ALUControl = ALU_ADD;
            default: ALUControl = 2'b00;//se coloca un caso default.
        endcase
    end
endmodule