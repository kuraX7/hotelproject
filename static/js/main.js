// ===== AL ANDALUS HOTEL — MAIN JS =====

document.addEventListener('DOMContentLoaded', function () {

    // --- Navbar scroll effect ---
    const navbar = document.getElementById('mainNavbar');
    if (navbar) {
        const handleScroll = () => {
            if (window.scrollY > 60) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        };
        window.addEventListener('scroll', handleScroll, { passive: true });
        handleScroll();
    }

    // --- Active nav link ---
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
            link.style.color = 'var(--gold)';
        }
    });

    // --- Auto-dismiss alerts ---
    document.querySelectorAll('.custom-alert').forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // --- Smooth scroll for anchor links ---
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                const navbarH = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--navbar-h')) || 90;
                const top = target.getBoundingClientRect().top + window.pageYOffset - navbarH;
                window.scrollTo({ top, behavior: 'smooth' });
            }
        });
    });

    // --- Intersection Observer: fade-in on scroll ---
    const fadeEls = document.querySelectorAll(
        '.room-card-premium, .amenity-card, .testimonial-card, .stat-card, .spec-card'
    );
    if ('IntersectionObserver' in window && fadeEls.length) {
        fadeEls.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        });

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, i) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, 80);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12 });

        fadeEls.forEach(el => observer.observe(el));
    }

    // --- Image lazy load fallback ---
    document.querySelectorAll('img[loading="lazy"]').forEach(img => {
        img.addEventListener('error', function () {
            this.src = 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=600&q=80';
        });
    });

    // --- Booking date constraints ---
    const today = new Date().toISOString().split('T')[0];
    document.querySelectorAll('input[type="date"]').forEach(input => {
        if (!input.min) input.min = today;
    });

    const checkInInputs = document.querySelectorAll('[name="check_in"], #qb-checkin, #avail-checkin');
    checkInInputs.forEach(input => {
        input.addEventListener('change', function () {
            const checkOutSelectors = ['[name="check_out"]', '#qb-checkout', '#avail-checkout'];
            checkOutSelectors.forEach(sel => {
                const co = document.querySelector(sel);
                if (co) co.min = this.value;
            });
        });
    });

    // --- Form validation UI ---
    const forms = document.querySelectorAll('form[novalidate]');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // --- Sticky filter bar offset correction ---
    const stickyFilter = document.querySelector('.sticky-filter');
    if (stickyFilter) {
        // Lit la variable CSS --navbar-h au lieu d'une valeur codée en dur
        const navbarH = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--navbar-h')) || 90;
        stickyFilter.style.top = navbarH + 'px';
    }

    // --- Tooltip init (Bootstrap) ---
    const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipEls.forEach(el => new bootstrap.Tooltip(el));
});

// ── FAQ Accordion (global) ─────────────────────────
function toggleFaq(btn) {
  const answer = btn.nextElementSibling;
  const icon   = btn.querySelector('.faq-icon');
  const isOpen = btn.classList.contains('open');
  const col    = btn.closest('.col-lg-6') || btn.closest('.faq-col') || document;
  col.querySelectorAll('.faq-question.open').forEach(b => {
    if (b !== btn) {
      b.classList.remove('open');
      b.nextElementSibling.classList.remove('open');
      b.querySelector('.faq-icon').classList.remove('rotated');
    }
  });
  btn.classList.toggle('open', !isOpen);
  answer.classList.toggle('open', !isOpen);
  icon.classList.toggle('rotated', !isOpen);
}
