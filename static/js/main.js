document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle
    const burger = document.querySelector('.burger');
    const nav = document.querySelector('.nav-links');
    
    if (burger) {
        burger.addEventListener('click', function() {
            nav.classList.toggle('active');
            
            // Animate burger to X
            this.classList.toggle('toggle');
            
            // Prevent scrolling when nav is open
            document.body.classList.toggle('no-scroll');
        });
    }
    
    // Close mobile nav when link is clicked
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (nav.classList.contains('active')) {
                nav.classList.remove('active');
                burger.classList.remove('toggle');
                document.body.classList.remove('no-scroll');
            }
        });
    });
    
    // Scroll Animation for elements
    const fadeElements = document.querySelectorAll('.fade-in');
    
    function checkFade() {
        fadeElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150;
            
            if (elementTop < window.innerHeight - elementVisible) {
                element.classList.add('active');
            }
        });
    }
    
    // Animate stat numbers
    function animateStatNumbers() {
        const statNumbers = document.querySelectorAll('.stat-number');
        
        statNumbers.forEach(stat => {
            const targetValue = stat.textContent;
            const suffix = targetValue.replace(/[0-9.]/g, '');
            const value = parseFloat(targetValue);
            
            if (!isNaN(value)) {
                let startValue = 0;
                const duration = 2000;
                const increment = value / (duration / 16);
                
                const animateCount = () => {
                    startValue += increment;
                    if (startValue < value) {
                        if (Number.isInteger(value)) {
                            stat.textContent = Math.floor(startValue) + suffix;
                        } else {
                            stat.textContent = startValue.toFixed(1) + suffix;
                        }
                        requestAnimationFrame(animateCount);
                    } else {
                        stat.textContent = targetValue;
                    }
                };
                
                const observer = new IntersectionObserver((entries) => {
                    if (entries[0].isIntersecting) {
                        requestAnimationFrame(animateCount);
                        observer.disconnect();
                    }
                });
                
                observer.observe(stat);
            }
        });
    }
    
    // Check elements on load
    checkFade();
    
    // Check elements on scroll
    window.addEventListener('scroll', checkFade);
    
    // Animate stat numbers when they come into view
    animateStatNumbers();
    
    // File Upload Handling
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.querySelector('.file-input');
    const uploadBtn = document.querySelector('.upload-btn');
    const resultsContainer = document.querySelector('.results-container');
    
    if (uploadArea && fileInput) {
        // Click on upload area to trigger file input
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        // Handle drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('active');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('active');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('active');
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                updateFileName(e.dataTransfer.files[0].name);
            }
        });
        
        // Update file name when file selected
        fileInput.addEventListener('change', (e) => {
            if (fileInput.files.length) {
                updateFileName(fileInput.files[0].name);
            }
        });
        
        // Display selected file name
        function updateFileName(name) {
            const fileNameDisplay = document.querySelector('.file-name');
            if (fileNameDisplay) {
                fileNameDisplay.textContent = name;
                fileNameDisplay.style.display = 'block';
            }
        }
        
        // Handle file upload
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => {
                if (!fileInput.files.length) {
                    alert('Please select a file first');
                    return;
                }
                
                const file = fileInput.files[0];
                const formData = new FormData();
                formData.append('file', file);
                
                // Show loading state with button animation
                uploadBtn.innerHTML = '<span class="spinner"></span> Processing...';
                uploadBtn.disabled = true;
                
                // Send file to server
                fetch('/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    // Reset button state
                    uploadBtn.innerHTML = 'Upload Wafer Image';
                    uploadBtn.disabled = false;
                    
                    // Display results with animation
                    if (resultsContainer) {
                        resultsContainer.style.opacity = '0';
                        resultsContainer.style.display = 'block';
                        
                        displayResults(data);
                        
                        setTimeout(() => {
                            resultsContainer.style.opacity = '1';
                            resultsContainer.style.transform = 'translateY(0)';
                        }, 50);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    uploadBtn.innerHTML = 'Upload Wafer Image';
                    uploadBtn.disabled = false;
                    alert('An error occurred during upload. Please try again.');
                });
            });
        }
        
        // Display results from server
        function displayResults(data) {
            const filenameElement = document.querySelector('.result-filename');
            const defectsElement = document.querySelector('.result-defects');
            const accuracyElement = document.querySelector('.result-accuracy');
            const imagePreview = document.querySelector('.image-preview');
            
            if (filenameElement) {
                filenameElement.textContent = data.filename || 'Unknown';
            }
            
            if (defectsElement) {
                defectsElement.textContent = data.prediction || 'N/A';
            }
            
            if (accuracyElement) {
                accuracyElement.textContent = data.confidence || 'N/A';
            }

            // Display uploaded image preview
            if (imagePreview && data.filename) {
                imagePreview.innerHTML = `<img src="/static/uploads/${data.filename}" alt="Uploaded wafer" style="max-width: 100%; height: auto;">`;
                imagePreview.style.display = 'block';
            }
        }
    }
    
    // Navbar scroll behavior
    const header = document.querySelector('header');
    let lastScroll = 0;
    
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll <= 0) {
            header.classList.remove('scroll-up');
            return;
        }
        
        if (currentScroll > lastScroll && !header.classList.contains('scroll-down')) {
            // Scroll Down
            header.classList.remove('scroll-up');
            header.classList.add('scroll-down');
        } else if (currentScroll < lastScroll && header.classList.contains('scroll-down')) {
            // Scroll Up
            header.classList.remove('scroll-down');
            header.classList.add('scroll-up');
        }
        
        lastScroll = currentScroll;
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add burger menu animation styles
    const style = document.createElement('style');
    style.textContent = `
        .burger.toggle div:nth-child(1) {
            transform: rotate(-45deg) translate(-5px, 6px);
        }
        
        .burger.toggle div:nth-child(2) {
            opacity: 0;
        }
        
        .burger.toggle div:nth-child(3) {
            transform: rotate(45deg) translate(-5px, -6px);
        }
        
        .no-scroll {
            overflow: hidden;
        }
        
        .scroll-down {
            transform: translateY(-100%);
        }
        
        .scroll-up {
            transform: translateY(0);
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        }
        
        header {
            transition: transform 0.3s ease;
        }
        
        .fade-in {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.8s ease, transform 0.8s ease;
        }
        
        .fade-in.active {
            opacity: 1;
            transform: translateY(0);
        }
        
        .upload-area.active {
            background-color: rgba(216, 207, 188, 0.2);
            border-color: var(--secondary-color);
        }
        
        .results-container {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.5s ease, transform 0.5s ease;
        }
        
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
            margin-right: 8px;
            vertical-align: middle;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);

    // Fade-in animation
    const fadeInObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('appear');
                fadeInObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });
    
    fadeElements.forEach(element => {
        fadeInObserver.observe(element);
    });
    
    // Update active nav link based on current page
    const currentPage = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-links li a');
    
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href === currentPage || 
            (currentPage === '/' && href === '/') ||
            (currentPage === '/about' && href === '#about')) {
            item.classList.add('active');
        }
    });
    
    // Handle hash navigation
    const hashLinks = document.querySelectorAll('a[href^="#"]');
    
    hashLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Only prevent default if on the same page
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                e.preventDefault();
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
                
                // Update URL hash without scrolling
                history.pushState(null, null, `#${targetId}`);
            }
        });
    });
});