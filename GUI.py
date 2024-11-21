import random
import streamlit as st
from copy import deepcopy

# Ma trận hướng di chuyển
DIRECTIONS = {"U": [-1, 0], "D": [1, 0], "L": [0, -1], "R": [0, 1]}
# Ma trận đích
END = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

# Hàm hiển thị ma trận (thay đổi cho Streamlit)
def display_puzzle(puzzle):
    for row in puzzle:
        st.write(" | ".join([str(num) if num != 0 else " " for num in row]))

# Lớp Node lưu trữ trạng thái của mỗi ma trận
class Node:
    def __init__(self, current_node, previous_node, g, h, dir):
        self.current_node = current_node  # Ma trận hiện tại
        self.previous_node = previous_node  # Ma trận trước đó
        self.g = g  # Chi phí từ điểm bắt đầu đến điểm hiện tại
        self.h = h  # Chi phí từ điểm hiện tại đến đích
        self.dir = dir  # Hướng di chuyển

    def f(self):
        return self.g + self.h  # Tổng chi phí (g + h)

# Hàm tìm vị trí của một phần tử trong ma trận
def get_pos(current_state, element):
    for row in range(len(current_state)):
        if element in current_state[row]:
            return (row, current_state[row].index(element))

# Hàm tính chi phí Euclid
def euclidianCost(current_state):
    cost = 0
    for row in range(len(current_state)):
        for col in range(len(current_state[0])):
            pos = get_pos(END, current_state[row][col])  # Vị trí của phần tử trong ma trận đích
            cost += abs(row - pos[0]) + abs(col - pos[1])  # Tính chi phí Euclid
    return cost

# Hàm lấy các node liền kề với node hiện tại
def getAdjNode(node):
    listNode = []
    emptyPos = get_pos(node.current_node, 0)  # Vị trí của ô trống (0)

    for dir in DIRECTIONS.keys():
        newPos = (emptyPos[0] + DIRECTIONS[dir][0], emptyPos[1] + DIRECTIONS[dir][1])
        if 0 <= newPos[0] < len(node.current_node) and 0 <= newPos[1] < len(node.current_node[0]):
            newState = deepcopy(node.current_node)  # Sao chép ma trận hiện tại
            newState[emptyPos[0]][emptyPos[1]] = node.current_node[newPos[0]][newPos[1]]  # Di chuyển phần tử
            newState[newPos[0]][newPos[1]] = 0  # Đặt ô trống vào vị trí mới
            listNode.append(Node(newState, node.current_node, node.g + 1, euclidianCost(newState), dir))  # Thêm node mới vào danh sách

    return listNode

# Hàm lấy node tốt nhất từ danh sách mở
def getBestNode(openSet):
    firstIter = True

    for node in openSet.values():
        if firstIter or node.f() < bestF:
            firstIter = False
            bestNode = node
            bestF = bestNode.f()
    return bestNode

# Hàm xây dựng đường đi nhỏ nhất
def buildPath(closedSet):
    node = closedSet[str(END)]  # Lấy node kết thúc
    branch = list()

    while node.dir:
        branch.append({
            'dir': node.dir,
            'node': node.current_node
        })
        node = closedSet[str(node.previous_node)]  # Quay lại node trước đó
    branch.append({
        'dir': '',
        'node': node.current_node
    })
    branch.reverse()  # Đảo ngược danh sách để có đường đi từ đầu đến cuối

    return branch

# Hàm kiểm tra số đảo chẵn (đảm bảo bài toán có thể giải được)
def is_solvable(puzzle):
    flat_puzzle = [item for row in puzzle for item in row]
    inversions = 0
    for i in range(len(flat_puzzle)):
        for j in range(i + 1, len(flat_puzzle)):
            if flat_puzzle[i] != 0 and flat_puzzle[j] != 0 and flat_puzzle[i] > flat_puzzle[j]:
                inversions += 1
    return inversions % 2 == 0  # Đảm bảo số đảo chẵn

