// ==========================================
// ENHANCED PORTFOLIO INTERACTIONS
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    initializePortfolio();
});

function initializePortfolio() {
    initCustomCursor();
    initTypingEffect();
    initLandingInteractions();
    initPortfolioNavigation(); // This is the only nav function we need
    initScrollAnimations();
    initSkillBars();
    initChatbot();
    
    // Initially disable body scroll
    document.body.style.overflow = 'hidden';

    // *** FIX: Listen to the PORTFOLIO's scroll event for active links ***
    const portfolio = document.getElementById('portfolio');
    if (portfolio) {
        portfolio.addEventListener('scroll', updateActiveNavigation);
    }
}

// ==========================================
// CUSTOM CURSOR
// ==========================================
function initCustomCursor() {
    const cursor = document.querySelector('.cursor');
    const cursorFollower = document.querySelector('.cursor-follower');
    const hoverElements = document.querySelectorAll('a, button, .nav-item, .project-link, .contact-link, .cert-item, .stat-item, .skill-category, .project-item, .timeline-content, .chat-bubble, .chat-close, #chatSend');

    let mouseX = 0, mouseY = 0;
    let followerX = 0, followerY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        
        cursor.style.left = mouseX + 'px';
        cursor.style.top = mouseY + 'px';
    });

    // Smooth follower animation
    function animateFollower() {
        const speed = 0.2;
        followerX += (mouseX - followerX) * speed;
        followerY += (mouseY - followerY) * speed;
        
        cursorFollower.style.left = followerX + 'px';
        cursorFollower.style.top = followerY + 'px';
        
        requestAnimationFrame(animateFollower);
    }
    animateFollower();

    // Hover effects
    hoverElements.forEach(el => {
        el.addEventListener('mouseenter', () => {
            cursor.classList.add('large');
            cursorFollower.classList.add('large');
        });
        el.addEventListener('mouseleave', () => {
            cursor.classList.remove('large');
            cursorFollower.classList.remove('large');
        });
    });

    // Hide cursor on mobile
    if (window.innerWidth <= 768) {
        cursor.style.display = 'none';
        cursorFollower.style.display = 'none';
    }
}

// ==========================================
// TYPING EFFECT
// ==========================================
function initTypingEffect() {
    const typingElement = document.querySelector('.typing-text');
    if (!typingElement) return;

    const commands = [
        'whoami',
        'cat about.txt',
        'ls projects/',
        'grep skills cv.txt',
        'git status',
        'python -c "print(\'Hello World\')"',
        'pip install intelligence',
        'cd future && ls'
    ];

    let commandIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    const typingSpeed = 100;
    const deletingSpeed = 50;
    const pauseDuration = 700;

    function typeCommand() {
        const currentCommand = commands[commandIndex];
        
        if (!isDeleting && charIndex <= currentCommand.length) {
            typingElement.textContent = currentCommand.slice(0, charIndex);
            charIndex++;
            setTimeout(typeCommand, typingSpeed);
        } else if (isDeleting && charIndex >= 0) {
            typingElement.textContent = currentCommand.slice(0, charIndex);
            charIndex--;
            setTimeout(typeCommand, deletingSpeed);
        } else if (!isDeleting) {
            setTimeout(() => {
                isDeleting = true;
                typeCommand();
            }, pauseDuration);
        } else {
            isDeleting = false;
            commandIndex = (commandIndex + 1) % commands.length;
            charIndex = 0;
            setTimeout(typeCommand, 500);
        }
    }

    setTimeout(typeCommand, 1000);
}

// ==========================================
// LANDING PAGE INTERACTIONS
// ==========================================
function initLandingInteractions() {
    const landing = document.getElementById('landing');
    const portfolio = document.getElementById('portfolio');
    const enterBtn = document.getElementById('enterBtn');
    const closeBtn = document.getElementById('closeBtn');

    enterBtn.addEventListener('click', () => {
        landing.classList.add('hide');
        setTimeout(() => {
            portfolio.classList.add('show');
            document.body.style.overflow = 'auto'; 
            document.body.style.cursor = 'auto';
            triggerScrollAnimations();
        }, 600);
    });

    closeBtn.addEventListener('click', () => {
        portfolio.classList.remove('show');
        document.body.style.overflow = 'hidden';
        document.body.style.cursor = 'none';
        setTimeout(() => {
            landing.classList.remove('hide');
        }, 600);
    });
}

