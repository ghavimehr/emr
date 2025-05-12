function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}


document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('dashboard-search-box');
  const resultsDiv = document.getElementById('dashboard-search-results');

  searchInput.addEventListener('input', function() {
    const query = this.value.trim();
    if (query.length >= 3) {
      fetch('/my_dashboard/patient-search/?q=' + encodeURIComponent(query))
        .then(resp => resp.json())
        .then(data => {
          // Clear old results
          resultsDiv.innerHTML = '';
  
          // Create a wrapper that can scroll
          const list = document.createElement('div');
          list.style.maxHeight = '250px';
          list.style.overflowY = 'auto';
  
          let currentIndex = -1;
          let items = [];
  
          data.forEach((item, idx) => {
            let row = document.createElement('div');
            row.classList.add('search-result-row', 'cursor-pointer');
            row.style.display = 'grid';
            row.style.gridTemplateColumns = '120px 1fr 1fr 1fr';
            row.style.padding = '4px';
            row.style.alignItems = 'center';
            row.style.backgroundColor = 'var(--search-result-bg, white)';
            row.style.color = 'var(--search-result-text, black)';
            // row.style.fontSize = '10xp';
  
            const pid = String(item.patient_id);
            row.innerHTML = `
              <div>${item.first_name}</div>
              <div>${item.last_name}</div>
              <div>${pid}</div>
              <div>${item.ssn}</div>
            `;
  
            row.addEventListener('click', () => {
              searchInput.value = `${item.first_name} ${item.last_name}`;
              resultsDiv.style.display = 'none';
              // POST to the server to save 'selected_patient_id' in session
              fetch('/my_dashboard/select-patient/', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') // see below
                  },
                  body: JSON.stringify({ patient_id: item.id }) // item.id = DB PK
              })
              .then(resp => resp.json())
              .then(result => {
                  console.log('Session updated:', result);
                  // Reload the page after patient selection is complete
                  location.reload();  // This reloads the page
              })
              .catch(err => console.error(err));
              console.log('Clicked:', item);
            });
  
            items.push(row);
  
            row.addEventListener('mouseenter', () => {
              row.style.backgroundColor = '#e2e8f0';
            });
            row.addEventListener('mouseleave', () => {
              row.style.backgroundColor = 'var(--search-result-bg, white)';
            });
  
            list.appendChild(row);
          });
  
          resultsDiv.appendChild(list);
          resultsDiv.style.display = 'block';
  
          searchInput.addEventListener('keydown', function(e) {
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
              if (currentIndex >= 0 && items[currentIndex]) {
                items[currentIndex].click();
              }
            }
          });
  
          function highlightItem() {
            items.forEach((row, idx) => {
              row.style.backgroundColor = (idx === currentIndex)
                ? '#cbd5e1'
                : 'var(--search-result-bg, white)';
            });
          }
        })
        .catch(err => console.error(err));
    } else {
      resultsDiv.style.display = 'none';
    }
  });  
});
