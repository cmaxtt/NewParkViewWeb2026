/* ==========================================================================
   Park View Drugs - Enhanced Client Scripts
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {

    // ======================================================================
    // 1. MOBILE MENU & DROPDOWN TOGGLE
    // ======================================================================
    const mobileToggle = document.getElementById('mobileToggle');
    const mainNav = document.getElementById('mainNav');

    if (mobileToggle && mainNav) {
        mobileToggle.addEventListener('click', function() {
            const isOpen = mainNav.classList.toggle('open');
            mobileToggle.classList.toggle('active', isOpen);
            mobileToggle.setAttribute('aria-expanded', String(isOpen));
        });

        document.addEventListener('click', function(e) {
            if (!mainNav.contains(e.target) && !mobileToggle.contains(e.target)) {
                mainNav.classList.remove('open');
                mobileToggle.classList.remove('active');
                mobileToggle.setAttribute('aria-expanded', 'false');
            }
        });
    }

    // Mobile dropdown touch toggle
    document.querySelectorAll('.has-dropdown > .nav-link').forEach(function(link) {
        link.addEventListener('click', function(e) {
            if (window.innerWidth <= 900) {
                e.preventDefault();
                const parent = this.parentElement;
                const wasOpen = parent.classList.contains('open');
                
                // Close other open dropdowns on mobile
                document.querySelectorAll('.has-dropdown.open').forEach(function(item) {
                    if (item !== parent) item.classList.remove('open');
                });

                parent.classList.toggle('open', !wasOpen);
                this.setAttribute('aria-expanded', String(!wasOpen));
            }
        });
    });

    // ======================================================================
    // 2. HERO CAROUSEL
    // ======================================================================
    const track = document.getElementById('carouselTrack');
    const prevBtn = document.getElementById('carouselPrev');
    const nextBtn = document.getElementById('carouselNext');
    const dotsContainer = document.getElementById('carouselDots');

    if (track && dotsContainer) {
        const slides = track.querySelectorAll('.carousel-slide');
        const totalSlides = slides.length;
        let currentIndex = 0;
        let autoSlideInterval;
        const AUTO_INTERVAL = 8000;

        // Build indicators
        dotsContainer.innerHTML = '';
        for (let i = 0; i < totalSlides; i++) {
            const dot = document.createElement('button');
            dot.type = 'button';
            dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
            dot.setAttribute('role', 'tab');
            if (i === 0) {
                dot.classList.add('active');
                dot.setAttribute('aria-selected', 'true');
            } else {
                dot.setAttribute('aria-selected', 'false');
            }
            dot.addEventListener('click', function() {
                goToSlide(i);
                resetAutoSlide();
            });
            dotsContainer.appendChild(dot);
        }

        function goToSlide(index) {
            currentIndex = (index + totalSlides) % totalSlides;
            track.style.transform = 'translateX(-' + (currentIndex * 100) + '%)';
            dotsContainer.querySelectorAll('button').forEach(function(dot, i) {
                const isActive = (i === currentIndex);
                dot.classList.toggle('active', isActive);
                dot.setAttribute('aria-selected', String(isActive));
            });
        }

        function nextSlide() {
            goToSlide(currentIndex + 1);
        }

        function prevSlide() {
            goToSlide(currentIndex - 1);
        }

        function resetAutoSlide() {
            clearInterval(autoSlideInterval);
            autoSlideInterval = setInterval(nextSlide, AUTO_INTERVAL);
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', function() {
                nextSlide();
                resetAutoSlide();
            });
        }
        if (prevBtn) {
            prevBtn.addEventListener('click', function() {
                prevSlide();
                resetAutoSlide();
            });
        }

        // Swipe support
        let touchStartX = 0;
        let touchEndX = 0;

        track.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        track.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            const diff = touchStartX - touchEndX;
            if (Math.abs(diff) > 45) {
                if (diff > 0) nextSlide();
                else prevSlide();
                resetAutoSlide();
            }
        }, { passive: true });

        // Keyboard arrow navigation
        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowLeft') { prevSlide(); resetAutoSlide(); }
            else if (e.key === 'ArrowRight') { nextSlide(); resetAutoSlide(); }
        });

        // Pause on hover
        track.addEventListener('mouseenter', function() { clearInterval(autoSlideInterval); });
        track.addEventListener('mouseleave', function() { resetAutoSlide(); });

        autoSlideInterval = setInterval(nextSlide, AUTO_INTERVAL);
    }

    // ======================================================================
    // 3. PHARMACY LOCATOR & DIRECTIONS MODAL
    // ======================================================================
    window.openPharmacyFinder = function() {
        const modal = document.getElementById('pharmacyModal');
        if (modal) {
            modal.classList.add('open');
            document.body.style.overflow = 'hidden';
            const closeBtn = modal.querySelector('.modal-close');
            if (closeBtn) closeBtn.focus();
        }
    };

    window.closePharmacyFinder = function() {
        const modal = document.getElementById('pharmacyModal');
        if (modal) {
            modal.classList.remove('open');
            document.body.style.overflow = '';
        }
    };

    const modalOverlay = document.getElementById('pharmacyModal');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', function(e) {
            if (e.target === this) closePharmacyFinder();
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modalOverlay.classList.contains('open')) {
                closePharmacyFinder();
            }
        });
    }

    // ======================================================================
    // 4. WEEKLY FLYER VIEW SWITCHER
    // ======================================================================
    const weeklyViewGrid = document.querySelector('[data-weekly-view-grid]');
    const weeklyViewButtons = document.querySelectorAll('[data-weekly-view]');
    if (weeklyViewGrid && weeklyViewButtons.length) {
        let selectedView = 'four';
        try {
            selectedView = localStorage.getItem('weeklyFlyerProductView') || 'four';
        } catch (error) {
            selectedView = 'four';
        }
        if (!['four', 'three', 'list'].includes(selectedView)) selectedView = 'four';

        function setWeeklyProductView(view) {
            weeklyViewGrid.dataset.view = view;
            weeklyViewButtons.forEach(function(button) {
                const isActive = (button.dataset.weeklyView === view);
                button.classList.toggle('is-active', isActive);
                button.setAttribute('aria-pressed', String(isActive));
            });
            try {
                localStorage.setItem('weeklyFlyerProductView', view);
            } catch (error) {}
        }

        weeklyViewButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                setWeeklyProductView(button.dataset.weeklyView);
            });
        });

        setWeeklyProductView(selectedView);
    }

    // ======================================================================
    // 5. SMOOTH SCROLL FOR IN-PAGE ANCHORS
    // ======================================================================
    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId && targetId !== '#') {
                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });

    // ======================================================================
    // 6. SCROLL FADE-IN ANIMATIONS
    // ======================================================================
    const fadeEls = document.querySelectorAll('.fade-in');
    if (fadeEls.length && 'IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12 });
        fadeEls.forEach(function(el) { observer.observe(el); });
    } else if (fadeEls.length) {
        fadeEls.forEach(function(el) { el.classList.add('visible'); });
    }

    console.log('%c Park View Drugs ', 'background: #0284C7; color: white; font-size: 18px; font-weight: 800; padding: 6px 14px; border-radius: 4px;');
    console.log('%c Professional Community Pharmacy - Esperance, San Fernando ', 'color: #D97706; font-size: 13px; font-weight: 600;');
});
