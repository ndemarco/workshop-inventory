// Main JavaScript for Inventory System

// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide banners (replacement for alerts)
    const banners = document.querySelectorAll('.banner');
    banners.forEach(b => {
        setTimeout(() => {
            b.style.opacity = '0';
            b.style.transition = 'opacity 0.5s';
            setTimeout(() => b.remove(), 500);
        }, 5000);
    });

    // Dismiss handlers for banners
    document.querySelectorAll('.banner-close').forEach(btn => {
        btn.addEventListener('click', function() {
            const el = this.closest('.banner');
            if (el) el.remove();
        });
    });
});

// Confirm delete actions
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

// Dynamic location selector
// This can be expanded in future phases for smarter location suggestions
function initLocationSelector() {
    const moduleSelect = document.getElementById('module_select');
    const levelSelect = document.getElementById('level_select');
    const locationSelect = document.getElementById('location_select');
    
    if (!moduleSelect || !levelSelect || !locationSelect) return;
    
    moduleSelect.addEventListener('change', async function() {
        const moduleId = this.value;
        if (!moduleId) {
            levelSelect.innerHTML = '<option value="">Select level...</option>';
            locationSelect.innerHTML = '<option value="">Select location...</option>';
            return;
        }
        
        // Fetch levels for selected module
        const response = await fetch(`/modules/api/modules/${moduleId}/levels`);
        const levels = await response.json();
        
        levelSelect.innerHTML = '<option value="">Select level...</option>';
        levels.forEach(level => {
            const option = document.createElement('option');
            option.value = level.id;
            option.textContent = `Level ${level.level_number}${level.name ? ' - ' + level.name : ''}`;
            levelSelect.appendChild(option);
        });
        
        locationSelect.innerHTML = '<option value="">Select location...</option>';
    });
    
    levelSelect.addEventListener('change', async function() {
        const levelId = this.value;
        if (!levelId) {
            locationSelect.innerHTML = '<option value="">Select location...</option>';
            return;
        }
        
        // Fetch locations for selected level
        const response = await fetch(`/locations/api/locations?level_id=${levelId}`);
        const locations = await response.json();
        
        locationSelect.innerHTML = '<option value="">Select location...</option>';
        locations.forEach(location => {
            const option = document.createElement('option');
            option.value = location.id;
            const occupied = location.item_count > 0 ? ' (Occupied)' : '';
            option.textContent = `${location.full_address}${occupied}`;
            locationSelect.appendChild(option);
        });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initLocationSelector();
});

// Utility to show a banner message programmatically
function showBanner(message, type = 'info', { timeout = 5000, containerSelector = '#banners' } = {}) {
    const container = document.querySelector(containerSelector) || (function() {
        const main = document.querySelector('main.container');
        const c = document.createElement('div');
        c.id = 'banners';
        c.className = 'banners-container';
        if (main) main.insertBefore(c, main.firstChild);
        return c;
    })();

    const banner = document.createElement('div');
    banner.className = `banner banner-${type}`;
    const content = document.createElement('div');
    content.className = 'banner-content';
    // Preserve newlines as <br>
    content.innerHTML = String(message).replace(/\n/g, '<br>');
    const close = document.createElement('button');
    close.className = 'banner-close';
    close.setAttribute('aria-label', 'Dismiss');
    close.innerHTML = '&times;';
    close.addEventListener('click', () => banner.remove());

    banner.appendChild(content);
    banner.appendChild(close);
    container.appendChild(banner);

    if (timeout > 0) {
        setTimeout(() => {
            banner.style.opacity = '0';
            banner.style.transition = 'opacity 0.4s';
            setTimeout(() => banner.remove(), 400);
        }, timeout);
    }
    return banner;
}
