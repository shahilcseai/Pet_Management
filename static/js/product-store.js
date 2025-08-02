// product-store.js - Handles product store functionality

document.addEventListener('DOMContentLoaded', function() {
    // Product sort functionality
    const sortSelect = document.getElementById('sortOrder');
    const productGrid = document.querySelector('.row.row-cols-1.row-cols-md-2.row-cols-lg-3');
    
    if (sortSelect && productGrid) {
        sortSelect.addEventListener('change', function() {
            const products = Array.from(productGrid.children);
            
            // Sort products based on selection
            switch (this.value) {
                case 'priceAsc':
                    sortProductsByPrice(products, 'asc');
                    break;
                case 'priceDesc':
                    sortProductsByPrice(products, 'desc');
                    break;
                case 'nameAsc':
                    sortProductsByName(products, 'asc');
                    break;
                case 'nameDesc':
                    sortProductsByName(products, 'desc');
                    break;
                default:
                    // Default to newest first (no sorting needed as that's the default)
                    break;
            }
            
            // Reappend sorted elements
            products.forEach(product => {
                productGrid.appendChild(product);
            });
        });
    }
    
    function sortProductsByPrice(products, direction) {
        products.sort((a, b) => {
            const priceA = parseFloat(a.querySelector('.product-price').textContent.replace('$', ''));
            const priceB = parseFloat(b.querySelector('.product-price').textContent.replace('$', ''));
            
            return direction === 'asc' ? priceA - priceB : priceB - priceA;
        });
    }
    
    function sortProductsByName(products, direction) {
        products.sort((a, b) => {
            const nameA = a.querySelector('.card-title').textContent;
            const nameB = b.querySelector('.card-title').textContent;
            
            return direction === 'asc' 
                ? nameA.localeCompare(nameB) 
                : nameB.localeCompare(nameA);
        });
    }
    
    // Category filter functionality
    const categoryLinks = document.querySelectorAll('.list-group-item-action');
    
    if (categoryLinks.length > 0) {
        categoryLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                // Remove active class from all links
                categoryLinks.forEach(l => l.classList.remove('active'));
                
                // Add active class to clicked link
                this.classList.add('active');
            });
        });
    }
    
    // Add to cart functionality
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    
    if (addToCartButtons.length > 0) {
        addToCartButtons.forEach(button => {
            button.addEventListener('click', function() {
                const productId = this.getAttribute('data-product-id');
                const productName = this.getAttribute('data-product-name');
                
                // Show confirmation message
                showCartConfirmation(productName);
                
                // In a real implementation, you would add the item to the cart
                // Here we're just showing a notification
            });
        });
    }
    
    function showCartConfirmation(productName) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'toast show position-fixed bottom-0 end-0 m-3';
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-live', 'assertive');
        notification.setAttribute('aria-atomic', 'true');
        
        notification.innerHTML = `
            <div class="toast-header bg-primary text-white">
                <i class="fas fa-shopping-cart me-2"></i>
                <strong class="me-auto">Item Added</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${productName} has been added to your cart.
            </div>
        `;
        
        // Append to body
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 500);
        }, 3000);
    }
});
