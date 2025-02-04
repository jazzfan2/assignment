#!/usr/bin/env python3
# Name:   assignment.py
# Author: Rob Toscani
# Date:   26-01-2025
# Description: Implementation in Python3 of algorithm and pseudocode on:
# https://users.cs.duke.edu/~brd/Teaching/Bio/asmb/current/Handouts/munkres.html
# (see also https://en.wikipedia.org/wiki/Hungarian_algorithm)
#
# Efficient in finding optimum (max. or min.) (sum-)cost assignment in a square cost matrix,
# also if more than one configuration with same optimum sum exist.
#
# The matrix is a flat text file with space-separated integers arranged in a square matrix pattern.
# for instance a random matrix, generated by program: '~/scripts/matrix.py'
# ANSI color codes can be suppressed from the text stream output of this program,
# by filtering this via a pipe by the function "nocolor" in ~/scripts/functions.sh
#
# Example command to analyze first 40 rows and columns of a square random 60x60 matrix
# to result in a maximum cost assignment, without color indication:
# matrix.py 60 | assignment.py -x -n 40 - | nocolor
#
############################################################################################
#

import sys
import argparse


# If filename is '-', input redirection is performed. Otherwise the file with given name is opened:
def process_input(filename):
    if filename == '-':
        return sys.stdin
    else:
        try:
            return open(filename, 'r')
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            sys.exit(1)


# Print a matrix, with assigned elements (on starred zero positions) green and zeroes (elsewhere) yellow:
def printmatrix(matrix):
    for i in range(n):
        for j in range(n):
            if matrix[i][j] == 0 and M[i][j] == 1:
                print("\x1b[1;94m%4d\x1b[0m" % matrix[i][j], end = '') # Assigned zeroes blue:
            elif C[i][j] == 0 and M[i][j] == 1:
                print("\x1b[1;92m%4d\x1b[0m" % matrix[i][j], end = '') # Assigned elements green:
            elif C[i][j] == 0 and M[i][j] == 2:
                print("\x1b[1;91m%4d\x1b[0m" % matrix[i][j], end = '') # Primed zeroes red:
            elif matrix[i][j] == 0:
                print("\x1b[1;93m%4d\x1b[0m" % matrix[i][j], end = '') # Other zeroes yellow:
            else:
                print("%4d" % matrix[i][j], end = '')
        print()
    print()


# Determine maximum matrix value:
def maxmatrix(matrix):
    maximum = 0
    for i in range(n):
        for j in range(n):
            if matrix[i][j] > maximum:
                maximum = matrix[i][j]
    return(maximum)


# Sum the matrix values over the assigned positions:
def summatrix(matrix):
    total = 0
    for i in range(n):
        for j in range(n):
            if C[i][j] == 0 and M[i][j] == 1:
                total += matrix[i][j]
    return(total)


# Print the cover-pattern ('strikes') through the zeroes:
def printstrikes(R_cov, C_cov):
    for i in range(n):
        print(" ", end = '')
        for j in range(n):
            if C[i][j] == 0 and M[i][j] == 1:
                print("\x1b[1;94m 0  \x1b[0m", end = '')   # Starred zeroes blue:
            elif C[i][j] == 0 and M[i][j] == 2:
                print("\x1b[1;91m 0  \x1b[0m", end = '')   # Primed zeroes red
            elif C[i][j] == 0:
                print("\x1b[1;93m 0  \x1b[0m", end = '')   # Other zeroes yellow
            elif R_cov[i] == 1 and C_cov[j] == 1:
                print("-|--", end = '')
            elif R_cov[i] == 1 and C_cov[j] == 0:
                print("----", end = '')
            elif R_cov[i] == 0 and C_cov[j] == 1:
                print(" |  ", end = '')
            else:
                print(" .  ", end = '')
        print()
    print()


# STEP 1
# For each row of the matrix, find the smallest element and subtract it from every element in its row.
# (Opm. RJT: dit gebeurt hier niet *ook* voor de kleinste elementen per *kolom*. Blijkt dus niet nodig!)
# Go to Step 2
def step1(*args):
    print("\n===> STEP 1: subtract smallest element in row from each element:\n")
    global step
    for i in range(0, n):
        minval = C[i][0]
        for j in range(1, n):
            if minval > C[i][j]:
                minval = C[i][j]
        for j in range(n):
            C[i][j] = C[i][j] - minval
    printmatrix(C)
    step = 2


