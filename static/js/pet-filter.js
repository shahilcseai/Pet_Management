// pet-filter.js - Handles pet listing filters and search

document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('pet-search-form');
    const speciesFilter = document.getElementById('species');
    const searchInput = document.getElementById('query');
    const clearButton = document.getElementById('clear-filters');
    
    // Submit form when species filter changes
    if (speciesFilter) {
        speciesFilter.addEventListener('change', function() {
            if (searchForm) {
                searchForm.submit();
            }
        });
    }
    
    // Clear all filters
    if (clearButton) {
        clearButton.addEventListener('click', function(e) {
            e.preventDefault();
            if (searchInput) {
                searchInput.value = '';
            }
            if (speciesFilter) {
                speciesFilter.value = '';
            }
            if (searchForm) {
                searchForm.submit();
            }
        });
    }
    
    // Age range filter if implemented
    const ageRange = document.getElementById('age-range');
    const ageOutput = document.getElementById('age-output');
    
    if (ageRange && ageOutput) {
        ageRange.addEventListener('input', function() {
            // Update the displayed value
            const value = this.value;
            let displayText = '';
            
            if (value < 12) {
                displayText = `${value} months`;
            } else {
                const years = Math.floor(value / 12);
                displayText = `${years} year${years !== 1 ? 's' : ''}`;
            }
            
            ageOutput.textContent = displayText;
        });
    }
    
    // Advanced search toggle
    const advancedSearchToggle = document.getElementById('advanced-search-toggle');
    const advancedSearchOptions = document.getElementById('advanced-search-options');
    
    if (advancedSearchToggle && advancedSearchOptions) {
        advancedSearchToggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Toggle visibility
            if (advancedSearchOptions.classList.contains('d-none')) {
                advancedSearchOptions.classList.remove('d-none');
                this.innerHTML = 'Simple Search <i class="fas fa-chevron-up"></i>';
            } else {
                advancedSearchOptions.classList.add('d-none');
                this.innerHTML = 'Advanced Search <i class="fas fa-chevron-down"></i>';
            }
        });
    }
});
