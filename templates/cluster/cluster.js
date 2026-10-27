// The NMAX instrument cluster drawn around the TFT, so mockups and the demo look like the bike.
// Drawn from photos of an NMAX Turbo / Tech MAX cluster; no vendor artwork is used.
//
//   <script src="cluster/cluster.js"></script>, then
//   const c = mountCluster(document.querySelector("#here"));
//   c.frame            // the 480×234 element where your dash page goes (an <img>, <iframe> or <div>)
//   c.set({ speed: 32, clock: "14:42", odo: 2576, fuel: 4 })
//
// The cluster is 1000×640 CSS px; scale the container with a transform to fit.

(() => {
// Seven-segment digits on a 10×20 cell, slightly italic like the bike's LCD.
const T = 2.1; // segment thickness
const hseg = (x, y) => `M${x + 0.4} ${y}l${T / 2} ${-T / 2}h${7.2 - T}l${T / 2} ${T / 2}l${-T / 2} ${T / 2}h${-(7.2 - T)}z`;
const vseg = (x, y) => `M${x} ${y + 0.4}l${T / 2} ${T / 2}v${8.2 - T}l${-T / 2} ${T / 2}l${-T / 2} ${-T / 2}v${-(8.2 - T)}z`;
const SEG = {
  a: hseg(1, 1), g: hseg(1, 10), d: hseg(1, 19),
  f: vseg(1, 1), b: vseg(9, 1), e: vseg(1, 10), c: vseg(9, 10),
};
const DIGITS = {
  0: "abcdef", 1: "bc", 2: "abdeg", 3: "abcdg", 4: "bcfg", 5: "acdfg", 6: "acdefg", 7: "abc", 8: "abcdefg", 9: "abcdfg",
};

function segText(text, { x, y, h, gap = 0.35, on = "#d8d0f4", off = "rgba(216,208,244,0.045)", align = "right" }) {
  const k = h / 20, w = 10 * k, step = w * (1 + gap);
  const chars = String(text).split("");
  const total = chars.length * step - gap * w;
  let cx = align === "right" ? x - total : x;
  let out = "";
  for (const ch of chars) {
    const lit = DIGITS[ch] ?? "";
    out += `<g transform="translate(${cx.toFixed(1)} ${y}) scale(${k.toFixed(3)}) skewX(-5)">`;
    for (const seg of "abcdefg") out += `<path d="${SEG[seg]}" fill="${lit.includes(seg) ? on : off}"/>`;
    out += "</g>";
    cx += step;
  }
  return out;
}

const CSS = `
.cluster { position: relative; width: 1000px; height: 640px; font-family: -apple-system, "SF Pro Text", Inter, system-ui, sans-serif; }
.cluster > svg { position: absolute; inset: 0; width: 1000px; height: 640px; }
.cluster .tft { position: absolute; left: 260px; top: 240px; width: 480px; height: 268px; background: #000; overflow: hidden; }
.cluster .status { position: absolute; left: 0; right: 0; top: 0; height: 32px; display: flex; align-items: center; gap: 8px; padding: 0 12px; color: #fff; font-size: 22px; font-weight: 600; line-height: 1; font-variant-numeric: tabular-nums; border-bottom: 2px solid #e9e9e9; box-sizing: border-box; }
.cluster .status svg { width: 22px; height: 22px; }
.cluster .status .app { margin-left: 118px; font-size: 13px; font-weight: 600; line-height: 1; color: #111; background: #f2f2f2; border-radius: 3px; padding: 4px 5px; }
.cluster .status .t { margin-left: auto; width: 24px; height: 22px; border-radius: 3px; background: #19b6c9; color: #062c33; font-size: 16px; font-weight: 700; line-height: 22px; text-align: center; }
.cluster .frame { position: absolute; left: 0; top: 34px; width: 480px; height: 234px; overflow: hidden; background: #000; }
.cluster .frame > img, .cluster .frame > iframe { display: block; width: 480px; height: 234px; border: 0; }
.cluster .sign { position: absolute; left: 411px; top: 169px; width: 62px; height: 62px; box-sizing: border-box; border-radius: 50%; border: 6px solid #e0201b; background: #fff; color: #111; display: grid; place-items: center; font: 700 24px/1 -apple-system, "SF Pro Text", Inter, system-ui, sans-serif; z-index: 5; opacity: 0; transform: scale(.85); transition: opacity .3s ease, transform .3s ease; }
.cluster .sign.on { opacity: 1; transform: none; }
`;

const SVG = `
<svg viewBox="0 0 1000 640" aria-hidden="true">
  <defs>
    <linearGradient id="cl-glass" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0" stop-color="#17181b"/><stop offset="0.55" stop-color="#0c0d0f"/><stop offset="1" stop-color="#0a0a0c"/>
    </linearGradient>
    <linearGradient id="cl-shell" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2a2b2f"/><stop offset="1" stop-color="#1b1c1f"/>
    </linearGradient>
  </defs>
  <!-- shell -->
  <path d="M170 8H830Q872 8 898 40L986 170Q996 186 996 206V438Q996 456 986 470L896 612Q878 636 846 636H154Q122 636 104 612L14 470Q4 456 4 438V206Q4 186 14 170L102 40Q128 8 170 8Z" fill="url(#cl-shell)"/>
  <!-- glass -->
  <path d="M196 44H804Q826 44 840 62L940 196Q948 207 948 222V428Q948 440 941 450L858 576Q848 590 830 590H170Q152 590 142 576L59 450Q52 440 52 428V222Q52 207 60 196L160 62Q174 44 196 44Z" fill="url(#cl-glass)" stroke="#34363a" stroke-width="2"/>
  <path d="M200 50H800" stroke="rgba(255,255,255,0.10)" stroke-width="2" stroke-linecap="round"/>

  <!-- turn signals -->
  <path d="M190 72H300V176H160L136 152Z" fill="#141518" stroke="#2b2d31" stroke-width="2" stroke-linejoin="round"/>
  <path id="cl-left" d="M248 106V96L218 124L248 152V142H272V106Z" fill="#1d2620"/>
  <path d="M810 72H700V176H840L864 152Z" fill="#141518" stroke="#2b2d31" stroke-width="2" stroke-linejoin="round"/>
  <path id="cl-right" d="M752 106V96L782 124L752 152V142H728V106Z" fill="#1d2620"/>

  <!-- LCD -->
  <rect x="320" y="64" width="360" height="156" rx="8" fill="#07080a" stroke="#24262a" stroke-width="2"/>
  <g id="cl-speed"></g>
  <text x="478" y="196" font-size="15" fill="#d8d0f4" font-family="inherit">km/h</text>
  <g fill="none" stroke="#d8d0f4" stroke-width="2.5">
    <rect x="510" y="84" width="152" height="42" rx="5"/>
  </g>
  <g id="cl-fuel"></g>
  <text x="518" y="112" font-size="16" font-weight="700" fill="#07080a" font-family="inherit">E</text>
  <text x="646" y="112" font-size="16" font-weight="700" fill="#d8d0f4" font-family="inherit">F</text>
  <path d="M552 98h10v18h-10zM562 104h4v8" fill="none" stroke="#07080a" stroke-width="2"/>
  <path d="M510 136H662" stroke="#d8d0f4" stroke-width="2.5"/>
  <text x="512" y="158" font-size="13" font-weight="600" fill="#d8d0f4" letter-spacing="1.5" font-family="inherit">ODO</text>
  <g id="cl-odo"></g>
  <text x="644" y="194" font-size="13" fill="#d8d0f4" font-family="inherit">km</text>

  <!-- left tell-tales -->
  <path d="M86 230H228V520H140L92 456Z" fill="#101114" stroke="#222428" stroke-width="2" stroke-linejoin="round"/>
  <circle cx="126" cy="318" r="12" fill="#2a2b2f"/>
  <text x="162" y="300" font-size="26" font-weight="600" fill="#3d3f44" font-family="inherit">TCS</text>
  <g fill="none" stroke="#3d3f44" stroke-width="3" stroke-linecap="round"><path d="M170 376h18M178 368v16M196 360a14 14 0 0 1 0 22M204 354a22 22 0 0 1 0 34"/></g>
  <text x="160" y="460" font-size="26" font-weight="600" fill="#3d3f44" font-family="inherit">CVT</text>
  <!-- right tell-tales -->
  <path d="M914 230H772V520H860L908 456Z" fill="#101114" stroke="#222428" stroke-width="2" stroke-linejoin="round"/>
  <g fill="none" stroke="#3d3f44" stroke-width="3" stroke-linejoin="round"><path d="M806 276h40v8h8v20h-8v8h-40l-6-8v-20z"/></g>
  <g fill="none" stroke="#3d3f44" stroke-width="3" stroke-linecap="round"><path d="M828 336v26M820 348h16M806 372q8 6 16 0t16 0t16 0"/></g>
  <circle cx="830" cy="420" r="20" fill="none" stroke="#ff9a1f" stroke-width="3"/>
  <text x="830" y="427" text-anchor="middle" font-size="16" font-weight="800" fill="#ff9a1f" font-family="inherit">ABS</text>
  <circle cx="830" cy="480" r="18" fill="none" stroke="#3d3f44" stroke-width="3"/>
  <text x="830" y="487" text-anchor="middle" font-size="20" font-weight="700" fill="#3d3f44" font-family="inherit">A</text>

  <!-- TFT bezel -->
  <rect x="250" y="230" width="500" height="288" rx="6" fill="#050506" stroke="#2a2c30" stroke-width="2"/>
</svg>`;

let styled = false;

function mountCluster(host) {
  if (!styled) {
    const s = document.createElement("style");
    s.textContent = CSS;
    document.head.appendChild(s);
    styled = true;
  }
  const root = document.createElement("div");
  root.className = "cluster";
  root.innerHTML =
    SVG +
    `<div class="tft"><div class="status"><span class="clock">14:42</span>` +
    `<svg viewBox="0 0 22 22" fill="none" stroke="#fff" stroke-width="1.8" stroke-linejoin="round"><path d="M3 6l5-2 6 2 5-2v12l-5 2-6-2-5 2z M8 4v12 M14 6v12"/></svg>` +
    `<span class="app">App</span><span class="t">T</span></div><div class="frame"></div><div class="sign"></div></div>`;
  host.appendChild(root);
  const $ = (id) => root.querySelector(id);

  function set({ speed, clock, odo, fuel } = {}) {
    if (speed !== undefined) $("#cl-speed").innerHTML = segText(Math.round(speed), { x: 470, y: 84, h: 104, gap: 0.3 });
    if (odo !== undefined) $("#cl-odo").innerHTML = segText(Math.round(odo), { x: 640, y: 166, h: 28, gap: 0.4 });
    if (fuel !== undefined) {
      let cells = "";
      for (let i = 0; i < 5; i++) {
        cells += `<rect x="${514 + i * 29.6}" y="88" width="26" height="34" rx="2" fill="${i < fuel ? "#d8d0f4" : "rgba(216,208,244,0.08)"}"/>`;
      }
      $("#cl-fuel").innerHTML = cells;
    }
    if (clock !== undefined) $(".clock").textContent = clock;
  }
  set({ speed: 0, odo: 2576, fuel: 4 });
  // The dash's own speed-limit sign (cmd 17): drawn by the dash over the frame, centre (442, 166), radius 31.
  function sign(kmh) {
    const el = $(".sign");
    if (kmh) el.textContent = kmh;
    el.classList.toggle("on", !!kmh);
  }
  return { root, frame: $(".frame"), set, sign, signal: (side, on) => ($(side === "left" ? "#cl-left" : "#cl-right").style.fill = on ? "#3ddc6a" : "#1d2620") };
}

window.mountCluster = mountCluster;
})();
