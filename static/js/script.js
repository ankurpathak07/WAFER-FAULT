// Navbar behavior
document.addEventListener('DOMContentLoaded', function() {
    const header = document.querySelector('header');
    const burger = document.querySelector('.burger');
    const navLinks = document.querySelector('.nav-links');
    
    // Check initial scroll position when page loads
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
    
    // Add scroll event listener
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // Mobile menu toggle
    if (burger) {
        burger.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            burger.classList.toggle('active');
        });
    }

    // Close mobile menu when clicking a link
    const navItems = document.querySelectorAll('.nav-links a');
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            navLinks.classList.remove('active');
            burger.classList.remove('active');
        });
    });
}); 