// ==========================================
// PORTFOLIO NAVIGATION (FIXED & CLEANED)
// ==========================================
function initPortfolioNavigation() {
    // This single listener handles all nav clicks robustly
    document.body.addEventListener('click', function(e) {
        
        // Find the closest link (or button) that has a 'data-section' attribute
        const navLink = e.target.closest('[data-section]');

        // If we didn't click on a nav link, do nothing
        if (!navLink) return;

        // ** THIS IS THE FIX **
        // We clicked a valid link, so prevent the default HTML jump (which changes the URL)
        e.preventDefault(); 

        const targetId = navLink.getAttribute('data-section');
        const targetSection = document.getElementById(targetId);
        
        if (targetSection) {
            const portfolio = document.getElementById('portfolio');
            const enterBtn = document.getElementById('enterBtn');
            
            // Check if we are on the landing page
            if (!portfolio.classList.contains('show')) {
                // If on landing, click 'Enter' first, then scroll after a delay
                enterBtn.click();
                setTimeout(() => {
                    scrollToSection(targetSection);
                }, 800); // Wait for portfolio to animate in
            } else {
                // If already in portfolio, just scroll
                scrollToSection(targetSection);
            }
        }
    });
}

// *** FIX: Scroll function that targets the .portfolio div ***
function scrollToSection(section) {
    const portfolioNav = document.querySelector('.portfolio-nav');
    const portfolio = document.getElementById('portfolio');
    
    if (!section || !portfolio || !portfolioNav) return;

    const navHeight = portfolioNav.offsetHeight;
    // Calculate position relative to the scrolling container (.portfolio)
    const elementPosition = section.offsetTop; 
    const offsetPosition = elementPosition - navHeight; // Adjust for fixed nav bar

    // Scroll the .portfolio div, not the window
    portfolio.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
}

// *** FIX: Update active navigation item based on PORTFOLIO scroll ***
function updateActiveNavigation() {
    const portfolio = document.getElementById('portfolio');
    const sections = document.querySelectorAll('.section');
    const navLinks = document.querySelectorAll('.portfolio-nav-links a[data-section]');
    const portfolioNav = document.querySelector('.portfolio-nav');
    
    if (!portfolio || !portfolioNav) return;

    const navHeight = portfolioNav.offsetHeight;
    // Get scroll position of the .portfolio div
    const scrollPosition = portfolio.scrollTop; 

    let currentSection = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop - navHeight - 50; // 50px buffer
        const sectionHeight = section.offsetHeight;
        
        if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            currentSection = section.id;
        }
    });

    // Update active nav link
    navLinks.forEach(link => {
        const linkSection = link.getAttribute('data-section');
        if (linkSection === currentSection) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// ==========================================
// SCROLL ANIMATIONS
// ==========================================
function initScrollAnimations() {
    const portfolio = document.getElementById('portfolio');
    
    const observerOptions = {
        root: portfolio, // *** FIX: Observe items within the .portfolio div ***
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                
                if (entry.target.classList.contains('stats-grid')) {
                    animateStatsGrid(entry.target);
                } else if (entry.target.classList.contains('timeline')) {
                    animateTimeline(entry.target);
                } else if (entry.target.classList.contains('skills-grid')) {
                    animateSkillsGrid(entry.target);
                } else if (entry.target.classList.contains('projects-grid')) {
                    animateProjectsGrid(entry.target);
                } else if (entry.target.classList.contains('certifications-grid')) {
                    animateCertificationsGrid(entry.target);
                } else if (entry.target.classList.contains('contact-text')) {
                    // Manually trigger siblings for contact section
                    document.querySelector('.contact-links')?.classList.add('visible');
                    document.querySelector('.contact-availability')?.classList.add('visible');
                }
            }
        });
    }, observerOptions);

    // Observe all animated elements
    document.querySelectorAll('.section-number, .section-title, .about-text, .about-image, .stats-grid, .timeline, .skills-grid, .projects-grid, .certifications-grid, .contact-text, .contact-links, .contact-availability').forEach(el => {
        observer.observe(el);
    });
}

