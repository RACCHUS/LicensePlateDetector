// select_field.js
// Injected to let the user select a target input/textarea field for license plate input
(function() {
  let lastElem = null;

  function highlight(elem) {
    if (lastElem) lastElem.style.outline = '';
    if (elem) {
      elem.style.outline = '2px solid #1976d2';
      lastElem = elem;
    }
  }

  function onMouseOver(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
      highlight(e.target);
    }
  }

  function onClick(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
      e.preventDefault();
      e.stopPropagation();
      highlight(e.target);
      // Save selector (prefer id, then name, then tag)
      let selector = '';
      if (e.target.id) selector = `#${e.target.id}`;
      else if (e.target.name) selector = `${e.target.tagName.toLowerCase()}[name="${e.target.name}"]`;
      else selector = e.target.tagName.toLowerCase();
      chrome.storage.local.set({licensePlateFieldSelector: selector});
      document.removeEventListener('mouseover', onMouseOver, true);
      document.removeEventListener('click', onClick, true);
      if (lastElem) lastElem.style.outline = '';
      alert('Target field selected!');
    }
  }

  document.addEventListener('mouseover', onMouseOver, true);
  document.addEventListener('click', onClick, true);
  alert('Click on the field where license plates should be entered.');
})();
