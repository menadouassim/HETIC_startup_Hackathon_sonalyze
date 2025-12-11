

/* ---------------------------
   Config
   --------------------------- */
const API_BASE = "http://127.0.0.1:5000";
const GRID = 20;                // grid size for grid snapping (user selected B)
const MAGNETIC_DIST = 16;       // distance to magnetically snap to other rooms
const MIN_W = 40, MIN_H = 30;   // minimum room size
const roomCounters = {
    Bedroom: 0,
    Bathroom: 0,
    Kitchen: 0,
    LivingRoom: 0,
    Toilet: 0,
    Office: 0,
    Custom: 0
};

/* ---------------------------
   Helpers
   --------------------------- */
function qs(sel, root=document) { return root.querySelector(sel); }
function qsa(sel, root=document) { return [...root.querySelectorAll(sel)]; }
function create(tag, props={}) {
  const el = document.createElement(tag);
  Object.assign(el, props);
  return el;
}
function px(v) { return v + "px"; }
function toInt(v) { return parseInt(v || 0, 10); }

/* Get numeric rect relative to canvas (top/left are px strings) */
function getRect(el) {
  return {
    x: toInt(el.style.left || 0),
    y: toInt(el.style.top || 0),
    w: toInt(el.style.width || el.offsetWidth),
    h: toInt(el.style.height || el.offsetHeight),
    el
  };
}

/* Axis-aligned rectangle collision test */
function isColliding(a, b) {
  return !(
    a.x + a.w <= b.x ||
    a.x >= b.x + b.w ||
    a.y + a.h <= b.y ||
    a.y >= b.y + b.h
  );
}

/* Snap number to grid */
function snapToGrid(n) {
  return Math.round(n / GRID) * GRID;
}

/* Constrain within canvas area */
function clampToCanvas(rect, canvasEl) {
  const maxW = Math.max(rect.w, 0);
  const maxH = Math.max(rect.h, 0);
  const maxX = Math.max(0, canvasEl.clientWidth - maxW - 6);
  const maxY = Math.max(0, canvasEl.clientHeight - maxH - 6);
  rect.x = Math.max(0, Math.min(rect.x, maxX));
  rect.y = Math.max(0, Math.min(rect.y, maxY));
  return rect;
}

/* ---------------------------
   App state
   --------------------------- */
const canvas = qs("#canvas");
let locked = false;
let roomCounter = 1;
let dragging = null;    // {el, startMouseX, startMouseY, startX, startY}
let resizing = null;    // {el, handle, startX, startY, startW, startH, startL, startT}

/* Store uploaded JSON per room locally for quick access in UI (backend copy stored via POST) */
const localRoomData = {}; // roomId -> string (json)

/* ---------------------------
   Backend: load room types
   --------------------------- */
async function loadRoomTemplates() {
  try {
    const res = await fetch(API_BASE + "/rooms");
    const data = await res.json();
    const container = qs("#roomTemplates");
    container.innerHTML = "";
    data.rooms.forEach(t => {
      const btn = create("div", { className: "room-btn" });
      btn.innerHTML = `<div style="font-weight:600">${t.type}</div><div style="color:var(--muted)"> ${t.width}×${t.height}</div>`;
      btn.onclick = () => addRoomInstance(t);
      container.appendChild(btn);
    });
  } catch (err) {
    console.warn("Could not load /rooms:", err);
    // Fallback templates
    const fallback = [
      {"type":"bedroom","width":120,"height":18880},
      {"type":"bathroom","width":80,"height":80},
      {"type":"kitchen","width":140,"height":100},
      {"type":"living","width":160,"height":140}
    ];
    const container = qs("#roomTemplates");
    container.innerHTML = "";
    fallback.forEach(t => {
      const btn = create("div", { className: "room-btn" });
      btn.innerHTML = `<div style="font-weight:600">${t.type}</div><div style="color:var(--muted)"> ${t.width}×${t.height}</div>`;
      btn.onclick = () => addRoomInstance(t);
      container.appendChild(btn);
    });
  }
}

