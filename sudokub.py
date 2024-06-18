#!/usr/bin/python3

import sys
import subprocess
from math import comb


# reads a sudoku from file
# columns are separated by |, lines by newlines
# Example of a 4x4 sudoku:
# |1| | | |
# | | | |3|
# | | |2| |
# | |2| | |
# spaces and empty lines are ignored
def sudoku_read(filename):
    myfile = open(filename, 'r')
    sudoku = []
    N = 0
    for line in myfile:
        line = line.replace(" ", "")
        if line == "":
            continue
        line = line.split("|")
        if line[0] != '':
            exit("illegal input: every line should start with |\n")
        line = line[1:]
        if line.pop() != '\n':
            exit("illegal input\n")
        if N == 0:
            N = len(line)
            if N != 4 and N != 9 and N != 16 and N != 25:
                exit("illegal input: only size 4, 9, 16 and 25 are supported\n")
        elif N != len(line):
            exit("illegal input: number of columns not invariant\n")
        line = [int(x) if x != '' and int(x) >= 0 and int(x) <= N else 0 for x in line]
        sudoku += [line]
    return sudoku

# print sudoku on stdout
def sudoku_print(myfile, sudoku):
    if sudoku == []:
        myfile.write("impossible sudoku\n")
    N = len(sudoku)
    for line in sudoku:
        myfile.write("|")
        for number in line:
            if N > 9 and number < 10:
                myfile.write(" ")
            myfile.write(" " if number == 0 else str(number))
            myfile.write("|")
        myfile.write("\n")

# get number of constraints for sudoku
def sudoku_constraints_number(sudoku):
    N = len(sudoku)
    n = int(N ** 0.5)
    
    cell_constraints = N**2
    row_column_constraints = 2 * N**2 * comb(N, 2)
    box_constraints = N**2 * comb(n**2, 2)
    initial_numbers = sum(1 for row in sudoku for num in row if num > 0)
    
    count = cell_constraints + row_column_constraints + box_constraints + initial_numbers
    return count

# prints the generic constraints for sudoku of size N
def sudoku_generic_constraints(myfile, N):
    num_digits = len(str(N))

    def output(s):
        myfile.write(s)

    def newlit(i, j, k, negative=False):
        sign = "-" if negative else ""
        output(f"{sign}{i:0{num_digits}d}{j:0{num_digits}d}{k:0{num_digits}d} ")

    def newcl():
        output("0\n")

    if N == 4:
        n = 2
    elif N == 9:
        n = 3
    elif N == 16:
        n = 4
    elif N == 25:
        n = 5
    else:
        exit("Only supports size 4, 9, 16 and 25")

    # Cell Constraints: At least one number in each cell
    for i in range(1, N+1):
        for j in range(1, N+1):
            for k in range(1, N+1):
                newlit(i, j, k)
            newcl()

    # Row and Column Constraints: At most one occurrence of each number in each row and column
    for k in range(1, N+1):
        for i in range(1, N+1):
            for j1 in range(1, N+1):
                for j2 in range(j1+1, N+1):
                    newlit(i, j1, k, True)
                    newlit(i, j2, k, True)
                    newcl()
                    newlit(j1, i, k, True)
                    newlit(j2, i, k, True)
                    newcl()

    # Box Constraints: At most one occurrence of each number in each box
    for k in range(1, N+1):
        for x in range(n):
            for y in range(n):
                for u1 in range(1, n+1):
                    for v1 in range(1, n+1):
                        i1, j1 = n*x + u1, n*y + v1
                        for u2 in range(u1, n+1):
                            for v2 in range(v1+1 if u1 == u2 else 1, n+1):
                                i2, j2 = n*x + u2, n*y + v2
                                newlit(i1, j1, k, True)
                                newlit(i2, j2, k, True)
                                newcl()

def sudoku_specific_constraints(myfile, sudoku):

    N = len(sudoku)

    num_digits = len(str(N))

    def output(s):
        myfile.write(s)

    def newlit(i, j, k):
        output(f"{i:0{num_digits}d}{j:0{num_digits}d}{k:0{num_digits}d} ")

    def newcl():
        output("0\n")

    for i in range(N):
        for j in range(N):
            if sudoku[i][j] > 0:
                newlit(i + 1, j + 1, sudoku[i][j])
                newcl()

