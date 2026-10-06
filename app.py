import random

import streamlit as st

# ---------- Cấu hình ----------
GRID = 15          # lưới GRID x GRID
SPEED = 0.25       # giây giữa mỗi bước
DIRS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}
OPPOSITE = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}

st.set_page_config(page_title="Rắn săn mồi", page_icon="🐍", layout="centered")


# ---------- Logic game ----------
def spawn_food(snake):
    free = [(x, y) for x in range(GRID) for y in range(GRID) if (x, y) not in snake]
    return random.choice(free) if free else None


def new_game():
    mid = GRID // 2
    snake = [(mid, mid), (mid - 1, mid), (mid - 2, mid)]
    st.session_state.snake = snake
    st.session_state.direction = "RIGHT"
    st.session_state.moved_dir = "RIGHT"
    st.session_state.food = spawn_food(snake)
    st.session_state.score = 0
    st.session_state.running = False
    st.session_state.game_over = False


def set_direction(d):
    # Không cho quay đầu 180 độ
    if d != OPPOSITE[st.session_state.moved_dir]:
        st.session_state.direction = d


def toggle_run():
    if not st.session_state.game_over:
        st.session_state.running = not st.session_state.running


def step():
    ss = st.session_state
    dx, dy = DIRS[ss.direction]
    hx, hy = ss.snake[0]
    head = (hx + dx, hy + dy)
    ss.moved_dir = ss.direction

    # Đâm tường hoặc cắn thân
    body = ss.snake[:-1]  # đuôi sẽ di chuyển nên không tính
    if not (0 <= head[0] < GRID and 0 <= head[1] < GRID) or head in body:
        ss.game_over = True
        ss.running = False
        return

    ss.snake.insert(0, head)
    if head == ss.food:
        ss.score += 10
        ss.food = spawn_food(ss.snake)
        if ss.food is None:  # thắng game
            ss.game_over = True
            ss.running = False
    else:
        ss.snake.pop()


def render_board():
    ss = st.session_state
    snake_set = set(ss.snake)
    head = ss.snake[0]
    cells = []
    for y in range(GRID):
        for x in range(GRID):
            if (x, y) == head:
                color = "#00c853"
            elif (x, y) in snake_set:
                color = "#69f0ae"
            elif (x, y) == ss.food:
                color = "#ff5252"
            else:
                color = "#263238" if (x + y) % 2 == 0 else "#2d3b42"
            cells.append(f'<div style="background:{color};border-radius:3px"></div>')
    html = (
        f'<div style="display:grid;grid-template-columns:repeat({GRID},1fr);'
        f'gap:1px;aspect-ratio:1/1;max-width:420px;margin:auto;'
        f'padding:4px;background:#111;border-radius:8px">{"".join(cells)}</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ---------- Khởi tạo ----------
if "snake" not in st.session_state:
    new_game()


# ---------- Vùng game: tự làm mới theo chu kỳ ----------
def game_area():
    ss = st.session_state
    if ss.running and not ss.game_over:
        step()
        if ss.game_over:
            st.rerun()  # rerun toàn app để dừng vòng lặp tự làm mới

    st.markdown(f"### Điểm: {ss.score}")
    render_board()

    if ss.game_over:
        st.error(f"Game over! Điểm của bạn: {ss.score}")

    # Nút điều khiển hướng
    _, c, _ = st.columns([1, 1, 1])
    c.button("⬆️", key="up", on_click=set_direction, args=("UP",), use_container_width=True)
    l, d, r = st.columns(3)
    l.button("⬅️", key="left", on_click=set_direction, args=("LEFT",), use_container_width=True)
    d.button("⬇️", key="down", on_click=set_direction, args=("DOWN",), use_container_width=True)
    r.button("➡️", key="right", on_click=set_direction, args=("RIGHT",), use_container_width=True)


st.title("🐍 Rắn săn mồi")

b1, b2 = st.columns(2)
b1.button(
    "⏸️ Tạm dừng" if st.session_state.running else "▶️ Bắt đầu",
    on_click=toggle_run,
    disabled=st.session_state.game_over,
    use_container_width=True,
)
b2.button("🔄 Chơi lại", on_click=new_game, use_container_width=True)

run_every = SPEED if (st.session_state.running and not st.session_state.game_over) else None
st.fragment(run_every=run_every)(game_area)()

st.caption("Ăn mồi đỏ 🔴 để ghi điểm. Đừng đâm tường hoặc cắn vào thân mình!")