/* ---------------------------
   Create a room DOM node
   --------------------------- */
function createRoomNode({type, width, height, x=20, y=20, id=null, svg=null}) {
  const el = create("div", { className:"room" });
  el.dataset.roomType = type;
  el.dataset.room_name= type + roomCounter;
  el.dataset.roomId = id || ("room_" + (roomCounter++));
  
  el.style.width = px(width);
  el.style.height = px(height);
  el.style.left = px(x);
  el.style.top = px(y);
  el.style.position = "absolute";

  // --- Insert SVG if provided ---
  if(svg) {
    el.insertAdjacentHTML("beforeend", svg);
    // make SVG fill the container
    const svgEl = el.querySelector("svg");
    if(svgEl){
      svgEl.style.width = "100%";
      svgEl.style.height = "100%";
      svgEl.style.display = "block";
      el.style.backgroundImage = `url('data:image/svg+xml;utf8,${encodeURIComponent(svgEl)}')`;
      el.style.backgroundSize = "100% 100%";
    el.style.backgroundRepeat = "no-repeat";
    el.style.preserveAspectRatio="none";
    }
  }

  // --- Title & meta ---
  const title = create("div", { className:"title" });
  title.textContent = el.dataset.room_name;
  const meta = create("div", { className:"meta" });
  meta.textContent = `${height}px×${width}px`;
  el._meta = meta;

  el.appendChild(title);
  el.appendChild(meta);

  // --- Resize handles ---
  ["tl","tr","bl","br"].forEach(pos => {
    const rh = create("div", { className: `resize-handle resize-${pos}` });
    el.appendChild(rh);
  });

  // --- Delete & Edit buttons ---
  const delBtn = create("div", { className:"delete-btn" });
  delBtn.innerHTML = "✕";
  delBtn.onclick = () => el.remove();
  el.appendChild(delBtn);

  const editBtn = create("div", { className:"edit-btn" });
  editBtn.innerHTML = "Edit";
  el.appendChild(editBtn);

  // --- Drag events ---
  el.addEventListener("mousedown", (e) => {
    if(locked) return;
    if(e.target.classList.contains("resize-handle") || e.target.tagName==="INPUT") return;
    startDrag(e, el);
  });

  // --- Hover events ---
  el.addEventListener("mouseenter", () => handle_resize_text(el, el.style.height, el.style.width));
  el.addEventListener("mouseleave", () => handle_resize_text(el, el.style.height, el.style.width));

  return el;
}

/* ---------------------------
   Add room instance & append to canvas
   --------------------------- */
function addRoomInstance(template) {
  const x = 20 + (Math.random() * 160);
  const y = 20 + (Math.random() * 120);
  const el = createRoomNode({ type: template.type, width: template.width, height: template.height, x: snapToGrid(x), y: snapToGrid(y) ,svg:template.svg });
  canvas.appendChild(el);
}

/* ---------------------------
   Dragging logic
   --------------------------- */
function startDrag(e, el) {
  e.preventDefault();
  const rect = getRect(el);
  dragging = {
    el,
    startMouseX: e.pageX,
    startMouseY: e.pageY,
    startX: rect.x,
    startY: rect.y
  };
  el.classList.add("dragging");
  // bring to front
  el.style.zIndex = 1000;
}

