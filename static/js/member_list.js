// Member list functionality
document.addEventListener('DOMContentLoaded', function() {
    const featuredMembers = document.querySelectorAll('.featured-member');
    let currentIndex = 0;
    const totalMembers = featuredMembers.length;
    
    if (totalMembers <= 1) return;
    
    // Function to update member positions
    function updatePositions() {
        featuredMembers.forEach((member, index) => {
            member.classList.remove('active', 'back-1', 'back-2', 'rotating-in');
            
            if (index === currentIndex) {
                member.classList.add('active');
            } else if (index === (currentIndex - 1 + totalMembers) % totalMembers) {
                member.classList.add('back-1');
            } else if (index === (currentIndex + 1) % totalMembers) {
                member.classList.add('back-2');
            }
        });
    }
    
    // Handle click on back members
    featuredMembers.forEach((member, index) => {
        member.addEventListener('click', function() {
            if (this.classList.contains('back-1') || this.classList.contains('back-2')) {
                currentIndex = index;
                this.classList.add('rotating-in');
                updatePositions();
            }
        });
    });
    
    // Auto-rotate every 5 seconds
    setInterval(() => {
        currentIndex = (currentIndex + 1) % totalMembers;
        featuredMembers[currentIndex].classList.add('rotating-in');
        updatePositions();
    }, 5000);
    
    // Load more functionality
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
        let page = 2;
        loadMoreBtn.addEventListener('click', function() {
            fetch(`/members/?page=${page}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                const grid = document.querySelector('.members-grid');
                grid.insertAdjacentHTML('beforeend', data.html);
                
                if (!data.has_more) {
                    loadMoreBtn.style.display = 'none';
                }
                page++;
            });
        });
    }
});
