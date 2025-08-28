// Theme Switcher for PyLadies Seoul Website
class ThemeSwitcher {
    constructor() {
        // Get current theme from document attribute (already set by inline script)
        this.theme = document.documentElement.getAttribute('data-theme') || this.getStoredTheme() || 'light';
        this.init();
    }

    init() {
        // Theme is already applied by inline script, just sync UI
        console.log('Current theme from document:', this.theme);
        
        // Create theme switcher button if it doesn't exist
        this.createThemeSwitcherButton();
        
        // Listen for theme changes
        this.bindEvents();
        
        // Listen for system theme changes
        this.listenForSystemThemeChanges();
    }

    createThemeSwitcherButton() {
        // Switches are now in HTML, just update their state
        this.updateSwitchState();
        console.log('Theme switches found in HTML, updated state');
    }

    styleButton(button) {
        Object.assign(button.style, {
            background: 'var(--bg-component)',
            border: '2px solid var(--brand-red)',
            borderRadius: '50%',
            width: '50px',
            height: '50px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.2rem',
            color: 'var(--color-text-primary)',
            transition: 'all var(--transition-base)',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
        });

        button.addEventListener('mouseenter', () => {
            button.style.transform = 'scale(1.1)';
            button.style.backgroundColor = 'var(--brand-red)';
            button.style.color = 'var(--color-text-white)';
        });

        button.addEventListener('mouseleave', () => {
            button.style.transform = 'scale(1)';
            button.style.backgroundColor = 'var(--bg-component)';
            button.style.color = 'var(--color-text-primary)';
        });
    }

    getButtonIcon() {
        return this.theme === 'light' 
            ? '🌙' // Moon for switching to dark
            : '☀️'; // Sun for switching to light
    }

    bindEvents() {
        const checkbox = document.getElementById('theme-checkbox');
        const mobileCheckbox = document.getElementById('theme-checkbox-mobile');
        
        if (checkbox) {
            checkbox.addEventListener('change', (e) => this.handleCheckboxChange(e));
            console.log('Desktop theme checkbox event bound');
        }
        
        if (mobileCheckbox) {
            mobileCheckbox.addEventListener('change', (e) => this.handleCheckboxChange(e));
            console.log('Mobile theme checkbox event bound');
        }
    }

    handleCheckboxChange(event) {
        const isChecked = event.target.checked;
        const newTheme = isChecked ? 'dark' : 'light';
        
        this.theme = newTheme;
        console.log('Checkbox changed, setting theme to:', this.theme);
        
        this.applyTheme(this.theme);
        this.syncCheckboxes();
        this.storeTheme(this.theme);
    }

    toggleTheme() {
        // Simple toggle for backward compatibility
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        console.log('Toggling theme to:', this.theme);
        this.applyTheme(this.theme);
        this.syncCheckboxes();
        this.storeTheme(this.theme);
    }

    syncCheckboxes() {
        const checkbox = document.getElementById('theme-checkbox');
        const mobileCheckbox = document.getElementById('theme-checkbox-mobile');
        const isDark = this.theme === 'dark';
        
        if (checkbox) {
            checkbox.checked = isDark;
        }
        if (mobileCheckbox) {
            mobileCheckbox.checked = isDark;
        }
        
        console.log('Synced both checkboxes to:', this.theme);
    }

    applyTheme(theme) {
        console.log('Applying theme:', theme);
        document.documentElement.setAttribute('data-theme', theme);
        console.log('Document data-theme attribute set to:', document.documentElement.getAttribute('data-theme'));
        
        // Also update meta theme-color for mobile browsers
        this.updateMetaThemeColor(theme);
    }

    updateMetaThemeColor(theme) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        
        const themeColors = {
            light: '#fcd5ce',
            dark: '#2d1b1b'
        };
        
        metaThemeColor.content = themeColors[theme];
    }

    updateSwitchState() {
        const checkbox = document.getElementById('theme-checkbox');
        const mobileCheckbox = document.getElementById('theme-checkbox-mobile');
        const isDark = this.theme === 'dark';
        
        if (checkbox) {
            checkbox.checked = isDark;
        }
        
        if (mobileCheckbox) {
            mobileCheckbox.checked = isDark;
        }
        
        console.log('Updated switch state to:', this.theme);
    }

    updateButton() {
        // Keep for backward compatibility, now just calls updateSwitchState
        this.updateSwitchState();
    }

    storeTheme(theme) {
        try {
            localStorage.setItem('pyladies-theme', theme);
        } catch (e) {
            console.warn('Unable to save theme preference:', e);
        }
    }

    getStoredTheme() {
        try {
            return localStorage.getItem('pyladies-theme');
        } catch (e) {
            console.warn('Unable to load theme preference:', e);
            return null;
        }
    }

    getSystemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    listenForSystemThemeChanges() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addEventListener('change', (e) => {
            // Only auto-switch if user hasn't manually set a preference
            if (!this.getStoredTheme()) {
                this.theme = e.matches ? 'dark' : 'light';
                this.applyTheme(this.theme);
                this.updateButton();
            }
        });
    }
}

// Initialize theme switcher when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.themeSwitcher = new ThemeSwitcher();
});

// Also initialize immediately if DOM is already loaded
if (document.readyState === 'loading') {
    // DOM is still loading
} else {
    // DOM is already loaded
    window.themeSwitcher = new ThemeSwitcher();
}