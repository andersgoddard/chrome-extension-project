document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("toggle-btn");

  chrome.storage.local.get(["monitoring"], (res) => {
    const state = res.monitoring || false;
    btn.textContent = state ? "Stop Monitoring" : "Start Monitoring";
  });

  btn.addEventListener("click", () => {
    chrome.storage.local.get(["monitoring"], (res) => {
      const monitoring = !res.monitoring;
      chrome.storage.local.set({ monitoring });
      btn.textContent = monitoring ? "Stop Monitoring" : "Start Monitoring";
    });
  });
});