# STEP 2
# Find a zero (Z) in the resulting matrix.
# If there is no starred zero in its row or column, star Z. Repeat for each element in the matrix.
# Go to Step 3
def step2(*args):
    print("\n===> STEP 2: \x1b[1;94mstar\x1b[0m zeroes with no starred zero in same row and column:\n")
    global step
    for i in range(0, n):
        for j in range(0, n):
            if C[i][j] == 0 and C_cov[j] == 0 and R_cov[i] == 0:
                M[i][j]  = 1
                C_cov[j] = 1
                R_cov[i] = 1
    for i in range(0, n):
        C_cov[i] = 0
        R_cov[i] = 0
    printmatrix(C)
    step = 3


# STEP 3
# Cover each column containing a starred zero.
# If n columns are covered, the starred zeros describe a complete set of unique assignments.
# In this case, Go to DONE, otherwise, Go to Step 4.
def step3(*args):
    print("\n===> STEP 3: cover all columns containing a \x1b[1;94mstarred\x1b[0m zero:\n")
    global step
    for i in range(0, n):
        for j in range(0, n):
            if M[i][j] == 1:
                C_cov[j] = 1
    count = 0
    for j in range(0, n):
        count += C_cov[j]
    printmatrix(C)
    printstrikes(R_cov, C_cov)
    if count >= n:
        step = 7    # Done
    else:
        step = 4


# STEP 4
# Find a noncovered zero and prime it.
# If there is no starred zero in the row containing this primed zero, Go to Step 5.
# Otherwise, cover this row and uncover the column containing the starred zero.
# Continue in this manner until there are no uncovered zeros left.
# Go to Step 6.
def step4(*args):
    print("\n===> STEP 4: \x1b[1;91mprime\x1b[0m uncovered zero, uncover column of \x1b[1;94mstarred\x1b[0m in row and cover \x1b[1;91mprimed\x1b[0m row:\n")

    def find_a_zero(*args):
        row = col = undefined    # Meaning: no cell found so far with a zero value
        done = False
        for i in range(n):
            for j in range(n):
                if C[i][j] == 0 and R_cov[i] == 0 and C_cov[j] == 0:
                    row = i
                    col = j
                    done = True
            if done:
                break
        return (row, col)

    def star_in_row(row):
        tbool = False
        for j in range(n):
            if M[row][j] == 1:
                tbool = True
        return tbool

    def find_star_in_row(row):
        col = 0
        for j in range(n):
            if M[row][j] == 1:
                col = j
        return col

    done = False
    global step
    while not(done):
        row, col = find_a_zero();
        if row == undefined:   # Meaning: no row with a zero found => go to step 6
            printmatrix(C)
            printstrikes(R_cov, C_cov)
            done = True
            step = 6
        else:
            M[row][col] = 2
            if star_in_row(row):
                col = find_star_in_row(row)
                R_cov[row] = 1
                C_cov[col] = 0
            else:
                global z0_r
                z0_r = row
                global z0_c
                z0_c = col
                printmatrix(C)
                printstrikes(R_cov, C_cov)
                print("First \x1b[1;91mprimed\x1b[0m zero without \x1b[1;94mstarred\x1b[0m zero on same row: (%d,%d)" % (z0_r, z0_c))
                done = True
                step = 5


# STEP 5
# Construct a series of alternating primed and starred zeros as follows.
# Let Z0 represent the uncovered primed zero found in Step 4.
# Let Z1 denote the starred zero in the column of Z0 (if any).
# Let Z2 denote the primed zero in the row of Z1 (there will always be one).
# Continue until the series terminates at a primed zero that has no starred zero in its column.
# Unstar each starred zero of the series, star each primed zero of the series,
# erase all primes and uncover every line in the matrix.
# Return to Step 3.
def step5(*args):
    print("\n===> STEP 5: Construct a series of alternating \x1b[1;91mprimed\x1b[0m and \x1b[1;94mstarred\x1b[0m zeros:\n")

    def find_star_in_col(c):
        r = undefined
        for i in range(n):
            if M[i][c] == 1:
                r = i
        return r

    def find_prime_in_row(r):
        for j in range(n):
            if M[r][j] == 2:
                c = j
        return c

    def convert_path(*args):
        for i in range(1,len(path)+1):  # Opm RJT: hoogste waarde = 'len(path)' ipv 'n' (in pseudocode)!
            if M[path[i][0]][path[i][1]] == 1:
                M[path[i][0]][path[i][1]] = 0
            else:
                M[path[i][0]][path[i][1]] = 1

    def clear_covers(*args):
        for i in range(n):
            R_cov[i] = 0
            C_cov[i] = 0

    def erase_primes(*args):
        for i in range(n):
            for j in range(n):
                if M[i][j] == 2:
                    M[i][j] = 0

    global step
    count = 1
    path = {}
    # z0 = (z0_r, z0_c):
    path[count] = (z0_r, z0_c)
    done = False
    while not(done):
        r = find_star_in_col(path[count][1])
        if r >= 0:          # Meaning: row found
            count += 1
            # z1 = (find_star_in_col(z0_c), z0_c):
            path[count] = (r, path[count-1][1])
        else:
            done = True
        if not(done):
            c = find_prime_in_row(path[count][0])
            count += 1
            # z2 = (z1_r, find_prime_in_row(z1_r)):
            path[count] = (path[count-1][0], c)
    convert_path()
    clear_covers()
    erase_primes()
    print("Path of alternating (= starred<->primed and v.v.) zeroes :", path, "\n")
    printmatrix(C)
    step = 3