function triggerScrollAnimations() {
    // Manually trigger the first section's elements on load
    document.querySelector('#about .section-number')?.classList.add('visible');
    document.querySelector('#about .section-title')?.classList.add('visible');
    document.querySelector('#about .about-text')?.classList.add('visible');
    document.querySelector('#about .about-image')?.classList.add('visible');
}

function animateStatsGrid(grid) {
    const items = grid.querySelectorAll('.stat-item');
    items.forEach((item, index) => {
        setTimeout(() => {
            item.classList.add('visible');
            animateCounter(item.querySelector('.stat-number'));
        }, index * 150);
    });
}

function animateTimeline(timeline) {
    const items = timeline.querySelectorAll('.timeline-item');
    items.forEach((item, index) => {
        setTimeout(() => {
            item.classList.add('visible');
        }, index * 200);
    });
}

function animateSkillsGrid(grid) {
    const categories = grid.querySelectorAll('.skill-category');
    categories.forEach((category, index) => {
        setTimeout(() => {
            category.classList.add('visible');
        }, index * 150);
    });
}

function animateProjectsGrid(grid) {
    const projects = grid.querySelectorAll('.project-item');
    projects.forEach((project, index) => {
        setTimeout(() => {
            project.classList.add('visible');
        }, index * 150);
    });
}

function animateCertificationsGrid(grid) {
    const certs = grid.querySelectorAll('.cert-item');
    certs.forEach((cert, index) => {
        setTimeout(() => {
            cert.classList.add('visible');
        }, index * 100);
    });
}

// ==========================================
// COUNTER ANIMATION
// ==========================================
function animateCounter(element) {
    if (!element) return;
    const target = parseFloat(element.textContent.replace(/[^\d.]/g, ''));
    if (isNaN(target)) return;

    const suffix = element.textContent.replace(/[\d.]/g, '');
    const duration = 2000;
    const increment = target / (duration / 16);
    let current = 0;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        
        if (target % 1 === 0) {
            element.textContent = Math.floor(current) + suffix;
        } else {
            element.textContent = current.toFixed(2) + suffix;
        }
    }, 16);
}

// ==========================================
// SKILL BARS ANIMATION
// ==========================================
function initSkillBars() {
    const portfolio = document.getElementById('portfolio');

    const observerOptions = {
        root: portfolio, // *** FIX: Observe within the .portfolio div ***
        threshold: 0.5
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const skillCategory = entry.target;
                const progressBars = skillCategory.querySelectorAll('.skill-progress');
                
                progressBars.forEach((bar, index) => {
                    const progress = bar.getAttribute('data-progress');
                    setTimeout(() => {
                        bar.style.setProperty('--progress', progress + '%');
                        bar.style.width = progress + '%';
                    }, index * 200);
                });
                observer.unobserve(skillCategory); // Animate only once
            }
        });
    }, observerOptions);

    document.querySelectorAll('.skill-category').forEach(category => {
        observer.observe(category);
    });
}

