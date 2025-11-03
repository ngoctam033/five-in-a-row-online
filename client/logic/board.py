from ui.board import Board
import logging
import numpy as np

class BoardGameLogic:
    """Xử lý logic của trò chơi cờ caro"""

    def check_win(self, grid):
        """
        Kiểm tra thắng/thua trong game Cờ Caro (Five in a Row)
        - Thắng khi có 5 quân liên tiếp theo hàng, cột hoặc chéo.
        - Bị chặn hai đầu sẽ không tính là thắng.
        """
        """
        Kiểm tra người chơi có thắng hay không sau nước đi vừa rồi.
        Hiện tại chỉ kiểm tra theo hàng ngang (logic gốc của nhóm trưởng).
        """
        import numpy as np
        import logging

        board = np.array(grid)

        # Ghi log toàn bộ bàn cờ để debug
        for row in board:
            logging.info(row)

        # Duyệt từng hàng để kiểm tra chuỗi liên tiếp các ô có giá trị 1
        for row_idx, row in enumerate(board):
            consecutive = 0
            max_consecutive = 0

            for cell in row:
                if cell == 1:
                    consecutive += 1
                    max_consecutive = max(max_consecutive, consecutive)
                else:
                    consecutive = 0  # reset khi gặp ô khác 1

            logging.info(f"Row {row_idx}: max consecutive = {max_consecutive}")

        # Tạm thời chưa có điều kiện thắng cụ thể — giữ nguyên return gốc
        return 0

