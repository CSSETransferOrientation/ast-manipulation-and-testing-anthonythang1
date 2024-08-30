#!/usr/bin/python3
import os
from os.path import join as osjoin
import unittest
from enum import Enum

# Node type enumeration for distinguishing between numbers and operators
NodeType = Enum('BinOpNodeType', ['number', 'operator'])

class BinOpAst:
    """
    A binary operator AST that can be initialized from a list of tokens in prefix notation.
    """

    def __init__(self, prefix_list):
        if not prefix_list:
            raise ValueError("Cannot initialize BinOpAst with an empty prefix list.")
        self.val = prefix_list.pop(0)
        if self.val.isnumeric():
            self.type = NodeType.number
            self.left = None
            self.right = None
        else:
            self.type = NodeType.operator
            self.left = BinOpAst(prefix_list)
            self.right = BinOpAst(prefix_list)

    def __str__(self, indent=0):
        """
        Converts the binary tree to a string with indentation representing hierarchy.
        """
        ilvl = '  ' * indent
        left = f'\n{ilvl}{self.left.__str__(indent + 1)}' if self.left else ''
        right = f'\n{ilvl}{self.right.__str__(indent + 1)}' if self.right else ''
        return f"{ilvl}{self.val}{left}{right}"

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

    # Additive identity reduction
    def additive_identity(self):
        if self.type == NodeType.number:
            return
        self.left.additive_identity()
        self.right.additive_identity()
        if self.val == '*' or self.val == '/':
            return
        if self.left.val == '0':
            self._replace_node_with(self.right)
        elif self.right.val == '0':
            self._replace_node_with(self.left)

    # Multiplicative identity reduction
    def multiplicative_identity(self):
        if self.type == NodeType.number:
            return
        self.left.multiplicative_identity()
        self.right.multiplicative_identity()
        if self.val == '+':
            return
        if self.left.val == '1':
            self._replace_node_with(self.right)
        elif self.right.val == '1':
            self._replace_node_with(self.left)

    # Multiplication by zero reduction
    def mult_by_zero(self):
        if self.type == NodeType.number:
            return
        self.left.mult_by_zero()
        self.right.mult_by_zero()
        if self.val == '*' and (self.left.val == '0' or self.right.val == '0'):
            self._replace_node_with(BinOpAst(['0']))

    def _replace_node_with(self, other):
        """
        Replaces the current node with another node.
        """
        self.val = other.val
        self.type = other.type
        self.left = other.left
        self.right = other.right

    # Simplifies binary operations
    def simplify_binops(self):
        self.additive_identity()
        self.multiplicative_identity()
        self.mult_by_zero()
        self.constant_fold()

    def constant_fold(self):
        """
        Fold constants (e.g., 1 + 2 = 3).
        """
        # Optional implementation
        pass

class TreeOpTester(unittest.TestCase):

    def run_test_case(self, test_name, operation):
        print(f"\nTesting {test_name}")
        input_files = osjoin(f'testbench/{test_name}', 'inputs')
        output_files = osjoin(f'testbench/{test_name}', 'outputs')
        log = []
        flag = True

        for file_name in os.listdir(input_files):
            with open(osjoin(input_files, file_name)) as f:
                input_to_test = f.read().strip()
            if not input_to_test:
                print(f"Skipping empty input file: {file_name}")
                continue
            with open(osjoin(output_files, file_name)) as f:
                expected_output = f.read().strip()

            tree = BinOpAst(input_to_test.split())
            operation(tree)
            actual_output = tree.prefix_str()

            log.append((file_name, actual_output, expected_output))
            if actual_output != expected_output:
                flag = False
                print(f"!FAIL! {file_name}: Expected '{expected_output}', but got '{actual_output}'")

        for item in log:
            print(f'{"!FAIL!" if item[1] != item[2] else "Passed"} {item[0]}: {item[1]} = {item[2]}')

        if not flag:
            raise AssertionError(f"Some test cases failed in {test_name}. Check the log above for details.")

    def test_arith_id(self):
        self.run_test_case('arith_id', lambda tree: tree.additive_identity())

    def test_mult_id(self):
        self.run_test_case('mult_id', lambda tree: tree.multiplicative_identity())

    def test_mult_by_zero(self):
        self.run_test_case('mult_by_zero', lambda tree: tree.mult_by_zero())

if __name__ == "__main__":
    unittest.main()
