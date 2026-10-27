// Query options for every dash template:
//   ?h=234|240   frame height (default 234; 240 for dash part 006-B4160)
//   ?mode=day    day palette (default night)
//   ?chrome=0    hide what the dash draws on top (zoom buttons, road bar, speed sign)
//   ?guides=1    outline the zones where text must not go
(() => {
  const q = new URLSearchParams(location.search);
  const dash = document.querySelector(".dash");
  const h = q.get("h") === "240" ? 240 : 234;
  dash.style.setProperty("--h", `${h}px`);
  if (q.get("mode") === "day") dash.classList.add("day");

  if (q.get("chrome") !== "0") {
    const c = document.createElement("div");
    c.className = "chrome";
    c.setAttribute("aria-hidden", "true");
    c.innerHTML =
      '<svg viewBox="0 0 480 234"><g fill="#F4F4F4">' +
      '<path d="M29 68 L49 99.5 H9 Z" stroke="#F4F4F4" stroke-width="4" stroke-linejoin="round"/>' +
      '<path d="M9 116 H49 L29 147.5 Z" stroke="#F4F4F4" stroke-width="4" stroke-linejoin="round"/></g>' +
      '<g stroke="#1E1E1E" stroke-width="2.5" stroke-linecap="round"><path d="M22.5 87.5h13M29 81v13"/><path d="M22 127h14"/></g></svg>' +
      `<div class="bar">${dash.dataset.road || "Road"}</div>` +
      (dash.dataset.limit ? `<div class="sign">${dash.dataset.limit}</div>` : "");
    dash.appendChild(c);
  }
  if (q.get("guides") === "1") {
    const g = document.createElement("div");
    g.className = "guides";
    g.innerHTML = `<i style="left:0;top:68px;width:56px;height:100px"></i><i style="left:0;top:186px;width:480px;height:${h - 186}px"></i>`;
    dash.appendChild(g);
  }
})();
