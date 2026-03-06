// content.js



(() => {
  let maxScroll = 0;
  let lastScrollY = window.scrollY;
  let reversals = 0;
  let lastDirection = 0;
  const scrollTimes = [];

  // Update scroll metrics on each scroll
  window.addEventListener("scroll", () => {
    const currY = window.scrollY;
    const total = document.documentElement.scrollHeight - window.innerHeight;
    const pct = total > 0 ? (currY / total) * 100 : 0;
    if (pct > maxScroll) maxScroll = pct;

    const dir = currY > lastScrollY ? 1 : currY < lastScrollY ? -1 : lastDirection;
    if (dir !== lastDirection) reversals++;
    lastDirection = dir;
    lastScrollY = currY;

    scrollTimes.push(Date.now());
  }, { passive: true });

  // Function to compute averages and send data
  function sendScrollData() {
    let avgInterval = 0;
    if (scrollTimes.length > 1) {
      const intervals = scrollTimes.slice(1).map((t, i) => t - scrollTimes[i]);
      avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
    }

    const data = {
      type: "scrollData",
      url: window.location.href,
      maxScrollPercent: Math.round(maxScroll),
      reversals,
      avgScrollIntervalMs: Math.round(avgInterval),
      timestamp: new Date().toISOString()
    };

    try {
      browser.runtime.sendMessage({ type: "scrollData", data });
      //console.log("Scroll data sent:", data);
    } catch (err) {
      console.error("Failed to send scrollData:", err);
    }
  }

  // Send on pagehide (fires when navigating away or closing tab)
  window.addEventListener("pagehide", sendScrollData);

  // Also send if the page becomes hidden (e.g., switching tabs)
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") {
      sendScrollData();
    }
  });

  // content-script.js
  document.addEventListener('click', e => {
    console.log("Click detected:", e);
    const el = e.target;
    const sel = window.getSelection().toString();
    const caret = document.caretPositionFromPoint
      ? document.caretPositionFromPoint(e.clientX, e.clientY)
      : document.caretRangeFromPoint(e.clientX, e.clientY);

    const record = {
      type: 'mouseDownEvent',
      timestamp:    new Date().toISOString(),
      coords:  { x: e.pageX, y: e.pageY },
      button:  e.button,
      element: {
        tag:       el.tagName,
        id:        el.id,
        snippet:   el.innerText.trim().slice(0,50),
      },
      selection: sel || null,
      caret:     caret ? { node: caret.offsetNode.nodeName, offset: caret.offset } : null
    };

  // send to your background script or IndexedDB
  browser.runtime.sendMessage({ type: 'logClick', data: record });
});

  // content-script.js
document.addEventListener('mouseup', e => {
  // 1. Capture the selected text, if any
  const selectionText = window.getSelection().toString() || null;

  // 2. Find caret position (exact character offset) if supported
  let caretInfo = null;
  if (selectionText === "") {
    // Only try caret APIs when there's no selection
    const caretRange = 
      document.caretPositionFromPoint
        ? document.caretPositionFromPoint(e.clientX, e.clientY)
        : document.caretRangeFromPoint(e.clientX, e.clientY);
    if (caretRange) {
      caretInfo = {
        node:   caretRange.offsetNode.nodeName,
        offset: caretRange.offset
      };
    }
  }

  // 3. Element context
  const el = e.target;
  const elementInfo = {
    type:     'mouseupEvent',
    tag:       el.tagName,
    id:        el.id || null,
    snippet:   (el.innerText || "").trim().slice(0, 50)
  };

  // 4. Build the record
  const record = {
    timestamp:      new Date().toISOString(),
    coords:    { x: e.pageX, y: e.pageY },
    button:    e.button,
    element:   elementInfo,
    selection: selectionText,
    caret:     caretInfo
  };

  // 5. Send it off (to background, IndexedDB, etc.)
  browser.runtime.sendMessage({
    type: 'logMouseup',
    data: record
  });
});


  // === WATERMARK ===
  function addWatermark() {
    if (document.getElementById("ai-tracker-badge")) return; // prevent duplicates

    const badge = document.createElement("div");
    badge.id = "ai-tracker-badge";
    badge.textContent = "⦿ AI Copilot Tracker Active";

    Object.assign(badge.style, {
      position: "fixed",
      bottom: "10px",
      right: "10px",
      zIndex: "999999",
      backgroundColor: "rgb(255, 8, 8)",
      color: "#fff",
      padding: "6px 10px",
      fontSize: "12px",
      fontFamily: "sans-serif",
      borderRadius: "6px",
      pointerEvents: "none",
      userSelect: "none"
    });

    document.body.appendChild(badge);
  }

  // Run watermark injection when the DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", addWatermark);
  } else {
    addWatermark();
  }
})();
