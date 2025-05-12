document.addEventListener('DOMContentLoaded', function () {
    const tagsInput = document.getElementById('secretaryTagsSearch');
    const suggestionsList = document.getElementById('secretaryTagsSuggestions');
    const selectedTagsContainer = document.getElementById('selectedSecretaryTags');

    let selectedTags = new Set(); // To store selected tags' names

    tagsInput.addEventListener('input', function () {
        const query = this.value.trim();
        if (query.length >= 3) {
            fetch(`/secretary-tags-search/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    // Clear existing suggestions
                    suggestionsList.innerHTML = '';

                    if (data.length > 0) {
                        suggestionsList.classList.remove('hidden');
                        data.forEach(item => {
                            const suggestion = document.createElement('li');
                            suggestion.textContent = item.name;
                            suggestion.dataset.id = item.id;
                            suggestion.className = "p-2 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer";

                            // On click, add the tag to selected tags
                            suggestion.addEventListener('click', function () {
                                if (!selectedTags.has(item.name)) {
                                    addTag(item.name);
                                }
                                tagsInput.value = ''; // Clear the input field
                                suggestionsList.classList.add('hidden');
                            });

                            suggestionsList.appendChild(suggestion);
                        });
                    } else {
                        const noResults = document.createElement('li');
                        noResults.textContent = 'No results found';
                        noResults.className = "p-2 text-gray-500 dark:text-gray-400";
                        suggestionsList.appendChild(noResults);
                    }
                })
                .catch(err => console.error('Error fetching secretary tags:', err));
        } else {
            suggestionsList.classList.add('hidden');
        }
    });

    // Add a tag (new or selected)
    function addTag(tagName) {
        selectedTags.add(tagName);

        // Create a tag element
        const tagElement = document.createElement('div');
        tagElement.className = "flex items-center px-3 py-1 bg-blue-500 text-white rounded-full text-sm";
        tagElement.textContent = tagName;

        // Add remove button to the tag
        const removeButton = document.createElement('button');
        removeButton.textContent = 'x';
        removeButton.className = "ml-2 text-white text-xs font-bold";
        removeButton.addEventListener('click', function () {
            selectedTags.delete(tagName);
            tagElement.remove();
        });

        tagElement.appendChild(removeButton);
        selectedTagsContainer.appendChild(tagElement);
    }

    // Allow adding a new tag on "Enter" key press
    tagsInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && tagsInput.value.trim().length > 0) {
            const newTag = tagsInput.value.trim();
            if (!selectedTags.has(newTag)) {
                addTag(newTag);
            }
            tagsInput.value = ''; // Clear the input field
            e.preventDefault();
        }
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', function (e) {
        if (!suggestionsList.contains(e.target) && e.target !== tagsInput) {
            suggestionsList.classList.add('hidden');
        }
    });
});





// document.addEventListener('DOMContentLoaded', function() {
//   // DOM elements
//   const searchInput = document.getElementById('secretarytagsSearch'); // Search input box
//   const selectedTagsContainer = document.getElementById('selected-tags-container'); // Container for selected tags
//   const hiddenField = document.getElementById('id_secretarytags'); // Hidden field to store JSON
//   const resultsContainer = document.createElement('div'); // Dropdown for search results
//
//   // Styling for results dropdown
//   resultsContainer.style.position = 'absolute';
//   resultsContainer.style.backgroundColor = 'white';
//   resultsContainer.style.border = '1px solid #ccc';
//   resultsContainer.style.width = searchInput.offsetWidth + 'px';
//   resultsContainer.style.zIndex = '1000';
//   resultsContainer.style.display = 'none';
//   searchInput.parentNode.appendChild(resultsContainer);
//
//   // Store selected tags in JSON format
//   let selectedTags = {};
//
//   // Update the hidden field with JSON data
//   function updateHiddenField() {
//     hiddenField.value = JSON.stringify(selectedTags);
//   }
//
//   // Render selected tags
//   function renderSelectedTags() {
//     selectedTagsContainer.innerHTML = ''; // Clear existing tags
//
//     Object.entries(selectedTags).forEach(([id, name]) => {
//       const tagDiv = document.createElement('div');
//       tagDiv.textContent = name;
//       tagDiv.style.display = 'inline-block';
//       tagDiv.style.margin = '5px';
//       tagDiv.style.padding = '5px 10px';
//       tagDiv.style.border = '1px solid #ccc';
//       tagDiv.style.borderRadius = '5px';
//       tagDiv.style.backgroundColor = '#f9f9f9';
//       tagDiv.style.cursor = 'pointer';
//
//       // Add remove functionality
//       const removeIcon = document.createElement('span');
//       removeIcon.textContent = ' ✕';
//       removeIcon.style.color = 'red';
//       removeIcon.style.marginLeft = '5px';
//       removeIcon.style.cursor = 'pointer';
//       removeIcon.addEventListener('click', function() {
//         delete selectedTags[id];
//         renderSelectedTags();
//         updateHiddenField();
//       });
//
//       tagDiv.appendChild(removeIcon);
//       selectedTagsContainer.appendChild(tagDiv);
//     });
//   }
//
//   // Fetch and display search results
//   searchInput.addEventListener('input', function() {
//     const query = this.value.trim();
//     resultsContainer.innerHTML = ''; // Clear previous results
//
//     if (query.length >= 3) {
//       fetch('/identity/secretarytags-search/?q=' + encodeURIComponent(query))
//         .then(resp => resp.json())
//         .then(data => {
//           if (data.length > 0) {
//             resultsContainer.style.display = 'block';
//             data.forEach(item => {
//               const option = document.createElement('div');
//               option.textContent = item.name;
//               option.style.padding = '5px';
//               option.style.cursor = 'pointer';
//
//               // On click, add tag to selectedTags
//               option.addEventListener('click', function() {
//                 selectedTags[item.id] = item.name; // Add to selectedTags
//                 renderSelectedTags(); // Update UI
//                 updateHiddenField(); // Update hidden field
//                 resultsContainer.style.display = 'none'; // Hide dropdown
//                 searchInput.value = ''; // Clear input box
//               });
//
//               option.addEventListener('mouseenter', function() {
//                 option.style.backgroundColor = '#f0f0f0';
//               });
//
//               option.addEventListener('mouseleave', function() {
//                 option.style.backgroundColor = 'white';
//               });
//
//               resultsContainer.appendChild(option);
//             });
//           } else {
//             resultsContainer.style.display = 'none';
//           }
//         })
//         .catch(err => console.error('Error fetching secretarytags:', err));
//     } else {
//       resultsContainer.style.display = 'none';
//     }
//   });
//
//   // Hide dropdown when clicking outside
//   document.addEventListener('click', function(e) {
//     if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
//       resultsContainer.style.display = 'none';
//     }
//   });
//
//   // Initialize existing tags (if any)
//   if (hiddenField.value) {
//     selectedTags = JSON.parse(hiddenField.value);
//     renderSelectedTags();
//   }
// });
