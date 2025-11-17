
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type} show`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Validate email format
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Validate password strength
function validatePassword(password) {
    // At least 8 characters, one uppercase, one lowercase, one number
    const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
    return re.test(password);
}

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Debounce function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Toggle password visibility
function togglePasswordVisibility(inputId, buttonId) {
    const input = document.getElementById(inputId);
    const button = document.getElementById(buttonId);
    
    if (input.type === 'password') {
        input.type = 'text';
        button.textContent = 'Hide';
    } else {
        input.type = 'password';
        button.textContent = 'Show';
    }
}

// Set up CSRF token for AJAX requests (if needed)
function setupCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    if (token) {
        window.csrfToken = token.getAttribute('content');
    }
}

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    // Setup CSRF token if present
    setupCSRFToken();
    
    // Add form element animations
    const formElements = document.querySelectorAll('input, textarea, select');
    formElements.forEach(element => {
        element.classList.add('form-element');
    });
    
    // Add button hover effects
    const buttons = document.querySelectorAll('button, .btn');
    buttons.forEach(button => {
        button.classList.add('btn-hover');
    });
});