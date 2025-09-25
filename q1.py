"""
sudoku_solver.py

Implement the function `solve_sudoku(grid: List[List[int]]) -> List[List[int]]` using a SAT solver from PySAT.
"""

from pysat.formula import CNF
from pysat.solvers import Solver
from typing import List

def solve_sudoku(grid: List[List[int]]) -> List[List[int]]:
    """Solves a Sudoku puzzle using a SAT solver. Input is a 2D grid with 0s for blanks."""

    # TODO: implement encoding and solving using PySAT
    n=len(grid)
    places=list()
    nums=list()
    cnf=CNF()

    
    for i in range(9):
            for k in range(9):
                    cnf.append([100*(k+1)+10*(i+1)+(j+1) for j in range(9)])
                    

    for j in range(9):
           for k in range(9):
                  cnf.append([100*(k+1)+10*(i+1)+(j+1) for i in range (9)])
    
    for i in range(9):
           for j in range(9):
                  if grid[i][j]>0:
                         cnf.append([100*(grid[i][j]) + 10*(i+1) + (j+1)])
                  for k1 in range(9):
                     for k2 in range(9):
                      if k1!=k2:
                          cnf.append([ -(100*(k1+1)+10*(i+1)+(j+1)) , -(100*(k2+1)+10*(i+1)+(j+1))])     

    for i in range(0,9,3):
           for j in range(0,9,3):
                  for k in range(9):
                        cnf.append([100*(k+1)+10*(i+1+i1)+(j+1+j1) for i1 in range(3) for j1 in range(3)])

    
    with Solver(name='glucose3') as solver:
        solver.append_formula(cnf.clauses)
        if solver.solve():
            model = solver.get_model()
            for i in model:                
                  if(i>0):
                        grid[int((i%100)/10) -1][(i%10)-1]=int(i/100)
        else:
              return [[]]
            
    return grid