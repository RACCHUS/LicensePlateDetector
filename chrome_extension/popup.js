// popup.js
// Handles the Select Target Field button

document.addEventListener('DOMContentLoaded', function() {
  const btn = document.getElementById('select-field-btn');
  if (btn) {
    btn.addEventListener('click', function() {
      chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.scripting.executeScript({
          target: {tabId: tabs[0].id},
          files: ['select_field.js']
        });
      });
    });
  }
});