// ==========================================
// CHATBOT FUNCTIONALITY
// ==========================================
function initChatbot() {
    const chatBubble = document.getElementById('chatBubble');
    const chatWindow = document.getElementById('chatWindow');
    const chatClose = document.getElementById('chatClose');
    const chatInput = document.getElementById('chatInput');
    const chatSend = document.getElementById('chatSend');
    const chatBody = document.getElementById('chatBody');

    if (!chatBubble || !chatWindow || !chatClose || !chatInput || !chatSend || !chatBody) {
        console.warn('Chatbot elements not found.');
        return;
    }

    // Toggle chat window visibility
    chatBubble.addEventListener('click', () => {
        chatWindow.classList.toggle('active');
        chatInput.focus();
    });

    chatClose.addEventListener('click', () => {
        chatWindow.classList.remove('active');
    });

    // Send message on button click
    chatSend.addEventListener('click', sendMessage);

    // Send message on 'Enter' key press
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Main function to handle sending a message
    function sendMessage() {
        const userInput = chatInput.value.trim();
        if (userInput === '') return;

        addMessageToChat('user', userInput);
        chatInput.value = '';

        // Simulate bot thinking and get response
        setTimeout(() => {
            const botResponse = getBotResponse(userInput);
            addMessageToChat('bot', botResponse);
        }, 800);
    }

    // Function to add a new message to the chat body
    function addMessageToChat(sender, message) {
        const messageWrapper = document.createElement('div');
        messageWrapper.className = `chat-message ${sender}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Use marked.js to parse markdown for richer responses
        if (typeof marked !== 'undefined') {
            messageContent.innerHTML = marked.parse(message);
        } else {
            messageContent.textContent = message; // Fallback if marked.js fails
        }
        
        messageWrapper.appendChild(messageContent);
        chatBody.appendChild(messageWrapper);
        
        // Scroll to the latest message
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // Rule-based logic for the bot's responses
    function getBotResponse(input) {
        const i = input.toLowerCase();

        if (i.includes('hello') || i.includes('hi')) {
            return "Hello there! How can I help you learn more about Bhavya?";
        }

        if (i.includes('skill')) {
            return `Bhavya has a strong set of technical skills. His key areas include:
            - **Programming:** Python, SQL
            - **Machine Learning:** Scikit-learn, XGBoost, TensorFlow
            - **Data Viz:** Pandas, Matplotlib, Seaborn, Power BI
            - **Backend:** Flask, FastAPI
            - **AI & NLP:** NLTK, spaCy, Transformers
            
            You can see a more detailed list in the 'Skills' section!`;
        }

        if (i.includes('project')) {
            return `Bhavya has worked on over 15 projects! Some of the featured ones are:
            - **Customer Segmentation** using KMeans
            - **Flight Price Prediction** with 73% R² Score
            - **Smart Health Predictor** for diabetes
            - **Iris Classification** with 93% accuracy
            
            Would you like to know more about a specific one? You can also explore them all in the 'Projects' section.`;
        }
        
        if (i.includes('experience') || i.includes('internship')) {
            return `Bhavya has valuable internship experience:
            - **AI Intern at Bonrix Software Systems** (Current), where he's working with LLMs, Python, and Flask.
            - **Data Science Intern at Prodigy Infotech**, where he focused on data analysis and ML model development.`;
        }

        if (i.includes('education') || i.includes('college') || i.includes('gpa') || i.includes('cgpa')) {
            return "Bhavya is currently pursuing a B.Tech in Information Technology from Indus University (2022-2026). He maintains an excellent CGPA of **9.78**!";
        }
        
        if (i.includes('contact') || i.includes('email') || i.includes('linkedin') || i.includes('github')) {
            return `You can connect with Bhavya through several channels:
            - **Email:** [mistrybhavya9@gmail.com](mailto:mistrybhavya9@gmail.com)
            - **LinkedIn:** [linkedin.com/in/bhavya-mistry](https://www.linkedin.com/in/bhavya-mistry-5b5a57293/)
            - **GitHub:** [github.com/Bhavya-Mistry](https://github.com/Bhavya-Mistry)
            
            He's always open to new opportunities!`;
        }

        if (i.includes('resume') || i.includes('cv')) {
            return `Of course! You can download a copy of Bhavya's resume directly from the 'Contact' section of the portfolio or by clicking [here](Resume.pdf).`;
        }
        
        if (i.includes('thanks') || i.includes('thank you')) {
            return "You're welcome! Let me know if there's anything else you'd like to know.";
        }

        // Default response
        return "I'm not sure how to answer that. Could you try asking about Bhavya's skills, projects, experience, or education? You can also type 'contact' to see how to get in touch with him.";
    }
}