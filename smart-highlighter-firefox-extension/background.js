let currentTabId = null;
let currentStartTime = null;
let user_id = "default";
let host_option = "local_https"; // default to local
// 🔁 Send data to your FastAPI server
async function sendToServer(data) {
  try {
    let url = "";
    if (host_option === "remote") {
      url = "https://aiapi.cybernautics.net/api/log";
    } else if (host_option == "local_https") {
      url = "https://127.0.0.1:8443/api/log"; // Localhost for local testing
    } else{
      url = "http://127.0.0.1:8123/api/log";
    }
    await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });
  } catch (err) {
    console.error("Failed to send data to FastAPI server:", err);
  }
}

// 🕒 Log how long the user was on the previous tab
async function logTime() {
  if (!currentTabId || !currentStartTime) return;

  try {
    if (user_id != null) {
    
    const tab = await browser.tabs.get(currentTabId);
    const duration = Date.now() - currentStartTime;

    const entry = {
      user_id: user_id,
      type: "timeOnPage",
      url: tab.url,
      tabId: currentTabId,
      title: tab.title,
      timeSpentMs: duration,
      timestamp: new Date().toISOString()
    };

    const { logs = [] } = await browser.storage.local.get("logs");
    logs.push(entry);
    await browser.storage.local.set({ logs });

    await sendToServer(entry); // ✅ send to FastAPI
  }
  } catch (e) {
    console.error("Error logging time:", e);
  }
}

// 📌 Track when the active tab changes
browser.tabs.onActivated.addListener(async (activeInfo) => {
  await logTime(); // log the tab you were just on
  currentTabId = activeInfo.tabId;
  currentStartTime = Date.now(); // start timing new tab
});

// 📌 Track when the browser window is focused/unfocused
browser.windows.onFocusChanged.addListener(async (windowId) => {
  await logTime();

  if (windowId === browser.windows.WINDOW_ID_NONE) {
    // user switched away
    currentTabId = null;
    currentStartTime = null;
  } else {
    // user returned — resume tracking
    const [tab] = await browser.tabs.query({ active: true, windowId });
    currentTabId = tab.id;
    currentStartTime = Date.now();
  }
});


// background.js
// How many seconds of no input counts as idle
const IDLE_SECS = 300;      // 5 min
browser.idle.setDetectionInterval(IDLE_SECS);

browser.idle.onStateChanged.addListener(async newState => {
  // newState is "active", "idle", or "locked"
  console.log('[idle] state →', newState);

  // broadcast to every tab that your copilot cares about
  const tabs = await browser.tabs.query({});      // filter as needed
  for (const tab of tabs) {
    browser.tabs.sendMessage(tab.id, { type: 'systemIdle', state: newState });
  }
});


// 📬 Receive messages from popup.js and content.js
browser.runtime.onMessage.addListener(async (message) => {
  //if (message.type === "scrollData" || message.type === "userEntry" || message.type === "logClick" || message.type === "logMouseup") {
  if (message.type === "user_id") {
    user_id = message.data.user_id;
    console.log("Name is " + user_id);
    // Store user_id in local storage
    await browser.storage.local.set({ user_id });
    return;
  }else if (message.type === "host_option") {
    host_option = message.data.host_option;
  }
  if (user_id != null) {
    message.data.user_id = user_id;
    const key = "logs"; //message.type === "scrollData" ? "scrollLogs" : "logs";
    const existing = (await browser.storage.local.get(key))[key] || [];
    existing.push(message.data);
    await browser.storage.local.set({ [key]: existing });

    await sendToServer(message.data); // ✅ send to FastAPI
  }
  //}
});
// communicate with domain
/* Cached in-memory copy of user details
   (because onBeforeRequest must return synchronously).           */


// Load on start-up


/* Utility: add or replace ?user=… */
// function injectQueryParam(originalUrl) {
//   const url = new URL(originalUrl);
//   url.searchParams.set("user_id", user_id);
//   return url.toString();
// }

/* Utility: add X-User-ID header */
function injectHeader(headers) {
  console.log("Injecting header with user_id:", user_id);
  headers.push({ name: "X-User-ID", value: user_id });
  console.log("Headers after injection:", headers);
  return headers;
}

// // /* OPTION A – rewrite the URL (works for any GET, same-origin or CORS) */
// browser.webRequest.onBeforeRequest.addListener(
//   details => {
//     if (details.method !== "GET") return;
//     return { redirectUrl: injectQueryParam(details.url) };
//   },
//   { urls: ["*://aiapi.cybernautics.net/*"], types: ["main_frame", "xmlhttprequest"] },
//   ["blocking"]
// );

/* OPTION B – keep the URL but add a header                        */
browser.webRequest.onBeforeSendHeaders.addListener(
  details => {
    return { requestHeaders: injectHeader(details.requestHeaders) };
  },
  { urls: ["https://aiapi.cybernautics.net/*", "https://127.0.0.1:8443/*", "http://127.0.0.1:8123/*"] },
  ["blocking", "requestHeaders"]
);