document.addEventListener("mousemove", (e) => {
  if (dragging && !locked) {
    const { el, startMouseX, startMouseY, startX, startY } = dragging;
    let nx = startX + (e.pageX - startMouseX);
    let ny = startY + (e.pageY - startMouseY);

    // apply grid snapping
    nx = snapToGrid(nx);
    ny = snapToGrid(ny);

    el.style.left = px(nx);
    el.style.top = px(ny);

    // magnetic snapping to other rooms
    magneticSnap(el);

    // constrain to canvas
    resolveCanvasBounds(el);

    // collision prevention (push out minimally)
    resolveCollision(el);
  }

  // resizing
  if (resizing && !locked) {
    const { el, handle, startX, startY, startW, startH, startL, startT } = resizing;
    const dx = e.pageX - startX;
    const dy = e.pageY - startY;

    if (handle.classList.contains("resize-br")) {
      let w = Math.max(MIN_W, startW + dx);
      let h = Math.max(MIN_H, startH + dy);
      el.style.width = px(snapToGrid(w));
      el.style.height = px(snapToGrid(h));
    } else if (handle.classList.contains("resize-bl")) {
      let w = Math.max(MIN_W, startW - dx);
      let h = Math.max(MIN_H, startH + dy);
      let left = startL + dx;
      el.style.width = px(snapToGrid(w));
      el.style.height = px(snapToGrid(h));
      el.style.left = px(snapToGrid(left));
    } else if (handle.classList.contains("resize-tr")) {
      let w = Math.max(MIN_W, startW + dx);
      let h = Math.max(MIN_H, startH - dy);
      let top = startT + dy;
      el.style.width = px(snapToGrid(w));
      el.style.height = px(snapToGrid(h));
      el.style.top = px(snapToGrid(top));
    } else if (handle.classList.contains("resize-tl")) {
      let w = Math.max(MIN_W, startW - dx);
      let h = Math.max(MIN_H, startH - dy);
      let left = startL + dx;
      let top = startT + dy;
      el.style.width = px(snapToGrid(w));
      el.style.height = px(snapToGrid(h));
      el.style.left = px(snapToGrid(left));
      el.style.top = px(snapToGrid(top));
    }

    // magnetic + bounds + collision
    magneticSnap(el);
    resolveCanvasBounds(el);
    resolveCollision(el);
  }
});

document.addEventListener("mouseup", (e) => {
  if (dragging) {
    dragging.el.classList.remove("dragging");
    dragging.el.style.zIndex = 1;
    dragging = null;
  }
  if (resizing) {
    resizing.el.style.zIndex = 1;
    //handle_resize_text(resizing.el,resizing.startH,resizing.startW)
    resizing = null;
  }
});



/* ---------------------------
   Resize handle initiation
   --------------------------- */
document.addEventListener("mousedown", (e) => {
  if (locked) return;
  if (!e.target.classList.contains("resize-handle")) return;
  const handle = e.target;
  const el = handle.parentElement;
  const rect = getRect(el);
  resizing = {
    el,
    handle,
    startX: e.pageX,
    startY: e.pageY,
    startW: rect.w,
    startH: rect.h,
    startL: rect.x,
    startT: rect.y
  };
  el.style.zIndex = 1000;
  console.log("hello")
    console.log(resizing.startH)
  
  e.stopPropagation();
});
function handle_resize_text(el,height,width){
    el._meta.textContent = `${height}×${width}`;; 
}
/* ---------------------------
   Magnetic snapping (edge, corner, center) + grid
   --------------------------- */
function magneticSnap(el) {
  const rect1 = getRect(el);
  const others = qsa(".room").filter(r => r !== el);

  // compute centers for current
  const center1 = { x: rect1.x + rect1.w/2, y: rect1.y + rect1.h/2 };

  others.forEach(o => {
    const r2 = getRect(o);

    // edges
    // left edge of el to right edge of other
    if (Math.abs(rect1.x - (r2.x + r2.w)) <= MAGNETIC_DIST) {
      el.style.left = px(r2.x + r2.w);
    }
    // right edge of el to left edge of other
    if (Math.abs((rect1.x + rect1.w) - r2.x) <= MAGNETIC_DIST) {
      el.style.left = px(r2.x - rect1.w);
    }
    // top edge of el to bottom edge of other
    if (Math.abs(rect1.y - (r2.y + r2.h)) <= MAGNETIC_DIST) {
      el.style.top = px(r2.y + r2.h);
    }
    // bottom edge of el to top edge of other
    if (Math.abs((rect1.y + rect1.h) - r2.y) <= MAGNETIC_DIST) {
      el.style.top = px(r2.y - rect1.h);
    }

    // corners (align left/top etc.)
    if (Math.abs(rect1.x - r2.x) <= MAGNETIC_DIST) el.style.left = px(r2.x);
    if (Math.abs((rect1.x + rect1.w) - (r2.x + r2.w)) <= MAGNETIC_DIST) el.style.left = px(r2.x + r2.w - rect1.w);
    if (Math.abs(rect1.y - r2.y) <= MAGNETIC_DIST) el.style.top = px(r2.y);
    if (Math.abs((rect1.y + rect1.h) - (r2.y + r2.h)) <= MAGNETIC_DIST) el.style.top = px(r2.y + r2.h - rect1.h);

    // center alignment
    const center2 = { x: r2.x + r2.w/2, y: r2.y + r2.h/2 };
    if (Math.abs(center1.x - center2.x) <= MAGNETIC_DIST) {
      el.style.left = px(Math.round(center2.x - rect1.w/2));
    }
    if (Math.abs(center1.y - center2.y) <= MAGNETIC_DIST) {
      el.style.top = px(Math.round(center2.y - rect1.h/2));
    }
  });

  // after magnetic adjustments, snap to grid for consistent look & to respect user choice B
  const finalX = snapToGrid(toInt(el.style.left));
  const finalY = snapToGrid(toInt(el.style.top));
  el.style.left = px(finalX);
  el.style.top = px(finalY);
}

