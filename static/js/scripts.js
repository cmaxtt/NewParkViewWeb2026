/* ============================================
   Park View Drugs - JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {

    // ==========================================
    // MOBILE TOGGLE
    // ==========================================
    const mobileToggle = document.getElementById('mobileToggle');
    const mainNav = document.getElementById('mainNav');

    if (mobileToggle && mainNav) {
        mobileToggle.addEventListener('click', function() {
            mainNav.classList.toggle('open');
            mobileToggle.classList.toggle('active');
        });

        document.addEventListener('click', function(e) {
            if (!mainNav.contains(e.target) && !mobileToggle.contains(e.target)) {
                mainNav.classList.remove('open');
                mobileToggle.classList.remove('active');
            }
        });
    }

    // Mobile dropdown toggle
    document.querySelectorAll('.has-dropdown > a').forEach(function(link) {
        link.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                this.parentElement.classList.toggle('open');
            }
        });
    });

    // ==========================================
    // HERO CAROUSEL
    // ==========================================
    const track = document.getElementById('carouselTrack');
    const prevBtn = document.getElementById('carouselPrev');
    const nextBtn = document.getElementById('carouselNext');
    const dotsContainer = document.getElementById('carouselDots');

    if (track && dotsContainer) {
        const slides = track.querySelectorAll('.carousel-slide');
        const totalSlides = slides.length;
        let currentIndex = 0;
        let autoSlideInterval;
        const AUTO_INTERVAL = 5000;

        for (let i = 0; i < totalSlides; i++) {
            const dot = document.createElement('button');
            dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
            if (i === 0) dot.classList.add('active');
            dot.addEventListener('click', function() {
                goToSlide(i);
                resetAutoSlide();
            });
            dotsContainer.appendChild(dot);
        }

        function goToSlide(index) {
            currentIndex = index;
            track.style.transform = 'translateX(-' + (currentIndex * 100) + '%)';
            dotsContainer.querySelectorAll('button').forEach(function(dot, i) {
                dot.classList.toggle('active', i === currentIndex);
            });
        }

        function nextSlide() {
            currentIndex = (currentIndex + 1) % totalSlides;
            goToSlide(currentIndex);
        }

        function prevSlide() {
            currentIndex = (currentIndex - 1 + totalSlides) % totalSlides;
            goToSlide(currentIndex);
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

        // Touch/Swipe
        let touchStartX = 0;
        let touchEndX = 0;

        track.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        track.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            const diff = touchStartX - touchEndX;
            if (Math.abs(diff) > 50) {
                if (diff > 0) nextSlide();
                else prevSlide();
                resetAutoSlide();
            }
        }, { passive: true });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowLeft') { prevSlide(); resetAutoSlide(); }
            else if (e.key === 'ArrowRight') { nextSlide(); resetAutoSlide(); }
        });

        autoSlideInterval = setInterval(nextSlide, AUTO_INTERVAL);
    }

    // ==========================================
    // STORE MODAL
    // ==========================================
    window.openPharmacyFinder = function() {
        const modal = document.getElementById('pharmacyModal');
        if (modal) {
            modal.classList.add('open');
            document.body.style.overflow = 'hidden';
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

    // ==========================================
    // CONTACT FORM
    // ==========================================
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const btn = this.querySelector('button[type="submit"]');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            btn.disabled = true;
            setTimeout(function() {
                btn.innerHTML = '<i class="fas fa-check"></i> Message Sent!';
                setTimeout(function() {
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                }, 2000);
            }, 1500);
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ==========================================
    // SCROLL ANIMATIONS (fade-in)
    // ==========================================
    const fadeEls = document.querySelectorAll('.fade-in');
    if (fadeEls.length && 'IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });
        fadeEls.forEach(function(el) { observer.observe(el); });
    } else if (fadeEls.length) {
        // Fallback: show all
        fadeEls.forEach(function(el) { el.classList.add('visible'); });
    }

    console.log('%c Park View Drugs ', 'background: #1E7D29; color: white; font-size: 20px; font-weight: bold; padding: 8px 16px; border-radius: 4px;');
    console.log('%c Your Local Pharmacy in San Fernando ', 'color: #5C524C; font-size: 14px;');
});
