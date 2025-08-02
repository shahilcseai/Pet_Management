// form-validation.js - Handles form validation across the site

document.addEventListener('DOMContentLoaded', function() {
    // Add Bootstrap's validation classes to all forms with 'needs-validation' class
    const forms = document.querySelectorAll('.needs-validation');
    
    if (forms.length > 0) {
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                
                form.classList.add('was-validated');
            }, false);
        });
    }
    
    // Custom validation for registration form
    const registrationForm = document.getElementById('registration-form');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    
    if (registrationForm && passwordInput && confirmPasswordInput) {
        // Check password match
        confirmPasswordInput.addEventListener('input', function() {
            validatePasswordMatch(passwordInput, confirmPasswordInput);
        });
        
        passwordInput.addEventListener('input', function() {
            validatePasswordMatch(passwordInput, confirmPasswordInput);
        });
        
        // Check password strength
        passwordInput.addEventListener('input', function() {
            validatePasswordStrength(this);
        });
        
        // Form submission validation
        registrationForm.addEventListener('submit', function(event) {
            // Validate password match
            if (!validatePasswordMatch(passwordInput, confirmPasswordInput)) {
                event.preventDefault();
            }
            
            // Validate password strength
            if (!validatePasswordStrength(passwordInput)) {
                event.preventDefault();
            }
        });
    }
    
    function validatePasswordMatch(password, confirmPassword) {
        if (password.value !== confirmPassword.value) {
            confirmPassword.setCustomValidity("Passwords do not match");
            return false;
        } else {
            confirmPassword.setCustomValidity("");
            return true;
        }
    }
    
    function validatePasswordStrength(password) {
        // Simple password strength validation
        const value = password.value;
        
        // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
        const hasLength = value.length >= 8;
        const hasUpperCase = /[A-Z]/.test(value);
        const hasLowerCase = /[a-z]/.test(value);
        const hasNumber = /[0-9]/.test(value);
        
        const isStrong = hasLength && hasUpperCase && hasLowerCase && hasNumber;
        
        if (!isStrong) {
            password.setCustomValidity("Password must be at least 8 characters and include uppercase, lowercase, and numbers");
            return false;
        } else {
            password.setCustomValidity("");
            return true;
        }
    }
    
    // Pet form validation
    const petForm = document.getElementById('pet-form');
    const petImageInput = document.getElementById('image');
    const imagePreview = document.getElementById('image-preview');
    
    if (petForm && petImageInput && imagePreview) {
        // Preview image when selected
        petImageInput.addEventListener('change', function() {
            previewImage(this, imagePreview);
        });
    }
    
    function previewImage(input, previewElement) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                previewElement.src = e.target.result;
                previewElement.classList.remove('d-none');
            }
            
            reader.readAsDataURL(input.files[0]);
        }
    }
});
