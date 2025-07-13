document.getElementById('spinner').style.display = 'block';

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.status === "saved") {
    document.getElementById('spinner').style.display = 'none';
    document.getElementById('tick').style.display = 'block';
    document.getElementById('message').textContent = "Data saved successfully!";
  }
});
