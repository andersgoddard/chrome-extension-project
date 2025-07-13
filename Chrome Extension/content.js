function extractPropertyInfo() {
  const postcodeElement = document.querySelector('[itemprop="postalCode"]');
  const postcode = postcodeElement ? postcodeElement.textContent.trim() : null;

  const epcLink = [...document.querySelectorAll('a')]
    .find(a => a.href.includes('epc'));

  const epcURL = epcLink ? epcLink.href : null;

  const currentURL = window.location.href;

  chrome.storage.local.set({
    postcode,
    epcURL,
    currentURL
  }, () => {
    chrome.runtime.sendMessage({ status: "saved" });
  });
}

window.addEventListener("load", extractPropertyInfo);
