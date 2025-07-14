chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status !== "complete" || !tab.url) return;

  // Check if URL matches Rightmove property listing pattern
  const isRightmoveProperty = /^https:\/\/www\.rightmove\.co\.uk\/properties\/\d+/.test(tab.url);
  if (!isRightmoveProperty) return;

  chrome.scripting.executeScript({
    target: { tabId: tabId },
    files: ["content.js"]
  });
});
