document.addEventListener("DOMContentLoaded", () => {
  // Save your intent & rating, which augments the last pageData entry
  // if user_id on the background script isn't null, load it into the user_id input
  browser.storage.local.get("user_id").then(({ user_id }) => {
    if (user_id) {
      document.getElementById("user_id").value = user_id;
    }
  });

  document.getElementById("user_id").addEventListener("focusout", async () => {
    await browser.runtime.sendMessage({
      type: "user_id",
      data: {
        user_id: document.getElementById("user_id").value.trim()
      }
    });
  });

  document.getElementById("host_option").addEventListener("change", async () => {
    const hostOption = document.getElementById("host_option").value;
    await browser.runtime.sendMessage({
      type: "host_option",
      data: {
        host_option: hostOption
      }
    });
  });

  document.getElementById("save").addEventListener("click", async () => {
    const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
    const intent = document.getElementById("intent").value.trim();
    const rating = Number(document.getElementById("rating").value);
    if (!intent || !rating) {
      alert("Please fill in both intent and rating.");
      return;
    }

    await browser.runtime.sendMessage({
      type: "userEntry",
      data: {
        url: tab.url,
        intent,
        rating,
        timestamp: new Date().toISOString()
      }
    });
    window.close();
  });

  // Export the unified logs array
  document.getElementById("export").addEventListener("click", async () => {
    const { logs = [] } = await browser.storage.local.get("logs");
    const blob = new Blob([JSON.stringify(logs, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `browser-data-${new Date().toISOString().slice(0,10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  });
});
