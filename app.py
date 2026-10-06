import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Rắn Săn Mồi", page_icon="🐍", layout="centered")

# Nền tối + bớt khoảng trống mặc định của Streamlit
st.markdown(
    """
    <style>
    .stApp {background: radial-gradient(circle at top, #1b2740 0%, #0b1020 70%);}
    header[data-testid="stHeader"] {background: transparent;}
    .block-container {padding-top: 1rem; padding-bottom: 1rem; max-width: 540px;}
    h1, p, li, summary, span, label {color: #e8eefc !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

GAME_HTML = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
  * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
  html, body { margin: 0; background: transparent; color: #fff;
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
  #app { max-width: 480px; margin: 0 auto; padding: 6px;
    user-select: none; -webkit-user-select: none; outline: none; }
  #hud { display: flex; gap: 8px; align-items: stretch; margin-bottom: 8px; }
  .chip { flex: 1; background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.12);
    border-radius: 12px; padding: 6px 4px; text-align: center; font-size: 11px; color: #9fb3c8; }
  .chip b { display: block; font-size: 18px; color: #fff; }
  #pauseBtn { width: 52px; border: 1px solid rgba(255,255,255,.15); border-radius: 12px;
    background: rgba(255,255,255,.1); color: #fff; font-size: 20px; cursor: pointer; }
  #stage { position: relative; width: 100%; aspect-ratio: 1 / 1; border-radius: 16px; overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,.5); border: 2px solid rgba(255,255,255,.14); touch-action: none; }
  canvas { width: 100%; height: 100%; display: block; }
  #overlay { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
    background: rgba(8,13,26,.82); backdrop-filter: blur(3px); padding: 14px; overflow-y: auto; }
  #overlay.hidden { display: none; }
  .panel { width: 100%; text-align: center; margin: auto; }
  .panel h1 { font-size: 30px; margin: 0 0 4px; }
  .sub { color: #9fb3c8; font-size: 13px; margin: 6px 0; }
  .big { font-size: 40px; font-weight: 800; margin: 4px 0; }
  .btn { display: block; width: 100%; padding: 12px; margin: 8px 0; border: 0; border-radius: 12px;
    font-size: 16px; font-weight: 700; color: #06311f; cursor: pointer;
    background: linear-gradient(135deg, #43e97b, #38f9d7); }
  .btn.sec { background: rgba(255,255,255,.14); color: #fff; }
  .diff { display: flex; gap: 6px; margin-bottom: 6px; }
  .diff button { flex: 1; padding: 9px 4px; border-radius: 10px; border: 1px solid rgba(255,255,255,.25);
    background: transparent; color: #fff; cursor: pointer; font-weight: 600; font-size: 14px; }
  .diff button.on { background: #43e97b; color: #06311f; border-color: #43e97b; }
  .help { text-align: left; font-size: 13.5px; line-height: 1.5; color: #dce6f7; }
  .help h3 { margin: 10px 0 4px; font-size: 15px; color: #43e97b; }
  .help ul { margin: 0; padding-left: 18px; }
  .foods { font-size: 24px; letter-spacing: 3px; text-align: center; margin: 6px 0; }
  kbd { background: rgba(255,255,255,.15); border-radius: 5px; padding: 1px 6px; font-size: 12px; }
  #dpad { display: none; grid-template-columns: repeat(3, 62px); grid-template-rows: repeat(2, 56px);
    gap: 8px; justify-content: center; margin: 14px auto 4px; }
  #dpad button { border: 1px solid rgba(255,255,255,.18); border-radius: 16px; font-size: 24px; color: #fff;
    background: rgba(255,255,255,.1); touch-action: manipulation; }
  #dpad button:active { background: rgba(67,233,123,.35); }
  #dpad .up { grid-column: 2; grid-row: 1; }
  #dpad .left { grid-column: 1; grid-row: 2; }
  #dpad .down { grid-column: 2; grid-row: 2; }
  #dpad .right { grid-column: 3; grid-row: 2; }
  @media (pointer: coarse), (max-width: 700px) { #dpad { display: grid; } }
</style>
</head>
<body>
<div id="app" tabindex="0">
  <div id="hud">
    <div class="chip">ĐIỂM<b id="score">0</b></div>
    <div class="chip">KỶ LỤC<b id="best">0</b></div>
    <div class="chip">CẤP<b id="level">1</b></div>
    <button id="pauseBtn" title="Tạm dừng">⏸</button>
  </div>
  <div id="stage">
    <canvas id="cv"></canvas>
    <div id="overlay"></div>
  </div>
  <div id="dpad">
    <button class="up" data-d="U">▲</button>
    <button class="left" data-d="L">◀</button>
    <button class="down" data-d="D">▼</button>
    <button class="right" data-d="R">▶</button>
  </div>
</div>

<script>
(() => {
  const GRID = 17;
  const FOODS = ["🍎","🍌","🍇","🍓","🍕","🍔","🍩","🍉","🍒","🍪","🍗","🥕","🍰","🍍","🌭","🍟"];
  const EMOJI_FONT = '"Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",sans-serif';
  const DIFF = {
    easy:   { name: "Dễ",   base: 170 },
    normal: { name: "Vừa",  base: 130 },
    hard:   { name: "Khó",  base: 95 }
  };
  const $ = id => document.getElementById(id);
  const cv = $("cv"), ctx = cv.getContext("2d"), stage = $("stage"), overlay = $("overlay");

  let cell = 20;
  let snake, prev, dir, queue, food, score, level, tickMs;
  let state = "menu";            // menu | playing | paused | over
  let difficulty = "normal";
  let lastTick = 0, progress = 1;
  let particles = [];
  let best = 0;
  try { best = parseInt(localStorage.getItem("snake_best") || "0", 10) || 0; } catch (e) {}

  // ---------- Khởi tạo ----------
  function resize() {
    const dpr = window.devicePixelRatio || 1;
    const w = stage.clientWidth;
    cv.width = Math.round(w * dpr);
    cv.height = Math.round(w * dpr);
    cell = cv.width / GRID;
  }
  new ResizeObserver(resize).observe(stage);

  function baseSpeed() { return DIFF[difficulty].base; }

  function reset() {
    const m = Math.floor(GRID / 2);
    snake = [{x: m, y: m}, {x: m - 1, y: m}, {x: m - 2, y: m}];
    prev = snake.map(s => ({...s}));
    dir = {x: 1, y: 0};
    queue = [];
    score = 0; level = 1; tickMs = baseSpeed();
    particles = [];
    progress = 1;
    spawnFood();
    updateHud();
  }

  function spawnFood() {
    const used = new Set(snake.map(s => s.x + "," + s.y));
    const free = [];
    for (let x = 0; x < GRID; x++)
      for (let y = 0; y < GRID; y++)
        if (!used.has(x + "," + y)) free.push({x, y});
    if (!free.length) { food = null; return; }
    const p = free[Math.floor(Math.random() * free.length)];
    let e;
    do { e = FOODS[Math.floor(Math.random() * FOODS.length)]; } while (food && e === food.e);
    food = {x: p.x, y: p.y, e};
  }

  function updateHud() {
    $("score").textContent = score;
    $("best").textContent = best;
    $("level").textContent = level;
  }

  // ---------- Logic ----------
  function tick() {
    if (queue.length) dir = queue.shift();
    const head = {x: snake[0].x + dir.x, y: snake[0].y + dir.y};
    const hitWall = head.x < 0 || head.y < 0 || head.x >= GRID || head.y >= GRID;
    const body = snake.slice(0, -1);
    const hitSelf = body.some(s => s.x === head.x && s.y === head.y);
    if (hitWall || hitSelf) { gameOver(); return; }

    prev = snake.map(s => ({...s}));
    snake.unshift(head);
    if (food && head.x === food.x && head.y === food.y) {
      score += 10;
      burst(food.x, food.y);
      level = 1 + Math.floor(score / 50);
      tickMs = Math.max(60, baseSpeed() - (level - 1) * 8);
      if (score > best) {
        best = score;
        try { localStorage.setItem("snake_best", String(best)); } catch (e) {}
      }
      spawnFood();
      updateHud();
      if (!food) { gameOver(true); }
    } else {
      snake.pop();
    }
  }

  function gameOver(won) {
    state = "over";
    progress = 1;
    setTimeout(() => showPanel("over", won), 450);
  }

  function setDir(dx, dy) {
    if (state !== "playing") return;
    const last = queue.length ? queue[queue.length - 1] : dir;
    if ((dx === last.x && dy === last.y) || (dx === -last.x && dy === -last.y)) return;
    if (queue.length < 2) queue.push({x: dx, y: dy});
  }

  function burst(gx, gy) {
    for (let i = 0; i < 14; i++) {
      const a = Math.random() * Math.PI * 2, sp = (0.5 + Math.random() * 2) * (cell / 14);
      particles.push({x: (gx + .5) * cell, y: (gy + .5) * cell, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp,
        life: 1, c: ["#ffd54f", "#ff8a65", "#81d4fa", "#a5d6a7"][i % 4]});
    }
  }

  // ---------- Vẽ ----------
  function drawBoard() {
    for (let x = 0; x < GRID; x++)
      for (let y = 0; y < GRID; y++) {
        ctx.fillStyle = (x + y) % 2 === 0 ? "#1a2a3d" : "#1e3045";
        ctx.fillRect(x * cell, y * cell, cell + 1, cell + 1);
      }
  }

  function drawFood(ts) {
    if (!food) return;
    const cx = (food.x + .5) * cell, cy = (food.y + .5) * cell;
    const pulse = 1 + 0.08 * Math.sin(ts / 220);
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, cell * .75);
    g.addColorStop(0, "rgba(255,230,120,.35)");
    g.addColorStop(1, "rgba(255,230,120,0)");
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.arc(cx, cy, cell * .75, 0, 7); ctx.fill();
    ctx.font = `${cell * 0.78 * pulse}px ${EMOJI_FONT}`;
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillText(food.e, cx, cy + cell * 0.04);
  }

  function lerpPts(t) {
    return snake.map((s, i) => {
      const p = prev[Math.min(i, prev.length - 1)];
      return {x: (p.x + (s.x - p.x) * t + .5) * cell, y: (p.y + (s.y - p.y) * t + .5) * cell};
    });
  }

  function drawSnake(t, ts) {
    const pts = lerpPts(t), n = pts.length;
    const dead = state === "over";
    // Thân: các hình tròn nối nhau, thon dần về đuôi, có hoa văn sọc
    for (let i = n - 1; i >= 1; i--) {
      const a = pts[i], b = pts[i - 1];
      const steps = 6;
      for (let k = 0; k < steps; k++) {
        const f = k / steps;
        const x = a.x + (b.x - a.x) * f, y = a.y + (b.y - a.y) * f;
        const pos = (n - 1 - i) + f;                   // 0 = đuôi
        const u = pos / (n - 1);
        const r = cell * (0.26 + 0.19 * Math.min(1, u * 1.4));
        const stripe = Math.floor(pos * 1.6) % 2 === 0;
        ctx.fillStyle = dead ? (stripe ? "#8a9aa8" : "#76858f") : (stripe ? "#2ecc71" : "#1fa85a");
        ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fill();
        ctx.fillStyle = "rgba(255,255,255,.14)";
        ctx.beginPath(); ctx.arc(x, y - r * .3, r * .5, 0, 7); ctx.fill();
      }
    }
    // Đầu
    const H = pts[0];
    let hx = H.x - pts[1].x, hy = H.y - pts[1].y;
    let len = Math.hypot(hx, hy);
    if (len < 0.001) { hx = dir.x; hy = dir.y; len = 1; }
    const nx = hx / len, ny = hy / len, px = -ny, py = nx;

    // Lưỡi
    if (!dead && (ts % 1500) < 320) {
      ctx.strokeStyle = "#ff4d6d"; ctx.lineWidth = cell * .07; ctx.lineCap = "round";
      const sx = H.x + nx * cell * .45, sy = H.y + ny * cell * .45;
      const ex = H.x + nx * cell * .85, ey = H.y + ny * cell * .85;
      ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(ex, ey);
      ctx.moveTo(ex, ey); ctx.lineTo(ex + (nx + px) * cell * .12, ey + (ny + py) * cell * .12);
      ctx.moveTo(ex, ey); ctx.lineTo(ex + (nx - px) * cell * .12, ey + (ny - py) * cell * .12);
      ctx.stroke();
    }
    ctx.fillStyle = dead ? "#9aa8b4" : "#43e97b";
    ctx.beginPath(); ctx.ellipse(H.x, H.y, cell * .5, cell * .45, Math.atan2(ny, nx), 0, 7); ctx.fill();
    ctx.fillStyle = "rgba(255,255,255,.18)";
    ctx.beginPath(); ctx.arc(H.x - nx * cell * .05, H.y - cell * .12, cell * .26, 0, 7); ctx.fill();

    // Mắt
    for (const s of [-1, 1]) {
      const ex = H.x + nx * cell * .12 + px * s * cell * .22;
      const ey = H.y + ny * cell * .12 + py * s * cell * .22;
      ctx.fillStyle = "#fff";
      ctx.beginPath(); ctx.arc(ex, ey, cell * .16, 0, 7); ctx.fill();
      ctx.fillStyle = "#111";
      if (dead) {
        ctx.strokeStyle = "#111"; ctx.lineWidth = cell * .05;
        ctx.beginPath();
        ctx.moveTo(ex - cell * .07, ey - cell * .07); ctx.lineTo(ex + cell * .07, ey + cell * .07);
        ctx.moveTo(ex + cell * .07, ey - cell * .07); ctx.lineTo(ex - cell * .07, ey + cell * .07);
        ctx.stroke();
      } else {
        ctx.beginPath(); ctx.arc(ex + nx * cell * .05, ey + ny * cell * .05, cell * .08, 0, 7); ctx.fill();
      }
    }
  }

  function drawParticles() {
    particles = particles.filter(p => p.life > 0);
    for (const p of particles) {
      p.x += p.vx; p.y += p.vy; p.life -= 0.035;
      ctx.globalAlpha = Math.max(0, p.life);
      ctx.fillStyle = p.c;
      ctx.beginPath(); ctx.arc(p.x, p.y, cell * .1, 0, 7); ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  function loop(ts) {
    if (state === "playing") {
      if (ts - lastTick >= tickMs) { tick(); lastTick = ts; }
      if (state === "playing") progress = Math.min(1, (ts - lastTick) / tickMs);
    }
    ctx.clearRect(0, 0, cv.width, cv.height);
    drawBoard();
    drawFood(ts);
    drawSnake(progress, ts);
    drawParticles();
    requestAnimationFrame(loop);
  }

  // ---------- Menu / bảng thông tin ----------
  const PANELS = {
    menu: () => `
      <div class="panel">
        <h1>🐍 Rắn Săn Mồi</h1>
        <div class="sub">Ăn thật nhiều đồ ngon để lớn thật dài!</div>
        <div class="foods">🍎🍕🍩🍉🍔</div>
        <div class="sub">Độ khó</div>
        <div class="diff">${Object.entries(DIFF).map(([k, v]) =>
          `<button data-act="diff" data-v="${k}" class="${k === difficulty ? "on" : ""}">${v.name}</button>`).join("")}</div>
        <button class="btn" data-act="start">▶ Bắt đầu chơi</button>
        <button class="btn sec" data-act="help">❓ Hướng dẫn</button>
        <div class="sub">🏆 Kỷ lục: ${best}</div>
      </div>`,
    help: () => `
      <div class="panel help">
        <h1 style="text-align:center;font-size:22px">❓ Hướng dẫn</h1>
        <h3>🎯 Mục tiêu</h3>
        <ul><li>Điều khiển rắn ăn đồ ăn để ghi điểm (+10 mỗi món) và dài ra.</li>
            <li>Cứ 50 điểm lên 1 cấp, rắn chạy nhanh hơn.</li></ul>
        <h3>⌨️ Máy tính</h3>
        <ul><li>Di chuyển: <kbd>↑</kbd> <kbd>↓</kbd> <kbd>←</kbd> <kbd>→</kbd> hoặc <kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd></li>
            <li>Tạm dừng / tiếp tục: <kbd>Space</kbd> hoặc <kbd>P</kbd></li></ul>
        <h3>📱 Điện thoại</h3>
        <ul><li>Vuốt trên bảng chơi theo hướng muốn rẽ.</li>
            <li>Hoặc bấm các nút mũi tên bên dưới.</li></ul>
        <h3>☠️ Thua khi</h3>
        <ul><li>Đâm vào tường hoặc cắn vào thân mình.</li></ul>
        <div class="foods">🍌🍇🍓🍒🍪🍗🥕🍰🍍🌭🍟</div>
        <button class="btn" data-act="menu">← Quay lại</button>
      </div>`,
    paused: () => `
      <div class="panel">
        <h1>⏸ Tạm dừng</h1>
        <button class="btn" data-act="resume">▶ Tiếp tục</button>
        <button class="btn sec" data-act="start">🔄 Chơi lại</button>
        <button class="btn sec" data-act="help2">❓ Hướng dẫn</button>
        <button class="btn sec" data-act="menu">🏠 Menu chính</button>
      </div>`,
    over: (won) => `
      <div class="panel">
        <h1>${won ? "🏆 Bạn thắng!" : "💀 Game Over"}</h1>
        <div class="sub">Điểm của bạn</div>
        <div class="big">${score}</div>
        <div class="sub">🏆 Kỷ lục: ${best}</div>
        <button class="btn" data-act="start">🔄 Chơi lại</button>
        <button class="btn sec" data-act="menu">🏠 Menu chính</button>
      </div>`
  };

  function showPanel(name, arg) {
    overlay.innerHTML = PANELS[name](arg);
    overlay.classList.remove("hidden");
  }
  function hidePanel() { overlay.classList.add("hidden"); }

  function startGame() {
    reset();
    state = "playing";
    lastTick = performance.now();
    hidePanel();
    $("app").focus();
  }
  function pauseToggle() {
    if (state === "playing") { state = "paused"; showPanel("paused"); }
    else if (state === "paused") resumeGame();
  }
  function resumeGame() {
    state = "playing";
    lastTick = performance.now() - progress * tickMs;
    hidePanel();
    $("app").focus();
  }

  overlay.addEventListener("click", e => {
    const b = e.target.closest("[data-act]");
    if (!b) return;
    const act = b.dataset.act;
    if (act === "start") startGame();
    else if (act === "resume") resumeGame();
    else if (act === "help") showPanel("help");
    else if (act === "help2") showPanel("help");
    else if (act === "menu") {
      if (state === "paused" || state === "over") { state = "menu"; reset(); }
      showPanel("menu");
    }
    else if (act === "diff") { difficulty = b.dataset.v; showPanel("menu"); }
  });
  $("pauseBtn").addEventListener("click", pauseToggle);

  // ---------- Điều khiển ----------
  const KEYS = {
    ArrowUp: [0, -1], w: [0, -1], W: [0, -1],
    ArrowDown: [0, 1], s: [0, 1], S: [0, 1],
    ArrowLeft: [-1, 0], a: [-1, 0], A: [-1, 0],
    ArrowRight: [1, 0], d: [1, 0], D: [1, 0]
  };
  window.addEventListener("keydown", e => {
    if (KEYS[e.key]) { e.preventDefault(); setDir(...KEYS[e.key]); }
    else if (e.key === " " || e.key === "p" || e.key === "P") { e.preventDefault(); pauseToggle(); }
    else if (e.key === "Enter" && (state === "menu" || state === "over")) { e.preventDefault(); startGame(); }
  });

  document.querySelectorAll("#dpad button").forEach(b => {
    b.addEventListener("pointerdown", e => {
      e.preventDefault();
      const v = {U: [0, -1], D: [0, 1], L: [-1, 0], R: [1, 0]}[b.dataset.d];
      setDir(...v);
    });
  });

  // Vuốt trên bảng chơi
  let tx = 0, ty = 0, touching = false;
  stage.addEventListener("touchstart", e => {
    if (state !== "playing") return;
    const t = e.touches[0]; tx = t.clientX; ty = t.clientY; touching = true;
  }, {passive: true});
  stage.addEventListener("touchmove", e => {
    if (!touching) return;
    e.preventDefault();
    const t = e.touches[0];
    const dx = t.clientX - tx, dy = t.clientY - ty;
    if (Math.max(Math.abs(dx), Math.abs(dy)) > 22) {
      if (Math.abs(dx) > Math.abs(dy)) setDir(dx > 0 ? 1 : -1, 0);
      else setDir(0, dy > 0 ? 1 : -1);
      tx = t.clientX; ty = t.clientY;
    }
  }, {passive: false});
  stage.addEventListener("touchend", () => { touching = false; }, {passive: true});

  // ---------- Chạy ----------
  resize();
  reset();
  showPanel("menu");
  requestAnimationFrame(loop);
})();
</script>
</body>
</html>
"""

st.title("🐍 Rắn Săn Mồi")
components.html(GAME_HTML, height=780, scrolling=False)

with st.expander("📖 Hướng dẫn nhanh"):
    st.markdown(
        """
- **Máy tính:** phím mũi tên hoặc `W A S D` để di chuyển, `Space` / `P` để tạm dừng.
- **Điện thoại:** vuốt trên bảng chơi hoặc bấm các nút mũi tên.
- Ăn đồ ăn (🍎🍕🍩…) để ghi điểm và dài ra. Đâm tường hoặc cắn thân mình là thua.
- Mỗi 50 điểm lên 1 cấp, rắn chạy nhanh hơn.
        """
    )
