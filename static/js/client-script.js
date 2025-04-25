/**
 * Barberian Client Portal - Custom Scripts
 * Interactive elements and animations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations for elements with animation classes
    initAnimations();
    
    // Initialize scroll animations
    initScrollAnimations();
    
    // Initialize navbar effects
    initNavbarEffects();
    
    // Initialize service card hover effects
    initServiceCardEffects();
    
    // Initialize testimonial carousel if it exists
    if (document.querySelector('.testimonial-carousel')) {
        initTestimonialCarousel();
    }
    
    // Initialize form validations
    initFormValidations();
});

/**
 * Initialize animations for elements with animation classes
 */
function initAnimations() {
    // Add animation classes to elements with data-animation attribute
    const animatedElements = document.querySelectorAll('[data-animation]');
    
    animatedElements.forEach(element => {
        const animation = element.getAttribute('data-animation');
        const delay = element.getAttribute('data-delay');
        
        element.classList.add(animation);
        
        if (delay) {
            element.style.animationDelay = `${delay}s`;
        }
    });
}

/**
 * Initialize scroll animations
 */
function initScrollAnimations() {
    // Animate elements when they come into view
    const scrollElements = document.querySelectorAll('.scroll-animation');
    
    const elementInView = (el, dividend = 1) => {
        const elementTop = el.getBoundingClientRect().top;
        return (
            elementTop <= (window.innerHeight || document.documentElement.clientHeight) / dividend
        );
    };
    
    const displayScrollElement = element => {
        const animation = element.getAttribute('data-animation') || 'fade-in-up';
        element.classList.add(animation);
    };
    
    const hideScrollElement = element => {
        element.classList.remove('fade-in', 'fade-in-up', 'fade-in-left', 'fade-in-right');
    };
    
    const handleScrollAnimation = () => {
        scrollElements.forEach(element => {
            if (elementInView(element, 1.25)) {
                displayScrollElement(element);
            } else {
                hideScrollElement(element);
            }
        });
    };
    
    // Add event listener for scroll
    window.addEventListener('scroll', () => {
        handleScrollAnimation();
    });
    
    // Trigger once on load
    handleScrollAnimation();
}

/**
 * Initialize navbar effects
 */
function initNavbarEffects() {
    const navbar = document.querySelector('.navbar');
    
    if (!navbar) return;
    
    // Change navbar background on scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });
    
    // Add active class to current page nav link
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentLocation || currentLocation.startsWith(href)) {
            link.classList.add('active');
        }
    });
}

/**
 * Initialize service card hover effects
 */
function initServiceCardEffects() {
    const serviceCards = document.querySelectorAll('.service-card');
    
    serviceCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.querySelector('.btn').style.opacity = '1';
            card.querySelector('.btn').style.transform = 'translateY(0)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.querySelector('.btn').style.opacity = '0';
            card.querySelector('.btn').style.transform = 'translateY(20px)';
        });
    });
}

/**
 * Initialize testimonial carousel
 */
function initTestimonialCarousel() {
    const testimonialContainer = document.querySelector('.testimonial-carousel');
    const testimonials = testimonialContainer.querySelectorAll('.testimonial');
    const dotsContainer = document.querySelector('.carousel-dots');
    
    let currentIndex = 0;
    
    // Create dots
    testimonials.forEach((_, index) => {
        const dot = document.createElement('span');
        dot.classList.add('carousel-dot');
        if (index === 0) dot.classList.add('active');
        dot.addEventListener('click', () => {
            goToSlide(index);
        });
        dotsContainer.appendChild(dot);
    });
    
    // Show testimonial at index
    function showTestimonial(index) {
        testimonials.forEach((testimonial, i) => {
            testimonial.style.display = i === index ? 'block' : 'none';
            testimonial.style.opacity = i === index ? '1' : '0';
        });
        
        // Update dots
        const dots = dotsContainer.querySelectorAll('.carousel-dot');
        dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === index);
        });
    }
    
    // Go to specific slide
    function goToSlide(index) {
        currentIndex = index;
        showTestimonial(currentIndex);
    }
    
    // Next slide
    function nextSlide() {
        currentIndex = (currentIndex + 1) % testimonials.length;
        showTestimonial(currentIndex);
    }
    
    // Previous slide
    function prevSlide() {
        currentIndex = (currentIndex - 1 + testimonials.length) % testimonials.length;
        showTestimonial(currentIndex);
    }
    
    // Add navigation buttons
    const prevButton = document.querySelector('.carousel-prev');
    const nextButton = document.querySelector('.carousel-next');
    
    if (prevButton) prevButton.addEventListener('click', prevSlide);
    if (nextButton) nextButton.addEventListener('click', nextSlide);
    
    // Auto-advance slides every 5 seconds
    setInterval(nextSlide, 5000);
    
    // Show first testimonial
    showTestimonial(0);
}

/**
 * Initialize form validations
 */
function initFormValidations() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Add smooth scrolling for anchor links
 */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (!targetElement) return;
        
        window.scrollTo({
            top: targetElement.offsetTop - 80, // Adjust for navbar height
            behavior: 'smooth'
        });
    });
});

/**
 * Back to top button functionality
 */
const backToTopButton = document.querySelector('.back-to-top');

if (backToTopButton) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTopButton.classList.add('show');
        } else {
            backToTopButton.classList.remove('show');
        }
    });
    
    backToTopButton.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/**
 * Add parallax effect to hero section
 */
const heroSection = document.querySelector('.hero');

if (heroSection) {
    window.addEventListener('scroll', () => {
        const scrollPosition = window.scrollY;
        heroSection.style.backgroundPositionY = `${scrollPosition * 0.5}px`;
    });
}

/**
 * Add hover effects to buttons
 */
const buttons = document.querySelectorAll('.btn');

buttons.forEach(button => {
    button.addEventListener('mouseenter', () => {
        button.style.transform = 'translateY(-2px)';
        button.style.boxShadow = 'var(--shadow-md)';
    });
    
    button.addEventListener('mouseleave', () => {
        button.style.transform = '';
        button.style.boxShadow = '';
    });
    
    button.addEventListener('mousedown', () => {
        button.style.transform = 'translateY(0)';
    });
    
    button.addEventListener('mouseup', () => {
        button.style.transform = 'translateY(-2px)';
    });
});
