// donation.js - Handles donation form functionality

document.addEventListener('DOMContentLoaded', function() {
    const donationForm = document.getElementById('donation-form');
    const donationButtons = document.querySelectorAll('.donation-preset');
    const customAmountInput = document.getElementById('amount');
    
    // Set preset amounts when buttons are clicked
    if (donationButtons.length > 0 && customAmountInput) {
        donationButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Get the amount from data attribute
                const amount = this.getAttribute('data-amount');
                
                // Set the amount in the input field
                customAmountInput.value = amount;
                
                // Highlight active button
                donationButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
            });
        });
        
        // Clear active buttons when custom amount is entered
        customAmountInput.addEventListener('input', function() {
            donationButtons.forEach(btn => btn.classList.remove('active'));
        });
    }
    
    // Form validation
    if (donationForm) {
        donationForm.addEventListener('submit', function(event) {
            if (!validateDonationForm()) {
                event.preventDefault();
            }
        });
    }
    
    // Donation form validation
    function validateDonationForm() {
        const amount = parseFloat(customAmountInput.value);
        
        if (isNaN(amount) || amount <= 0) {
            // Show error for invalid amount
            customAmountInput.classList.add('is-invalid');
            return false;
        } else {
            customAmountInput.classList.remove('is-invalid');
            return true;
        }
    }
    
    // Payment method selection
    const paymentMethods = document.querySelectorAll('input[name="paymentMethod"]');
    const paymentDetails = document.getElementById('payment-details');
    
    if (paymentMethods.length > 0 && paymentDetails) {
        paymentMethods.forEach(method => {
            method.addEventListener('change', function() {
                updatePaymentForm(this.id);
            });
        });
        
        // Initial setup based on default selection
        const defaultMethod = document.querySelector('input[name="paymentMethod"]:checked');
        if (defaultMethod) {
            updatePaymentForm(defaultMethod.id);
        }
    }
    
    function updatePaymentForm(methodId) {
        // This function would show/hide different payment form fields
        // based on the selected payment method
        console.log(`Payment method selected: ${methodId}`);
        
        // In a real implementation, you would manipulate the DOM to show
        // the appropriate fields for each payment method
    }
});
