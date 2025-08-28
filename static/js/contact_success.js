// Contact success page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Auto-redirect after 10 seconds (optional)
    setTimeout(function() {
        const redirectNotice = document.createElement('div');
        redirectNotice.className = 'alert alert-info mt-4';
        redirectNotice.innerHTML = '<i class="fas fa-clock"></i> Redirecting to homepage in 10 seconds...';
        const container = document.querySelector('.container .row .col-lg-6');
        if (container) {
            container.appendChild(redirectNotice);
        }
    }, 10000);

    // Actual redirect after 20 seconds
    setTimeout(function() {
        window.location.href = '/';
    }, 20000);
});
