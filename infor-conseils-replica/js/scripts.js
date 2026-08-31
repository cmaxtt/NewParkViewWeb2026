/* ============================================================
   INFOR-Conseils — Main JavaScript
   ============================================================ */

(function() {
    'use strict';

    /* ============================================================
       Flexslider Carousel
       ============================================================ */
    function initSlider() {
        var slider = document.querySelector('.flexslider');
        if (!slider) return;

        var slides = slider.querySelectorAll('.slides li');
        var dotsContainer = slider.querySelector('.flex-control-nav');
        var prevBtn = slider.querySelector('.flex-prev');
        var nextBtn = slider.querySelector('.flex-next');
        var current = 0;
        var total = slides.length;
        var autoInterval;
        var autoDelay = 5000;

        if (total < 2) return;

        // Create dots
        if (dotsContainer) {
            for (var i = 0; i < total; i++) {
                var dot = document.createElement('li');
                var a = document.createElement('a');
                a.href = '#';
                a.setAttribute('data-slide', i);
                a.textContent = i + 1;
                if (i === 0) a.className = 'flex-active';
                dot.appendChild(a);
                dotsContainer.appendChild(dot);
            }
        }

        function showSlide(index) {
            for (var i = 0; i < total; i++) {
                slides[i].style.display = 'none';
            }
            slides[index].style.display = 'block';
            current = index;

            // Update dots
            var dots = dotsContainer ? dotsContainer.querySelectorAll('a') : [];
            for (var j = 0; j < dots.length; j++) {
                dots[j].className = '';
            }
            if (dots[index]) dots[index].className = 'flex-active';
        }

        function nextSlide() {
            var next = (current + 1) % total;
            showSlide(next);
        }

        function prevSlide() {
            var prev = (current - 1 + total) % total;
            showSlide(prev);
        }

        function startAutoPlay() {
            stopAutoPlay();
            autoInterval = setInterval(nextSlide, autoDelay);
        }

        function stopAutoPlay() {
            if (autoInterval) {
                clearInterval(autoInterval);
                autoInterval = null;
            }
        }

        function resetAutoPlay() {
            stopAutoPlay();
            startAutoPlay();
        }

        // Event listeners
        if (nextBtn) {
            nextBtn.addEventListener('click', function(e) {
                e.preventDefault();
                nextSlide();
                resetAutoPlay();
            });
        }

        if (prevBtn) {
            prevBtn.addEventListener('click', function(e) {
                e.preventDefault();
                prevSlide();
                resetAutoPlay();
            });
        }

        // Dot clicks
        if (dotsContainer) {
            dotsContainer.addEventListener('click', function(e) {
                var target = e.target;
                if (target.tagName === 'A' && target.hasAttribute('data-slide')) {
                    e.preventDefault();
                    var idx = parseInt(target.getAttribute('data-slide'));
                    if (idx !== current) {
                        showSlide(idx);
                        resetAutoPlay();
                    }
                }
            });
        }

        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowLeft') {
                prevSlide();
                resetAutoPlay();
            } else if (e.key === 'ArrowRight') {
                nextSlide();
                resetAutoPlay();
            }
        });

        // Touch/swipe support
        var touchStartX = 0;
        var touchEndX = 0;

        slider.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, {passive: true});

        slider.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            var diff = touchStartX - touchEndX;
            if (Math.abs(diff) > 50) {
                if (diff > 0) {
                    nextSlide();
                } else {
                    prevSlide();
                }
                resetAutoPlay();
            }
        }, {passive: true});

        // Start autoplay
        startAutoPlay();
    }

    /* ============================================================
       Mobile Navigation Toggle
       ============================================================ */
    function initMobileNav() {
        var toggle = document.querySelector('.nav-toggle');
        var menu = document.querySelector('.menu-navigation-container .menu');

        if (!toggle || !menu) return;

        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            menu.classList.toggle('open');
        });

        // Close menu on outside click
        document.addEventListener('click', function(e) {
            if (!toggle.contains(e.target) && !menu.contains(e.target)) {
                menu.classList.remove('open');
            }
        });
    }

    /* ============================================================
       Smooth Scroll for Anchor Links
       ============================================================ */
    function initSmoothScroll() {
        document.addEventListener('click', function(e) {
            var target = e.target;
            while (target && target.tagName !== 'A') {
                target = target.parentNode;
            }
            if (target && target.getAttribute('href') && target.getAttribute('href').charAt(0) === '#' && target.getAttribute('href').length > 1) {
                var hash = target.getAttribute('href');
                var el = document.querySelector(hash);
                if (el) {
                    e.preventDefault();
                    el.scrollIntoView({behavior: 'smooth', block: 'start'});
                }
            }
        });
    }

    /* ============================================================
       Fade-in Scroll Animations
       ============================================================ */
    function initFadeIn() {
        var elements = document.querySelectorAll('.fade-in');

        if (elements.length === 0) return;

        if ('IntersectionObserver' in window) {
            var observer = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                        observer.unobserve(entry.target);
                    }
                });
            }, {threshold: 0.15});

            elements.forEach(function(el) {
                observer.observe(el);
            });
        } else {
            // Fallback: show all
            elements.forEach(function(el) {
                el.classList.add('visible');
            });
        }
    }

    /* ============================================================
       Active Nav Highlight
       ============================================================ */
    function initActiveNav() {
        var currentPath = window.location.pathname;
        var navLinks = document.querySelectorAll('.menu-navigation-container .menu li a');

        navLinks.forEach(function(link) {
            var href = link.getAttribute('href');
            if (href) {
                // Remove domain part for comparison
                var cleanHref = href.replace(/^https?:\/\/[^\/]+/, '');
                if (cleanHref === currentPath || (cleanHref !== '/' && currentPath.indexOf(cleanHref) === 0)) {
                    link.classList.add('active');
                }
                // Home page
                if (currentPath === '/' || currentPath === '/index.html') {
                    if (cleanHref === '/' || cleanHref === '/index.html' || cleanHref === '') {
                        link.classList.add('active');
                    }
                }
            }
        });
    }

    /* ============================================================
       Initialize All
       ============================================================ */
    document.addEventListener('DOMContentLoaded', function() {
        initSlider();
        initMobileNav();
        initSmoothScroll();
        initFadeIn();
        initActiveNav();
    });

})();
