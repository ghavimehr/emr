// cc_autocomplete.js
document.addEventListener('DOMContentLoaded', function() {
  const inputCC = document.getElementById('chief_complaint_input');
  const hiddenField = document.getElementById('id_chief_complaint');

  // We'll create a container for suggestions, plus arrow navigation
  let dropdown = null;
  let currentIndex = -1;
  let items = [];

  function ensureDropdown() {
    if (!dropdown) {
      dropdown = document.createElement('div');
      dropdown.style.position = 'absolute';
      dropdown.style.background = '#fff';
      dropdown.style.border = '1px solid #ccc';
      dropdown.style.zIndex = '9999';
      dropdown.style.width = inputCC.offsetWidth + 'px';
      dropdown.style.maxHeight = '200px';
      dropdown.style.overflowY = 'auto';
      dropdown.style.fontSize = '0.9rem';
      dropdown.style.display = 'none';
      document.body.appendChild(dropdown);
    }
  }

  function positionDropdown() {
    const rect = inputCC.getBoundingClientRect();
    dropdown.style.left = rect.left + 'px';
    dropdown.style.top = (rect.bottom + window.scrollY) + 'px';
    dropdown.style.width = rect.width + 'px';
  }

  function showSuggestions(data) {
    ensureDropdown();
    dropdown.innerHTML = '';
    items = [];
    currentIndex = -1;

    data.forEach(cc => {
      const item = document.createElement('div');
      const displayText = cc.fname || cc.name || '';
      item.textContent = displayText;
      item.style.padding = '6px 8px';
      item.style.cursor = 'pointer';

      item.addEventListener('mouseenter', () => {
        item.style.background = '#e2e2e2';
      });
      item.addEventListener('mouseleave', () => {
        item.style.background = '#fff';
      });
      item.addEventListener('click', () => {
        selectItem(cc, displayText);
      });

      dropdown.appendChild(item);
      items.push({ element: item, data: cc, displayText });
    });

    if (data.length > 0) {
      dropdown.style.display = 'block';
    } else {
      dropdown.style.display = 'none';
    }
    positionDropdown();
  }

  function selectItem(cc, displayText) {
    hiddenField.value = cc.id;
    inputCC.value = displayText;
    dropdown.style.display = 'none';
  }

  function finalizeNewCC() {
    // user typed something new
    hiddenField.value = '';
  }

  // Hide dropdown if user clicks elsewhere
  document.addEventListener('click', function(e) {
    if (e.target !== inputCC && dropdown && !dropdown.contains(e.target)) {
      dropdown.style.display = 'none';
    }
  });

  // The core event: user typed in "chief_complaint_input"
  inputCC.addEventListener('input', function() {
    const val = this.value.trim();
    // reset hidden field by default
    hiddenField.value = '';

    if (val.length >= 3) {
      fetch(`/ccpi/search-cc/?q=` + encodeURIComponent(val), {
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(resp => resp.json())
      .then(data => {
        showSuggestions(data);
      })
      .catch(err => console.error("Autocomplete fetch error:", err));
    } else {
      if (dropdown) dropdown.style.display = 'none';
    }
  });

  // arrow navigation & enter
  inputCC.addEventListener('keydown', function(e) {
    if (!dropdown || dropdown.style.display === 'none') return;
    if (items.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      currentIndex = (currentIndex + 1) % items.length;
      highlightItem();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      currentIndex = (currentIndex - 1 + items.length) % items.length;
      highlightItem();
    } else if (e.key === 'Enter') {
      if (currentIndex >= 0 && currentIndex < items.length) {
        const { data, displayText } = items[currentIndex];
        selectItem(data, displayText);
      } else {
        finalizeNewCC();
      }
      dropdown.style.display = 'none';
      e.preventDefault();
    }
  });

  function highlightItem() {
    items.forEach((itm, idx) => {
      itm.element.style.background = (idx === currentIndex) ? '#dedede' : '#fff';
    });
  }
});
