// content.js
// Listens for window messages and fills the first detected input field

window.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'fill_plate') {
    const plate = event.data.plate;
    // Try to find a focused or visible input field
    let input = document.activeElement;
    if (!input || input.tagName !== 'INPUT') {
      input = document.querySelector('input[type="text"], input:not([type])');
    }
    if (input) {
      input.value = plate;
      input.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }
});
