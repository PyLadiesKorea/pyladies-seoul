// Contact page functionality
(function() {
    'use strict';
    
    // Bootstrap form validation
    window.addEventListener('load', function() {
        const forms = document.getElementsByClassName('needs-validation');
        Array.prototype.forEach.call(forms, function(form) {
            form.addEventListener('submit', function(event) {
                if (form.checkValidity() === false) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }, false);
    
    // Auto-resize textarea
    document.addEventListener('DOMContentLoaded', function() {
        const textarea = document.getElementById('id_message');
        if (textarea) {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
            });
        }
    });
})();
