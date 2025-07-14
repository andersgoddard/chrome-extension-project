chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status !== "complete" || !tab.url) return;

  chrome.storage.local.get("monitoring", (res) => {
    if (!res.monitoring) return;

    const isRightmove = /^https:\/\/www\.rightmove\.co\.uk\/properties\/\d+/.test(tab.url);
    if (!isRightmove) return;

    chrome.scripting.executeScript({
      target: { tabId },
      files: ["extract.js", "content.js"]
    });
  });
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "pageProcessed") {
    chrome.action.setBadgeText({ text: "✅" });
    chrome.action.setBadgeBackgroundColor({ color: "#4CAF50" });

    setTimeout(() => {
      chrome.action.setBadgeText({ text: "" });
    }, 3000);
  }
});
