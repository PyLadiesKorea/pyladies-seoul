// Member detail page functionality

// Share functionality
function shareProfile() {
    if (navigator.share) {
        navigator.share({
            title: document.title,
            text: '님의 프로필을 확인해보세요!',
            url: window.location.href
        });
    } else {
        // Fallback to copy URL
        navigator.clipboard.writeText(window.location.href).then(() => {
            alert('Profile URL copied to clipboard!');
        });
    }
}

// Make shareProfile function globally available
window.shareProfile = shareProfile;
