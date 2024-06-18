# Sudoku Solver and Generator

This Python script provides functionality for solving, checking the uniqueness of solutions, and generating Sudoku puzzles. It supports Sudoku sizes of 4x4, 9x9, 16x16, and 25x25. The script uses SAT solvers to perform these operations efficiently.

This project was developed as part of the course INFO9015-1.

## Requirements

- Python 3
- Java Runtime Environment (JRE) to run the SAT solver

## Installation

1. Ensure Python 3 is installed on your system.
2. Ensure Java Runtime Environment (JRE) is installed.
3. Download the `org.sat4j.core.jar` SAT solver from [SAT4J](http://www.sat4j.org/).

## Usage

The script can be executed with different modes to solve Sudoku, check uniqueness, create a new puzzle, or create a minimal puzzle. The modes are specified using command-line arguments.

### Modes

- **Solve Sudoku**: `-s`
- **Check Uniqueness**: `-u`
- **Create Sudoku**: `-c`
- **Create Minimal Sudoku**: `-cm`

### Commands

1. **Solve Sudoku**

    ```
    ./sudokub.py -s <input>.txt
    ```

    Reads the Sudoku puzzle from `<input>.txt`, solves it, and prints the solution.

2. **Check Uniqueness**

    ```
    ./sudokub.py -u <input>.txt
    ```

    Reads the Sudoku puzzle from `<input>.txt`, checks for uniqueness of the solution, and prints the result.

3. **Create Sudoku**

    ```
    ./sudokub.py -c <size>
    ```

    Generates a Sudoku puzzle of the specified `<size>` (4, 9, 16, or 25), and prints it.

4. **Create Minimal Sudoku**

    ```
    ./sudokub.py -cm <size>
    ```

    Generates a minimal Sudoku puzzle of the specified `<size>` (4, 9, 16, or 25), and prints it.

## File Format

The input Sudoku file should be in the following format:

- Columns are separated by `|`
- Rows are separated by newlines
- Example of a 4x4 Sudoku:

    ```
    |1| | | |
    | | | |3|
    | | |2| |
    | |2| | |
    ```