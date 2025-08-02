document.addEventListener('DOMContentLoaded', function() {
    // Handle donation amount selection
    const amountInputs = document.querySelectorAll('input[name="donationAmount"]');
    const customAmountInput = document.getElementById('amount');
    
    if (amountInputs.length > 0 && customAmountInput) {
        amountInputs.forEach(input => {
            input.addEventListener('change', function() {
                if (this.checked) {
                    customAmountInput.value = this.value;
                }
            });
        });
        
        customAmountInput.addEventListener('input', function() {
            // Uncheck any preset amount if custom amount is entered
            amountInputs.forEach(input => {
                input.checked = false;
            });
        });
    }
    
    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    if (flashMessages.length > 0) {
        setTimeout(function() {
            flashMessages.forEach(message => {
                const closeButton = message.querySelector('.btn-close');
                if (closeButton) {
                    closeButton.click();
                }
            });
        }, 5000);
    }
    
    // Product sorting functionality
    const sortSelect = document.getElementById('sortOrder');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const productCards = document.querySelectorAll('.product-card');
            const productContainer = document.querySelector('.row-cols-1');
            
            if (productCards.length > 0 && productContainer) {
                const productsArray = Array.from(productCards);
                
                switch(this.value) {
                    case 'priceAsc':
                        productsArray.sort((a, b) => {
                            const priceA = parseFloat(a.querySelector('.product-price').textContent.replace('$', ''));
                            const priceB = parseFloat(b.querySelector('.product-price').textContent.replace('$', ''));
                            return priceA - priceB;
                        });
                        break;
                    case 'priceDesc':
                        productsArray.sort((a, b) => {
                            const priceA = parseFloat(a.querySelector('.product-price').textContent.replace('$', ''));
                            const priceB = parseFloat(b.querySelector('.product-price').textContent.replace('$', ''));
                            return priceB - priceA;
                        });
                        break;
                    case 'nameAsc':
                        productsArray.sort((a, b) => {
                            const nameA = a.querySelector('.card-title').textContent;
                            const nameB = b.querySelector('.card-title').textContent;
                            return nameA.localeCompare(nameB);
                        });
                        break;
                    default:
                        // Default is newest, no need to sort
                        break;
                }
                
                // Re-append in the new order
                productsArray.forEach(card => {
                    const parentCol = card.closest('.col');
                    productContainer.appendChild(parentCol);
                });
            }
        });
    }
    
    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    if (forms.length > 0) {
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }
    
    // Image preview for pet registration
    const petImageInput = document.getElementById('image');
    const imagePreview = document.getElementById('image-preview');
    
    if (petImageInput && imagePreview) {
        petImageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                }
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    
    // Pet filter functionality
    const speciesFilter = document.getElementById('species');
    if (speciesFilter) {
        speciesFilter.addEventListener('change', function() {
            document.querySelector('form').submit();
        });
    }
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});