/* ---------------------------
   Prevent overlapping: resolveCollision
   Moves element minimally along smallest axis to avoid overlap
   --------------------------- */
function resolveCollision(el) {
  const rect1 = getRect(el);
  const others = qsa(".room").filter(r => r !== el);

  for (let o of others) {
    const rect2 = getRect(o);
    if (isColliding(rect1, rect2)) {
      // compute overlaps
      const overlapLeft = (rect1.x + rect1.w) - rect2.x;          // how much rect1 intrudes from left into rect2
      const overlapRight = (rect2.x + rect2.w) - rect1.x;
      const overlapTop = (rect1.y + rect1.h) - rect2.y;
      const overlapBottom = (rect2.y + rect2.h) - rect1.y;

      // pick smallest positive overlap
      const candidates = [
        {axis:'x', dir:'left', val: overlapLeft},
        {axis:'x', dir:'right', val: overlapRight},
        {axis:'y', dir:'top', val: overlapTop},
        {axis:'y', dir:'bottom', val: overlapBottom}
      ].filter(c => c.val > 0);

      if (candidates.length === 0) continue;
      candidates.sort((a,b) => a.val - b.val);
      const smallest = candidates[0];

      if (smallest.axis === 'x') {
        if (smallest.dir === 'left') {
          // move el to left of rect2
          el.style.left = px(rect2.x - rect1.w);
        } else {
          // move el to right of rect2
          el.style.left = px(rect2.x + rect2.w);
        }
      } else {
        if (smallest.dir === 'top') {
          el.style.top = px(rect2.y - rect1.h);
        } else {
          el.style.top = px(rect2.y + rect2.h);
        }
      }

      // after moving, update rect1 for possible further overlaps
      rect1.x = toInt(el.style.left);
      rect1.y = toInt(el.style.top);
    }
  }
}

/* Ensure the element remains within canvas bounds */
function resolveCanvasBounds(el) {
  const rect = getRect(el);
  const clamped = clampToCanvas(rect, canvas);
  el.style.left = px(clamped.x);
  el.style.top = px(clamped.y);
}

/* ---------------------------
   Save / Load layout
   --------------------------- */
async function saveLayout() {
  const rooms = qsa(".room").map(r => {
    const rect = getRect(r);
    return {
      id: r.dataset.roomId,
      type: r.dataset.roomType,
      x: rect.x,
      y: rect.y,
      width: rect.w,
      height: rect.h,
      attached_json: r.dataset.room_name+'.json' || null
    };
  });
  try {
    const res = await fetch(API_BASE + "/layout/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ layout: rooms })
    });
    const j = await res.json();
    alert("Layout saved: " + (j.status || "ok"));
  } catch (err) {
    console.error("Save failed", err);
    alert("Save failed");
  }
}