def sudoku_other_solution_constraint(myfile, sudoku):

    N = len(sudoku)

    num_digits = len(str(N))

    def output(s):
        myfile.write(s)

    def newlit(i, j, k):
        output(f"-{i:0{num_digits}d}{j:0{num_digits}d}{k:0{num_digits}d} ")

    def newcl():
        output("0\n")

    for i in range(N):
            for j in range(N):
                if sudoku[i][j] > 0:
                    newlit(i + 1, j + 1, sudoku[i][j])
    newcl()
                
def sudoku_solve(filename):
    command = "java -jar org.sat4j.core.jar " + filename
    process = subprocess.Popen(command, shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    for line in out.split(b'\n'):
        line = line.decode("utf-8")
        if line == "" or line[0] == 'c':
            continue
        if line[0] == 's':
            if not line.startswith('s SATISFIABLE'):
                return []
            continue
        if line[0] == 'v':
            line = line[2:]
            units = line.split()
            if not line.rstrip().endswith('0'):
                exit("strange output from SAT solver:" + line + "\n")
            units = [int(x) for x in units if int(x) > 0]  # Exclude negative literals
            N = len(units)
            if N == 16:
                N = 4
            elif N == 81:
                N = 9
            elif N == 256:
                N = 16
            elif N == 625:
                N = 25
            else:
                exit("strange output from SAT solver:" + line + "\n")
            sudoku = [[0 for i in range(N)] for j in range(N)]
            num_digits = len(str(N))
            for number in units:
                divisor = 10 ** (2 * num_digits)
                i = number // divisor
                j = (number % divisor) // (10 ** num_digits)
                k = number % (10 ** num_digits)
                sudoku[i - 1][j - 1] = k

            return sudoku
        exit("strange output from SAT solver:" + line + "\n")
    return []


import shutil
import random

def sudoku_generate(N, minimal=False, baseFilename="sudoku_base.cnf"):
    toremove = int(N**2 * 0.6)
    sudoku = None
    initial_placements = int(N**2 * 0.05)  # 5% of the total cells

    while sudoku is None:
        sudoku = [[0] * N for _ in range(N)]
        place_initial_numbers(sudoku, N, initial_placements)
        sudoku_print(sys.stdout, sudoku)

        sudoku_solution = generate_and_solve_sudoku(sudoku, N, baseFilename)
        sudoku = remove_excluded_digit_if_minimal(sudoku_solution, N, minimal)

    removed_positions = set()
    attempts, max_attempts = 0, 300 if N == 25 else N**2

    while len(removed_positions) < toremove and attempts < max_attempts:
        i, j = random.randint(0, N-1), random.randint(0, N-1)
        if (i, j) in removed_positions or sudoku[i][j] == 0:
            continue        
        original = sudoku[i][j]
        sudoku[i][j] = 0
        if is_unique_solution(sudoku):
            removed_positions.add((i, j))
        else:
            sudoku[i][j] = original
        attempts += 1

    return sudoku

def generate_and_solve_sudoku(sudoku, N, filename):
    constraints_number = sudoku_constraints_number(sudoku)
    with open(filename, 'w') as base_file:
        base_file.write(f"p cnf {N}{N}{N} {constraints_number}\n")
        sudoku_generic_constraints(base_file, N)
        sudoku_specific_constraints(base_file, sudoku)

    sudoku_solution = sudoku_solve(filename)
    with open(filename, 'w') as base_file:
        base_file.write(f"p cnf {N}{N}{N} {constraints_number}\n")
        sudoku_generic_constraints(base_file, N)
        if sudoku_solution:
            sudoku_other_solution_constraint(base_file, sudoku_solution)
    return sudoku_solution

def remove_excluded_digit_if_minimal(sudoku_solution, N, minimal):
    if minimal:
        excluded_digit = random.randint(1, N)
        for i in range(N):
            for j in range(N):
                if sudoku_solution[i][j] == excluded_digit:
                    sudoku_solution[i][j] = 0
        if not is_unique_solution(sudoku_solution):
                sudoku_solution = None
    return sudoku_solution

def is_unique_solution(sudoku):
    temp_file_name = "sudoku_temp.cnf"
    shutil.copy("sudoku_base.cnf", temp_file_name)
    with open(temp_file_name, 'a') as temp_file:
        sudoku_specific_constraints(temp_file, sudoku)
    return sudoku_solve(temp_file_name) == []

def place_initial_numbers(sudoku, N, count):
    for _ in range(count):
        i, j = random.randint(0, N-1), random.randint(0, N-1)
        while sudoku[i][j] != 0:
            i, j = random.randint(0, N-1), random.randint(0, N-1)
        value = random.randint(1, N)
        while not is_valid_placement(sudoku, i, j, value, N):
            value = random.randint(1, N)
        sudoku[i][j] = value

def is_valid_placement(sudoku, row, col, value, N):
    # Check row and column
    for k in range(N):
        if sudoku[row][k] == value or sudoku[k][col] == value:
            return False

    # Check box
    box_size = int(N**0.5)
    box_row_start = row - row % box_size
    box_col_start = col - col % box_size
    for i in range(box_row_start, box_row_start + box_size):
        for j in range(box_col_start, box_col_start + box_size):
            if sudoku[i][j] == value:
                return False

    return True
from enum import Enum
class Mode(Enum):
    SOLVE = 1
    UNIQUE = 2
    CREATE = 3
    CREATEMIN = 4

OPTIONS = {}
OPTIONS["-s"] = Mode.SOLVE
OPTIONS["-u"] = Mode.UNIQUE
OPTIONS["-c"] = Mode.CREATE
OPTIONS["-cm"] = Mode.CREATEMIN

if len(sys.argv) != 3 or not sys.argv[1] in OPTIONS :
    sys.stdout.write("./sudokub.py <operation> <argument>\n")
    sys.stdout.write("     where <operation> can be -s, -u, -c, -cm\n")
    sys.stdout.write("  ./sudokub.py -s <input>.txt: solves the Sudoku in input, whatever its size\n")
    sys.stdout.write("  ./sudokub.py -u <input>.txt: check the uniqueness of solution for Sudoku in input, whatever its size\n")
    sys.stdout.write("  ./sudokub.py -c <size>: creates a Sudoku of appropriate <size>\n")
    sys.stdout.write("  ./sudokub.py -cm <size>: creates a Sudoku of appropriate <size> using only <size>-1 numbers\n")
    sys.stdout.write("    <size> is either 4, 9, 16, or 25\n")
    exit("Bad arguments\n")

mode = OPTIONS[sys.argv[1]]
if mode == Mode.SOLVE or mode == Mode.UNIQUE:
    filename = str(sys.argv[2])
    sudoku = sudoku_read(filename)
    N = len(sudoku)
    myfile = open("sudoku.cnf", 'w')
    myfile.write("p cnf " + str(N) + str(N) + str(N) + " " + str(sudoku_constraints_number(sudoku)) + "\n")

    sudoku_generic_constraints(myfile, N)
    sudoku_specific_constraints(myfile, sudoku)
    myfile.close()
    sys.stdout.write("sudoku\n")
    sudoku_print(sys.stdout, sudoku)
    sudoku = sudoku_solve("sudoku.cnf")    
    sys.stdout.write("\nsolution\n")
    sudoku_print(sys.stdout, sudoku)
    if sudoku != [] and mode == Mode.UNIQUE:
        myfile = open("sudoku.cnf", 'a')
        sudoku_other_solution_constraint(myfile, sudoku)
        myfile.close()
        sudoku = sudoku_solve("sudoku.cnf")
        if sudoku == []:
            sys.stdout.write("\nsolution is unique\n")
        else:
            sys.stdout.write("\nother solution\n")
            sudoku_print(sys.stdout, sudoku)
elif mode == Mode.CREATE:
    size = int(sys.argv[2])
    sudoku = sudoku_generate(size)
    sys.stdout.write("\ngenerated sudoku\n")
    sudoku_print(sys.stdout, sudoku)
elif mode == Mode.CREATEMIN:
    size = int(sys.argv[2])
    sudoku = sudoku_generate(size, True)
    sys.stdout.write("\ngenerated sudoku\n")
    sudoku_print(sys.stdout, sudoku)
