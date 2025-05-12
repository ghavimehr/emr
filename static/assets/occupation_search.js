document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('occupationSearch');
  const resultsContainer = document.createElement('div');
  resultsContainer.style.position = 'absolute';
  resultsContainer.style.backgroundColor = 'white';
  resultsContainer.style.border = '1px solid #ccc';
  resultsContainer.style.width = searchInput.offsetWidth + 'px';
  resultsContainer.style.zIndex = '1000';
  resultsContainer.style.display = 'none';

  searchInput.parentNode.appendChild(resultsContainer);

  searchInput.addEventListener('input', function() {
    let query = this.value.trim();
    resultsContainer.innerHTML = ''; // Clear old results
    if (query.length >= 3) {
      fetch('/identity/occupation-search/?q=' + encodeURIComponent(query))
        .then(resp => resp.json())
        .then(data => {
          if (data.length > 0) {
            resultsContainer.style.display = 'block';
            data.forEach(item => {
              const option = document.createElement('div');
              option.textContent = item.name;
              option.style.padding = '5px';
              option.style.cursor = 'pointer';

              option.addEventListener('click', function() {
                searchInput.value = item.name;
                document.getElementById('id_occupation').value = item.id; // Set hidden field
                resultsContainer.style.display = 'none';
              });

              option.addEventListener('mouseenter', function() {
                option.style.backgroundColor = '#f0f0f0';
              });

              option.addEventListener('mouseleave', function() {
                option.style.backgroundColor = 'white';
              });

              resultsContainer.appendChild(option);
            });
          } else {
            resultsContainer.style.display = 'none';
          }
        })
        .catch(err => console.error('Error fetching occupations:', err));
    } else {
      resultsContainer.style.display = 'none';
    }
  });

  // Hide dropdown if clicking outside
  document.addEventListener('click', function(e) {
    if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
      resultsContainer.style.display = 'none';
    }
  });
});
