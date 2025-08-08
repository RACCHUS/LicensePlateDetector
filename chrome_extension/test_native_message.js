// Run this in the Chrome extension's background or popup console to test native messaging

chrome.runtime.sendNativeMessage(
  'com.licenseplatedetector.host',
  { type: 'fill_plate', plate: 'TEST123' },
  function(response) {
    if (chrome.runtime.lastError) {
      console.error('Native messaging error:', chrome.runtime.lastError.message);
    } else {
      console.log('Native host response:', response);
    }
  }
);