# STEP 6
# Determine value of smallest uncovered element, add it to every element of each covered row,
# and subtract it from every element of each uncovered column.
# Return to Step 4 without altering any stars, primes, or covered lines.
def step6(*args):
    print("\n===> STEP 6: add minimum uncovered to covered rows, subtract from uncovered columns:\n")

    def find_smallest(*args):
        minval = float('inf')
        for i in range(0, n):
            for j in range(0, n):
                if R_cov[i] == 0 and C_cov[j] == 0:
                    if C[i][j] < minval:
                        minval = C[i][j]
        return minval

    global step
    minval = find_smallest()
    for i in range(0, n):
        for j in range(0, n):
            if R_cov[i] == 1:
                C[i][j] += minval
            if C_cov[j] == 0:
                C[i][j] -= minval
    print("Minimum uncovered value = ", minval, "\n")
    printmatrix(C)
    step = 4


# (Main-function starts here:)

x = 0                     # Meaning: default minimum (cost-)sum optimization
undefined = -1000000      # Meaning: matrix- or list-index is yet undefined

parser = argparse.ArgumentParser()

# Optional arguments:
parser.add_argument("-n", "--number", type=int, default=0, help="Number of rows and columns")
parser.add_argument("-x", "--maximum", help="Determine maximum instead of minimum", action='store_true')

# Positional arguments:
parser.add_argument("input", help="Input file or '-' for stdin")

args = parser.parse_args()

# Open the matrix text-file by name or from standard input redirection:
with process_input(args.input) as f:
    content = f.readlines()

# Convert the matrix into a 2d-list:
matrix = []
for line in content:
    if not line:
        break
    lis = [int(i) for i in line.split()]
    matrix.append(lis)

# Consequences of options:
# Number of lowest rows and columns used (-n argument, or full matrix size if -n = 0 or not given):
n      = len(matrix)        if args.number == 0      else args.number

# For maximum cost assignment (option -x) subtract all values from maximum matrix value:
if args.maximum:  # Maximum cost assigment:
    C = [ [ maxmatrix(matrix) - element for element in row ] for row in matrix ]
else:             # Minimum cost assigment:
    C = [ [ element for element in row ] for row in matrix ]


# Mask matrix to indicate primed (= 2) and starred (= 1) zeros in C
M = [ [ 0 for element in row ] for row in matrix ]

# R_cov and C_cov maintain record of which row/columns are covered:
R_cov = [ 0 for i in range(n) ]
C_cov = [ 0 for i in range(n) ]

z0_r, z0_c = undefined, undefined   # Initialisatiewaarde met betekenis: geen rij, kolom

done = False
step = 1
while not(done):
    if step == 1:
        step1()
    elif step == 2:
        step2()
    elif step == 3:
        step3()
    elif step == 4:
        step4()
    elif step == 5:
        step5()
    elif step == 6:
        step6()
    else:
        done = True

# DONE
# Assignment pairs are indicated by the positions of the starred zeros in the cost matrix.
# If C[i][j] is a starred zero, then the element associated with row i is assigned
# to the element associated with column j.
print("\n===> DONE <===\n")


# Print the matrix and count the original numbers on the positions of the assigned zeroes,
# resulting in minimum (or maximum, if specified) sum:
printmatrix(matrix)
print("\n", summatrix(matrix))
