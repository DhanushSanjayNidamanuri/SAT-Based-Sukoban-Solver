
"""
Sokoban Solver using SAT (Boilerplate)
--------------------------------------
Instructions:
- Implement encoding of Sokoban into CNF.
- Use PySAT to solve the CNF and extract moves.
- Ensure constraints for player movement, box pushes, and goal conditions.

Grid Encoding:
- 'P' = Player
- 'B' = Box
- 'G' = Goal
- '#' = Wall
- '.' = Empty space
"""

from pysat.formula import CNF
from pysat.solvers import Solver

# Directions for movement
DIRS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}


class SokobanEncoder:
    def __init__(self, grid, T):
        """
        Initialize encoder with grid and time limit.

        Args:
            grid (list[list[str]]): Sokoban grid.
            T (int): Max number of steps allowed.
        """
        self.grid = grid
        self.T = T
        self.N = len(grid)
        self.M = len(grid[0])

        self.goals = []
        self.boxes = []
        self.walls=[] # i added this
        self.player_start = None

        # TODO: Parse grid to fill self.goals, self.boxes, self.player_start
        self._parse_grid()
        self.num_boxes = len(self.boxes)
        self.cnf = CNF()

    def _parse_grid(self):
        """Parse grid to find player, boxes, and goals."""
        # TODO: Implement parsing logic
        for i in range(self.N):
            for j in range(self.M):
                if self.grid[i][j]=='G':
                    self.goals.append([i+2,j+2])
                elif self.grid[i][j]=='B':
                    self.boxes.append([i+2,j+2])
                    
                elif self.grid[i][j]=='P':
                    self.player_start=[i+2,j+2]
                elif self.grid[i][j]=='#':
                    self.walls.append([i+2,j+2])
        self.num_boxes = len(self.boxes)
        return


    # ---------------- Variable Encoding ----------------
    def var_player(self, x, y, t):
        """
        Variable ID for player at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        ans=(self.N + 3)*(self.M +2)*t*(1+self.num_boxes)
        ans+=(self.M+2)*x + y
        return ans

    def var_box(self, b, x, y, t):
        """
        Variable ID for box b at (x, y) at time t.
        """
        ans=(self.N + 3)*(self.M +2)*t*(1+self.num_boxes)
        ans+=(self.N + 3)*(self.M +2)*b+(self.M+2)*x + y
        # TODO: Implement encoding scheme
        return ans

    # ---------------- Encoding Logic ----------------
    def encode(self):
        """
        Build CNF constraints for Sokoban:
        - Initial state
        - Valid moves (player + box pushes)
        - Non-overlapping boxes
        - Goal condition at final timestep
        """
        # TODO: Add constraints for:
        # 1. Initial conditions
        self.cnf.append([self.var_player(self.player_start[0],self.player_start[1],0)]) #player
        i=1
        for coords in self.boxes:
            self.cnf.append([self.var_box(i,coords[0],coords[1],0)])
            i+=1
        # 2. Player movement
        for time in range(0,self.T+1):
            #player cannot go to padding and walls
            for i in range (1,self.N+3):
                self.cnf.append([-self.var_player(i,1,time)])
                self.cnf.append([-self.var_player(i,self.M+2,time)])

            for j in range(1,self.M+3):
                self.cnf.append([-self.var_player(1,j,time)])
                self.cnf.append([-self.var_player(self.N+2,j,time)])
            
            for coords in self.walls:
                self.cnf.append([-self.var_player(coords[0],coords[1],time)])

        for time in range(0,self.T):
            for i in range (2,self.N+2):
                for j in range(2,self.M+2):
                    #next move
                    self.cnf.append([self.var_player(i+1,j,time), -self.var_player(i,j,time+1), self.var_player(i-1,j,time), self.var_player(i,j-1,time),self.var_player(i,j+1,time),self.var_player(i,j,time)])
                    self.cnf.append([-self.var_player(i,j,time), self.var_player(i,j,time+1), self.var_player(i-1,j,time+1), self.var_player(i,j-1,time+1),self.var_player(i,j+1,time+1),self.var_player(i+1,j,time+1)])
        #cannot be in different places simultaneously
        for time in range(0,self.T+1):
            for i in range (2,self.N+2):
                for j in range(2,self.M+2):
                    for i1 in range (2,self.N+2):
                        for j1 in range(2,self.M+2):
                            if i!=i1 or j!=j1:
                                self.cnf.append([-self.var_player(i,j,time),-self.var_player(i1,j1,time)])
        # 3. Box movement (push rules)
        for b in range(1,self.num_boxes+1):
            for time in range(0,self.T):
                for i in range (2,self.N+2):
                    for j in range(2,self.M+2):
                        self.cnf.append([self.var_box(b,i,j,time),-self.var_box(b,i,j,time+1),self.var_box(b,i+1,j,time),self.var_box(b,i,j+1,time),self.var_box(b,i-1,j,time),self.var_box(b,i,j-1,time)])
                        #box moves down
                        self.cnf.append([-self.var_box(b,i-1,j,time),-self.var_box(b,i,j,time+1),self.var_player(i-2,j,time)])
                        self.cnf.append([-self.var_box(b,i-1,j,time),self.var_player(i-1,j,time+1),-self.var_box(b,i,j,time+1)])
                        #box moves right
                        self.cnf.append([-self.var_box(b,i,j-1,time),-self.var_box(b,i,j,time+1),self.var_player(i,j-2,time)])
                        self.cnf.append([-self.var_box(b,i,j-1,time),self.var_player(i,j-1,time+1),-self.var_box(b,i,j,time+1)])
                        #box moves up
                        self.cnf.append([-self.var_box(b,i+1,j,time),-self.var_box(b,i,j,time+1),self.var_player(i+2,j,time)])
                        self.cnf.append([-self.var_box(b,i+1,j,time),self.var_player(i+1,j,time+1),-self.var_box(b,i,j,time+1)])
                        #box moves left
                        self.cnf.append([-self.var_box(b,i,j+1,time),-self.var_box(b,i,j,time+1),self.var_player(i,j+2,time)])
                        self.cnf.append([-self.var_box(b,i,j+1,time),self.var_player(i,j+1,time+1),-self.var_box(b,i,j,time+1)])
        #box cannot be in 2 places simultaneously
        for b in range(1,self.num_boxes+1):
            for time in range(0,self.T+1):
                for i in range (2,self.N+2):
                    for j in range(2,self.M+2):
                        for i1 in range (2,self.N+2):
                            for j1 in range(2,self.M+2):
                                if i!=i1 or j!=j1:
                                    self.cnf.append([-self.var_box(b,i1,j1,time),-self.var_box(b,i,j,time)])
            for time in range(0,self.T+1):
            #box cannot go to padding and walls
                for i in range (1,self.N+3):
                    self.cnf.append([-self.var_box(b,i,1,time)])
                    self.cnf.append([-self.var_box(b,i,self.M+2,time)])
                for j in range(1,self.M+3):
                    self.cnf.append([-self.var_box(b,1,j,time)])
                    self.cnf.append([-self.var_box(b,self.N+2,j,time)])
                for coords in self.walls:
                    self.cnf.append([-self.var_box(b,coords[0],coords[1],time)])
                    
        # 4. Non-overlap constraints
            #player and box cannot overlap, box and box cannot overlap
        for time in range(1,self.T+1):
            for i in range (2,self.N+2):
                for j in range(2,self.M+2):
                    for b1 in range(1,self.num_boxes+1):
                        self.cnf.append([-self.var_box(b1,i,j,time),-self.var_player(i,j,time)])
                        for b2 in range(1,self.num_boxes+1):
                            if(b1!=b2):
                                self.cnf.append([-self.var_box(b1,i,j,time),-self.var_box(b2,i,j,time)])
        # 5. Goal conditions
        for b in range(1,self.num_boxes+1):
            arr=[]
            for coords in self.goals:
                
                arr.append(self.var_box(b,coords[0],coords[1],self.T))
            self.cnf.append(arr)

        # 6. Other conditions
        return self.cnf
    


def decode(model, encoder):
    """
    Decode SAT model into list of moves ('U', 'D', 'L', 'R').

    Args:
        model (list[int]): Satisfying assignment from SAT solver.
        encoder (SokobanEncoder): Encoder object with grid info.

    Returns:
        list[str]: Sequence of moves.
    """
    N, M, T = encoder.N, encoder.M, encoder.T
    B=encoder.num_boxes
    coords = {}   # also empty
    a=(N + 3)*(M +2)*(1+B)
    out=[]
    for v in model:
        if v>0 and v%a>=0 and v%a<=(N+3)*(M+2):
            coords[int(v/a)]=[int((v%a)/(M+2)),v%(M+2)]
    for i in range(T):
        dx=coords[i+1][0]-coords[i][0]
        dy=coords[i+1][1]-coords[i][1]
        if (dx,dy)==DIRS['U']:
            out.append('U')
        elif (dx,dy)==DIRS['D']:
            out.append('D')
        elif (dx,dy)==DIRS['L']:
            out.append('L')
        elif (dx,dy)==DIRS['R']:
            out.append('R')
    # TODO: Map player positions at each timestep to movement directions
    print(out)
    return out


def solve_sokoban(grid, T):
    """
    DO NOT MODIFY THIS FUNCTION.

    Solve Sokoban using SAT encoding.

    Args:
        grid (list[list[str]]): Sokoban grid.
        T (int): Max number of steps allowed.

    Returns:
        list[str] or "unsat": Move sequence or unsatisfiable.
    """
    encoder = SokobanEncoder(grid, T)
    cnf = encoder.encode()

    with Solver(name='g3') as solver:
        solver.append_formula(cnf)
        
        if not solver.solve():
            return -1

        model = solver.get_model()


        if not model:
            return -1

        return decode(model, encoder)


