// static/js/suggestions.js
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('search-input');
    const suggestionBox = document.getElementById('suggestion-box');
    const form = document.getElementById('search-form');

    let selectedIndex = -1;
    let currentSuggestions = [];

    input.addEventListener('input', () => {
        const query = input.value.trim();
        selectedIndex = -1;

        if (query.length === 0) {
            suggestionBox.classList.remove('visible');
            suggestionBox.innerHTML = '';
            return;
        }

        fetch(`/api/suggestions?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                suggestionBox.innerHTML = '';
                currentSuggestions = data.suggestions || [];

                if (currentSuggestions.length === 0) {
                    suggestionBox.classList.remove('visible');
                    return;
                }

                currentSuggestions.forEach(suggestion => {
                    const item = document.createElement('li');
                    item.classList.add('suggestion-item');
                    item.textContent = suggestion;

                    item.addEventListener('click', () => {
                        input.value = suggestion;
                        suggestionBox.classList.remove('visible');
                        suggestionBox.innerHTML = '';
                        form.submit();
                    });

                    suggestionBox.appendChild(item);
                });

                suggestionBox.classList.add('visible');
            })
            .catch(err => {
                console.error('자동완성 오류:', err);
                suggestionBox.classList.remove('visible');
                suggestionBox.innerHTML = '';
            });
    });

    input.addEventListener('keydown', (e) => {
        const items = suggestionBox.querySelectorAll('.suggestion-item');
        if (items.length === 0) return;

        if (e.key === 'ArrowDown') {
            selectedIndex = (selectedIndex + 1) % items.length;
            updateHighlight(items);
            e.preventDefault();
        } else if (e.key === 'ArrowUp') {
            selectedIndex = (selectedIndex - 1 + items.length) % items.length;
            updateHighlight(items);
            e.preventDefault();
        } else if (e.key === 'Enter') {
            if (selectedIndex >= 0) {
                input.value = items[selectedIndex].textContent;
                suggestionBox.classList.remove('visible');
                suggestionBox.innerHTML = '';
                form.submit();
                e.preventDefault();
            }
        }
    });

    input.addEventListener('blur', () => {
        setTimeout(() => {
            suggestionBox.classList.remove('visible');
        }, 200);
    });

    function updateHighlight(items) {
        items.forEach((item, index) => {
            item.classList.toggle('highlighted', index === selectedIndex);
        });
    }
});


