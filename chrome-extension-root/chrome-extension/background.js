chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status !== "complete" || !tab.url) return;
  
  chrome.storage.local.get(["monitoring"], (res) => {

	  // Check if URL matches Rightmove property listing pattern
	  if (!res.monitoring) return; // Don't run unless monitoring is on
	  
	  const isRightmoveProperty = /^https:\/\/www\.rightmove\.co\.uk\/properties\/\d+/.test(tab.url);
	  if (!isRightmoveProperty) return;

	  chrome.scripting.executeScript({
		target: { tabId: tabId },
		files: ["content.js"]
	  });
	});
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "closeTab" && sender.tab && sender.tab.id) {
    chrome.tabs.remove(sender.tab.id);
  }
});