# Hàm tạo ma trận ngẫu nhiên có thể giải được
def generate_random_puzzle():
    while True:
        puzzle = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]  # Ma trận ban đầu
        flat_puzzle = [item for row in puzzle for item in row]
        random.shuffle(flat_puzzle)  # Xáo trộn ma trận
        # Chia lại danh sách thành ma trận 3x3
        puzzle = [flat_puzzle[i:i+3] for i in range(0, len(flat_puzzle), 3)]
        if is_solvable(puzzle):  # Kiểm tra xem ma trận có thể giải được không
            return puzzle

# Hàm chính để giải bài toán
def main(puzzle):
    open_set = {str(puzzle): Node(puzzle, puzzle, 0, euclidianCost(puzzle), "")}
    closed_set = {}

    while True:
        test_node = getBestNode(open_set)  # Lấy node tốt nhất từ danh sách mở
        closed_set[str(test_node.current_node)] = test_node

        if test_node.current_node == END:
            return buildPath(closed_set)  # Nếu tìm được đường đi đến đích, trả về kết quả

        adj_node = getAdjNode(test_node)  # Lấy các node liền kề
        for node in adj_node:
            if str(node.current_node) in closed_set.keys() or str(node.current_node) in open_set.keys() and open_set[
                str(node.current_node)].f() < node.f():  # Nếu node đã được xét hoặc có chi phí thấp hơn
                continue
            open_set[str(node.current_node)] = node  # Thêm node vào danh sách mở

        del open_set[str(test_node.current_node)]  # Xóa node đã xét khỏi danh sách mở

# Streamlit GUI code
def puzzle_gui():
    st.title("Giải đố 8 ô")

    # Thiết lập trạng thái cho ma trận ban đầu
    if 'steps' not in st.session_state:
        st.session_state.steps = []
    if 'step_index' not in st.session_state:
        st.session_state.step_index = 0
    if 'total_steps' not in st.session_state:
        st.session_state.total_steps = 0
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'puzzle' not in st.session_state:
        st.session_state.puzzle = generate_random_puzzle()  # Tạo ma trận ngẫu nhiên

    # Hiển thị ma trận chưa giải
    st.subheader("Ma trận chưa giải:")
    display_puzzle(st.session_state.puzzle)

    # Nút bắt đầu giải đố
    if st.button("Bắt đầu giải đố"):
        steps = main(st.session_state.puzzle)  # Giải đố
        steps = steps[1:]  # Loại bỏ bước đầu tiên
        st.session_state.steps = steps
        st.session_state.step_index = 0
        st.session_state.total_steps = len(steps)
        st.session_state.current_step = 1

    # Nút làm mới ma trận
    if st.button("Làm mới ma trận"):
        st.session_state.puzzle = generate_random_puzzle()  # Tạo ma trận ngẫu nhiên mới
        st.session_state.steps = []
        st.session_state.step_index = 0
        st.session_state.total_steps = 0
        st.session_state.current_step = 0

    # Hiển thị các bước
    if 'steps' in st.session_state and len(st.session_state.steps) > 0:
        step = st.session_state.steps[st.session_state.step_index]
        st.subheader(f"Bước hiện tại: {st.session_state.current_step}")
        st.write(f"Di chuyển: {step['dir']}")
        display_puzzle(step['node'])  # Hiển thị ma trận tại bước hiện tại

        # Các nút điều khiển bước
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Lùi lại") and st.session_state.step_index > 0:
                st.session_state.step_index -= 1
                st.session_state.current_step -= 1
        with col2:
            if st.button("Tiến lên") and st.session_state.step_index < st.session_state.total_steps - 1:
                st.session_state.step_index += 1
                st.session_state.current_step += 1

# Chạy ứng dụng Streamlit
if __name__ == "__main__":
    puzzle_gui()
