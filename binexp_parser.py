#!/usr/bin/python3
import os
from os.path import join as osjoin

##Anthony ThanG
## HELLLOOOO
## Hi Dr.Beard :D :D :D


import unittest

from enum import Enum

# Use these to distinguish node types, note that you might want to further
# distinguish between the addition and multiplication operators
NodeType = Enum('BinOpNodeType', ['number', 'operator'])

class BinOpAst():
    """
    A somewhat quick and dirty structure to represent a binary operator AST.

    Reads input as a list of tokens in prefix notation, converts into internal representation,
    then can convert to prefix, postfix, or infix string output.
    """
    def __init__(self, prefix_list):
        """
        Initialize a binary operator AST from a given list in prefix notation.
        Destroys the list that is passed in.
        """
        self.val = prefix_list.pop(0)
        if self.val.isnumeric():
            self.type = NodeType.number
            self.left = False
            self.right = False
        else:
            self.type = NodeType.operator
            self.left = BinOpAst(prefix_list)
            self.right = BinOpAst(prefix_list)

    def __str__(self, indent=0):
        """
        Convert the binary tree printable string where indentation level indicates
        parent/child relationships
        """
        ilvl = '  '*indent
        left = '\n  ' + ilvl + self.left.__str__(indent+1) if self.left else ''
        right = '\n  ' + ilvl + self.right.__str__(indent+1) if self.right else ''
        return f"{ilvl}{self.val}{left}{right}"

    def __repr__(self):
        """Generate the repr from the string"""
        return str(self)

    def prefix_str(self):
        """
        Convert the BinOpAst to a prefix notation string.
        """
        if self.type == NodeType.number:
            return self.val
        return f"{self.val} {self.left.prefix_str()} {self.right.prefix_str()}"

    def infix_str(self):
        """
        Convert the BinOpAst to an infix notation string.
        """
        if self.type == NodeType.number:
            return self.val
        return f"({self.left.infix_str()} {self.val} {self.right.infix_str()})"


    def postfix_str(self):
        """
        Convert the BinOpAst to a postfix notation string.
        """
        if self.type == NodeType.number:
            return self.val
        return f"{self.left.postfix_str()} {self.right.postfix_str()} {self.val}"


    def additive_identity(self):
        """
        Reduce additive identities
        x + 0 = x
        """
        # Check if node is an operator
        if self.type == NodeType.operator:
            # If it is, apply identity
            if self.left:
                self.left.additive_identity()
            if self.right:
                self.right.additive_identity()

        # Check if node is addition operator
        if self.val == '+':
            # if left child is 0, replace node with other child
            if self.left.type == NodeType.number and self.left.val == '0':
                self.val = self.right.val
                self.type = self.right.type
                self.left = self.right.left
                self.right = self.right.right

            # if right child is 0, replace node with other child
            elif self.right.type == NodeType.number and self.right.val == '0':
                self.val = self.left.val
                self.type = self.left.type
                self.left = self.left.left
                self.right = self.left.right

    def multiplicative_identity(self):
        """
        Reduce multiplicative identities
        x * 1 = x
        """
        if self.type == NodeType.operator:
            if self.left:
                self.left.multiplicative_identity()
            if self.right:
                self.right.multiplicative_identity()

        if self.val == '*':
            if self.left.type == NodeType.number and self.left.val == '1':
                self.val = self.right.val
                self.type = self.right.type
                self.left = self.right.left
                self.right = self.right.right
            elif self.right.type == NodeType.number and self.right.val == '1':
                self.val = self.left.val
                self.type = self.left.type
                self.left = self.left.left
                self.right = self.left.right

    def mult_by_zero(self):
        """
        Reduce multiplication by zero
        x * 0 = 0
        """
        # Optionally, IMPLEMENT ME! (I'm pretty easy)
        pass

    def constant_fold(self):
        """
        Fold constants,
        e.g. 1 + 2 = 3
        e.g. x + 2 = x + 2
        """
        # Optionally, IMPLEMENT ME! This is a bit more challenging.
        # You also likely want to add an additional node type to your AST
        # to represent identifiers.
        pass

    def simplify_binops(self):
        """
        Simplify binary trees with the following:
        1) Additive identity, e.g. x + 0 = x
        2) Multiplicative identity, e.g. x * 1 = x
        3) Extra #1: Multiplication by 0, e.g. x * 0 = 0
        4) Extra #2: Constant folding, e.g. statically we can reduce 1 + 1 to 2, but not x + 1 to anything
        """
        self.additive_identity()
        self.multiplicative_identity()
        self.mult_by_zero()
        self.constant_fold()

def load_input(filepath):
    with open(filepath, 'r') as file:
        return file.read().strip().split()

def load_output(filepath):
    with open(filepath, 'r') as file:
        return file.read().strip()

def run_tests(test_dir, transform_function):
    input_dir = os.path.join('testbench', test_dir, 'inputs')
    output_dir = os.path.join('testbench', test_dir, 'outputs')

    for test_file in os.listdir(input_dir):
        input_path = os.path.join(input_dir, test_file)
        output_path = os.path.join(output_dir, test_file)

        input_data = load_input(input_path)

        expr = BinOpAst(input_data)
        transform_function(expr)

        generated_output = expr.prefix_str()

        expected_output = load_output(output_path)
        if generated_output == expected_output:
            print(f"{test_file}: PASS")
        else:
            print(f"{test_file}: FAIL")
            print(f"Expected: {expected_output}")
            print(f"Got: {generated_output}")

def run_all_tests():
    print("Additive Identity Test")
    run_tests("arith_id", BinOpAst.additive_identity)

    print("Multiplicative Identity Test")
    run_tests("mult_id", BinOpAst.multiplicative_identity)

if __name__ == "__main__":
    run_all_tests()
