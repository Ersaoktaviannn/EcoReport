
/**
 * EcoReport Application JavaScript
 * Main application functionality and interactions
 */

class EcoReportApp {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.initializeComponents();
        this.loadData();
    }

    bindEvents() {
        // Form validations
        this.setupFormValidation();
        
        // Navigation enhancements
        this.setupNavigation();
        
        // Interactive elements
        this.setupInteractivity();
        
        // Auto-refresh for dashboard
        this.setupAutoRefresh();
    }

    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });

        // Real-time validation
        const inputs = document.querySelectorAll('.form-control');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('.form-control[required]');
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        let isValid = true;
        let message = '';

        // Required field check
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            message = 'Field ini wajib diisi';
        }

        // Email validation
        if (type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                message = 'Format email tidak valid';
            }
        }

        // Password validation
        if (type === 'password' && value) {
            if (value.length < 6) {
                isValid = false;
                message = 'Password minimal 6 karakter';
            }
        }

        // Phone validation
        if (field.name === 'phone' && value) {
            const phoneRegex = /^[0-9+\-\s()]+$/;
            if (!phoneRegex.test(value)) {
                isValid = false;
                message = 'Format nomor telepon tidak valid';
            }
        }

        this.showFieldValidation(field, isValid, message);
        return isValid;
    }

    showFieldValidation(field, isValid, message) {
        const feedback = field.parentNode.querySelector('.invalid-feedback') || 
                        this.createFeedbackElement();
        
        if (!isValid) {
            field.classList.add('is-invalid');
            field.classList.remove('is-valid');
            feedback.textContent = message;
            if (!field.parentNode.contains(feedback)) {
                field.parentNode.appendChild(feedback);
            }
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            if (field.parentNode.contains(feedback)) {
                feedback.remove();
            }
        }
    }

    createFeedbackElement() {
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        return feedback;
    }

    setupNavigation() {
        // Active link highlighting
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });

        // Smooth scrolling
        const scrollLinks = document.querySelectorAll('a[href^="#"]');
        scrollLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    setupInteractivity() {
        // Card hover effects
        const cards = document.querySelectorAll('.card-custom');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-8px)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
            });
        });

        // Button loading states
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                if (button.type === 'submit') {
                    this.showLoadingState(button);
                }
            });
        });

        // Auto-hide alerts
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.style.opacity = '0';
                    setTimeout(() => alert.remove(), 300);
                }
            }, 5000);
        });

        // Tooltip initialization
        this.initializeTooltips();
    }

    setupAutoRefresh() {
        // Auto-refresh dashboard stats every 30 seconds
        if (window.location.pathname === '/') {
            setInterval(() => {
                this.refreshDashboardStats();
            }, 30000);
        }
    }

    showLoadingState(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        button.disabled = true;

        // Reset after 3 seconds (fallback)
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
        }, 3000);
    }

    initializeTooltips() {
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => {
            new bootstrap.Tooltip(tooltip);
        });
    }

    refreshDashboardStats() {
        fetch('/api/reports/stats')
            .then(response => response.json())
            .then(data => {
                this.updateDashboardStats(data);
            })
            .catch(error => {
                console.error('Error refreshing stats:', error);
            });
    }

    updateDashboardStats(data) {
        // Update statistics if elements exist
        const totalElement = document.querySelector('.stats-total');
        const pendingElement = document.querySelector('.stats-pending');
        const resolvedElement = document.querySelector('.stats-resolved');

        if (totalElement) totalElement.textContent = data.total;
        if (pendingElement) pendingElement.textContent = data.by_status.pending;
        if (resolvedElement) resolvedElement.textContent = data.by_status.resolved;
    }

    loadData() {
        // Load additional data when needed
        this.loadRecentReports();
        this.loadUserPreferences();
    }

    loadRecentReports() {
        const recentContainer = document.querySelector('.recent-reports');
        if (!recentContainer) return;

        fetch('/api/reports/recent')
            .then(response => response.json())
            .then(data => {
                this.renderRecentReports(data);
            })
            .catch(error => {
                console.error('Error loading recent reports:', error);
            });
    }

    renderRecentReports(reports) {
        const container = document.querySelector('.recent-reports');
        if (!container) return;

        const html = reports.map(report => `
            <div class="card card-custom mb-3 priority-${report.priority}">
                <div class="card-body">
                    <h6 class="card-title">${report.title}</h6>
                    <p class="card-text text-muted small">
                        <i class="fas fa-map-marker-alt"></i> ${report.location}
                    </p>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="badge status-${report.status}">${report.status}</span>
                        <small class="text-muted">${this.formatDate(report.created_at)}</small>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    loadUserPreferences() {
        const preferences = localStorage.getItem('ecoreport_preferences');
        if (preferences) {
            const prefs = JSON.parse(preferences);
            this.applyUserPreferences(prefs);
        }
    }

    applyUserPreferences(preferences) {
        // Apply theme
        if (preferences.theme === 'dark') {
            document.body.classList.add('dark-theme');
        }

        // Apply notification settings
        if (preferences.notifications) {
            this.enableNotifications();
        }
    }

    enableNotifications() {
        if ('Notification' in window) {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    console.log('Notifications enabled');
                }
            });
        }
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('id-ID', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        });
    }

    // Utility functions
    static showNotification(title, message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-custom alert-dismissible fade show`;
        notification.innerHTML = `
            <strong>${title}</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('.container') || document.body;
        container.insertBefore(notification, container.firstChild);

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    static formatNumber(number) {
        return new Intl.NumberFormat('id-ID').format(number);
    }

    static debounce(func, wait) {
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
}

// Geolocation utilities
class GeolocationHelper {
    static getCurrentPosition() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation tidak didukung browser ini'));
                return;
            }

            navigator.geolocation.getCurrentPosition(resolve, reject, {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000
            });
        });
    }

    static async fillLocationInputs() {
        try {
            const position = await this.getCurrentPosition();
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            document.getElementById('latitude').value = latitude.toFixed(6);
            document.getElementById('longitude').value = longitude.toFixed(6);

            EcoReportApp.showNotification('Sukses', 'Lokasi berhasil dideteksi!', 'success');
        } catch (error) {
            EcoReportApp.showNotification('Error', error.message, 'warning');
        }
    }
}

// Chart utilities
class ChartHelper {
    static createPieChart(elementId, data, options = {}) {
        const ctx = document.getElementById(elementId);
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                ...options
            }
        });
    }

    static createBarChart(elementId, data, options = {}) {
        const ctx = document.getElementById(elementId);
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                ...options
            }
        });
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.ecoReportApp = new EcoReportApp();
});

// Service Worker registration (for PWA)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