async function loadLayout() {
  try {
    const res = await fetch(API_BASE + "/layout/load", { method: "POST" });
    const j = await res.json();
    if (!j || !j.layout) {
      alert("No saved layout found");
      return;
    }
    // clear canvas
    canvas.innerHTML = "";
    // reset counter a bit to avoid conflicts
    roomCounter = 1;
    j.layout.forEach(item => {
      const el = createRoomNode({
        type: item.type,
        width: item.width,
        height: item.height,
        x: snapToGrid(item.x),
        y: snapToGrid(item.y),
        id: item.id
      });
      canvas.appendChild(el);
      if (item.attached_json) {
        localRoomData[item.id] = item.attached_json;
      }
    });
  } catch (err) {
    console.error("Load failed", err);
    alert("Load failed");
  }
}

/* ---------------------------
   UI buttons
   --------------------------- */
qs("#btnAddSample").onclick = () => {
  // pick the first template or fallback
  const first = qs("#roomTemplates .room-btn");
  if (!first) return;
  // emulate click to add
  first.click();
};

qs("#btnToggleLock").onclick = () => {
  locked = !locked;
  qs("#btnToggleLock").textContent = locked ? "Unlock" : "Lock";
  qsa(".room").forEach(r => {
    if (locked) r.classList.add("locked");
    else r.classList.remove("locked");
  });
};

qs("#btnSave").onclick = saveLayout;


/* ---------------------------
   Init
   --------------------------- */
loadRoomTemplates();

/* Make canvas a bit roomy by default */
canvas.style.minHeight = "600px";


document.addEventListener("click", (e) => {
    if (e.target.classList.contains("delete-btn")) {
        const room = e.target.parentElement;
        room.remove();
        return;
    }
});



// modal js 

let modal = document.getElementById("roomModal");
let modalRoomName = document.getElementById("modalRoomName");
let modalFileInput = document.getElementById("roomFileInput");
let activeRoom = null;

// Open modal
document.addEventListener("click", (e) => {
    if (e.target.classList.contains("edit-btn")) {
        activeRoom = e.target.parentElement;
        modal.style.display = "flex";

        modalRoomName.textContent = activeRoom.dataset.room_name;
    }
});

// Close modal
document.querySelector(".modal .close").onclick = () => {
    modal.style.display = "none";
};

// Save JSON
document.getElementById("saveRoomData").onclick = async () => {
    const file = modalFileInput.files[0];
    if (!file) {
        alert("Please select a JSON file.");
        return;
    }

    // Save inside the room DOM element
    const text = await file.text();
    activeRoom.dataset.json = text;

    // Upload to the server
    const form = new FormData();
    form.append("room_id", activeRoom.dataset.room_name); // IMPORTANT
    form.append("file", file);

    try {
        const res = await fetch("http://127.0.0.1:5000/room/data", {
            method: "POST",
            body: form,
        });

        const out = await res.json();
        console.log("Uploaded room JSON:", out);

        alert("JSON saved as " + activeRoom.dataset.room_name + ".json");
    } catch (err) {
        console.error("Upload failed", err);
        alert("Failed to save JSON");
    }

    modal.style.display = "none";
};








/* Keyboard: delete selected room on Delete key when not locked (selected via clicking) */
let selectedForDelete = null;
canvas.addEventListener("click", (e) => {
  if (e.target.classList.contains("room") || e.target.closest(".room")) {
    selectedForDelete = e.target.closest(".room");
    // highlight briefly
    selectedForDelete.style.boxShadow = "0 6px 18px rgba(0,0,0,0.12)";
    setTimeout(() => {
      if (selectedForDelete) selectedForDelete.style.boxShadow = "";
    }, 400);
  } else {
    selectedForDelete = null;
  }
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Delete" && selectedForDelete && !locked) {
    selectedForDelete.remove();
    selectedForDelete = null;
  }
});





document.getElementById("runScriptsBtn").addEventListener("click", async () => {
    const res = await fetch("/run-scripts", { method: "POST" });

    const data = await res.json();
    console.log("Server response:", data);
});