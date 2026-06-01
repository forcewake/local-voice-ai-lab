const canvas = document.querySelector("#signal-canvas");
const context = canvas.getContext("2d");
let width = 0;
let height = 0;
let phase = 0;
let running = true;

const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

function resize() {
  const ratio = Math.min(window.devicePixelRatio || 1, 2);
  width = window.innerWidth;
  height = window.innerHeight;
  canvas.width = Math.floor(width * ratio);
  canvas.height = Math.floor(height * ratio);
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
}

function drawGrid() {
  context.strokeStyle = "rgba(190, 231, 220, 0.06)";
  context.lineWidth = 1;
  const step = 58;
  for (let x = 0; x < width; x += step) {
    context.beginPath();
    context.moveTo(x, 0);
    context.lineTo(x, height);
    context.stroke();
  }
  for (let y = 0; y < height; y += step) {
    context.beginPath();
    context.moveTo(0, y);
    context.lineTo(width, y);
    context.stroke();
  }
}

function drawSpectrogram() {
  const baseY = height * 0.45;
  const rows = 30;
  const columns = 84;
  const cellW = width / columns;
  for (let row = 0; row < rows; row += 1) {
    for (let col = 0; col < columns; col += 1) {
      const wave = Math.sin(col * 0.22 + phase) + Math.cos(row * 0.6 - phase * 0.7);
      const pulse = Math.max(0, wave * 0.5 + 0.5);
      const alpha = 0.035 + pulse * 0.12;
      const hue = row % 5 === 0 ? "245, 189, 78" : "78, 230, 195";
      context.fillStyle = `rgba(${hue}, ${alpha})`;
      context.fillRect(col * cellW, baseY + row * 9, cellW * 0.72, 3);
    }
  }
}

function drawWaveform() {
  const mid = height * 0.42;
  const amplitude = Math.min(138, height * 0.18);
  context.lineWidth = 2;
  context.strokeStyle = "rgba(158, 245, 111, 0.7)";
  context.beginPath();
  for (let x = -20; x <= width + 20; x += 8) {
    const y =
      mid +
      Math.sin(x * 0.012 + phase) * amplitude * 0.44 +
      Math.sin(x * 0.027 - phase * 1.5) * amplitude * 0.18 +
      Math.cos(x * 0.006 + phase * 0.8) * amplitude * 0.16;
    if (x === -20) {
      context.moveTo(x, y);
    } else {
      context.lineTo(x, y);
    }
  }
  context.stroke();

  context.lineWidth = 1;
  context.strokeStyle = "rgba(78, 230, 195, 0.38)";
  context.beginPath();
  for (let x = -20; x <= width + 20; x += 10) {
    const y = mid + 56 + Math.cos(x * 0.015 - phase * 1.2) * amplitude * 0.24;
    if (x === -20) {
      context.moveTo(x, y);
    } else {
      context.lineTo(x, y);
    }
  }
  context.stroke();
}

function draw() {
  context.clearRect(0, 0, width, height);
  drawGrid();
  drawSpectrogram();
  drawWaveform();
  phase += prefersReducedMotion.matches ? 0 : 0.012;
  if (running) {
    requestAnimationFrame(draw);
  }
}

window.addEventListener("resize", resize);
document.addEventListener("visibilitychange", () => {
  running = !document.hidden;
  if (running) {
    draw();
  }
});

resize();
draw();

document.querySelectorAll("[data-copy]").forEach((button) => {
  button.addEventListener("click", async () => {
    const text = button.getAttribute("data-copy");
    try {
      await navigator.clipboard.writeText(text);
      const original = button.querySelector("span").textContent;
      button.querySelector("span").textContent = "Copied command";
      window.setTimeout(() => {
        button.querySelector("span").textContent = original;
      }, 1200);
    } catch {
      button.querySelector("code").focus();
    }
  });
});
