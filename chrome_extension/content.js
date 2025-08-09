// content.js
// Listens for window messages and fills the first detected input field

window.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'fill_plate') {
    const plate = event.data.plate;
    // Try to use the user-selected field if available
    chrome.storage.local.get('licensePlateFieldSelector', (result) => {
      let selector = result.licensePlateFieldSelector;
      let input = null;
      if (selector) {
        try {
          input = document.querySelector(selector);
        } catch (e) {
          input = null;
        }
      }
      if (!input) {
        // Fallback to focused or first input
        input = document.activeElement;
        if (!input || (input.tagName !== 'INPUT' && input.tagName !== 'TEXTAREA')) {
          input = document.querySelector('input[type="text"], input:not([type]), textarea');
        }
      }
      if (input) {
        input.value = plate;
        input.dispatchEvent(new Event('input', { bubbles: true }));
      }
    });
  }
});
