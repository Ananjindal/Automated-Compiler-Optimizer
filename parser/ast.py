from dataclasses import dataclass


class ASTNode:
    pass


# ==========================================
# EXPRESSIONS
# ==========================================

@dataclass
class Number(ASTNode):
    value: int


@dataclass
class Variable(ASTNode):
    name: str


@dataclass
class BinaryOperation(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode


@dataclass
class Comparison(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode


# ==========================================
# BASIC STATEMENTS
# ==========================================

@dataclass
class Assignment(ASTNode):
    variable: str
    expression: ASTNode


@dataclass
class PrintStatement(ASTNode):
    expression: ASTNode


@dataclass
class ReadStatement(ASTNode):
    variable: str


# ==========================================
# CONDITIONAL STATEMENTS
# ==========================================

@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_body: list
    else_body: list


# ==========================================
# LOOPS
# ==========================================

@dataclass
class WhileStatement(ASTNode):
    condition: ASTNode
    body: list


@dataclass
class ForStatement(ASTNode):
    initialization: ASTNode
    condition: ASTNode
    update: ASTNode
    body: list


# ==========================================
# PROGRAM
# ==========================================

@dataclass
class Program(ASTNode):
    statements: list