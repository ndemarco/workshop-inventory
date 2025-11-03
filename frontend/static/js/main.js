// Main JavaScript for Inventory System

// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
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
