document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("toggle-btn");

  chrome.storage.local.get(["monitoring"], (res) => {
    let state = res.monitoring;
	
	// If undefined, default to false
	if (state == undefined) {
		state = false;
		chrome.storage.local.set({ monitoring: state });
	}
	
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
