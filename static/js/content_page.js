// Track page view for content pages
function trackPageView(pageId) {
    fetch('/api/track-view/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: 'page_id=' + pageId
    }).catch(err => console.log('View tracking failed:', err));
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get page ID from data attribute or global variable
    const pageId = document.querySelector('[data-page-id]')?.dataset.pageId;
    if (pageId) {
        trackPageView(pageId);
    }
});
