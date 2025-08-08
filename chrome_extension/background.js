// background.js
// Listens for messages from the desktop app (via native messaging or WebSocket in future)

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'fill_plate') {
    // Relay to content script in active tab
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
      if (tabs.length > 0) {
        chrome.scripting.executeScript({
          target: {tabId: tabs[0].id},
          func: (plate) => {
            window.postMessage({type: 'fill_plate', plate: plate}, '*');
          },
          args: [message.plate]
        });
      }
    });
    sendResponse({status: 'ok'});
  }
});
