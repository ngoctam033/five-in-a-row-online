from ui.board import Board
import logging
import numpy as np

class BoardGameLogic:
    """Xử lý logic của trò chơi cờ caro"""

    def check_win(self,grid):
        """Kiểm tra người chơi có thắng không sau nước đi vừa rồi"""
        directions = [(1,0), #tăng y, x giữ nguyên
                      (0,1), # giữ nguyên y, tăng x
                      (1,1), # tăng y, tăng x
                      (1,-1),# tăng y, giảm x
                      (-1,1),# giảm y, tăng x
                      (-1,-1)] # giảm y, giảm x
        # in ra grid
        for row in grid:
            logging.info(row)
        board = np.array(grid)
        # Kiểm tra chuỗi liên tiếp giá trị 1 trên từng hàng
        for row_idx in range(board.shape[0]):
            row = board[row_idx]
            max_consecutive = 0
            current = 0
            for cell in row:
                if cell == 1:
                    current += 1
                    if current > max_consecutive:
                        max_consecutive = current
                else:
                    current = 0
            logging.info(f"Row {row_idx} has max {max_consecutive} consecutive cells with value 1.")

        return 0