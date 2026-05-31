/* ============================================
   MAIN JS - EXAM SYSTEM HOMEPAGE
   ============================================ */

// المنت‌های DOM
const loginBtn = document.getElementById('loginBtn');
const loginModal = document.getElementById('loginModal');
const modalClose = document.querySelector('.modal-close');
const getStartedBtn = document.getElementById('getStartedBtn');
const learnMoreBtn = document.getElementById('learnMoreBtn');
const registerBtn = document.getElementById('registerBtn');
const demoBtn = document.getElementById('demoBtn');
const signupLink = document.getElementById('signupLink');
const loginForm = document.getElementById('loginForm');
const snackbar = document.getElementById('snackbar');

// ========== توابع کمکی ==========
function showSnackbar(message, duration = 3000) {
    snackbar.textContent = message;
    snackbar.classList.add('show');
    setTimeout(() => {
        snackbar.classList.remove('show');
    }, duration);
}

function openModal() {
    loginModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    loginModal.classList.remove('active');
    document.body.style.overflow = '';
}

// ========== رویدادهای دکمه ورود ==========
loginBtn.addEventListener('click', openModal);

modalClose.addEventListener('click', closeModal);

loginModal.addEventListener('click', (e) => {
    if (e.target === loginModal) {
        closeModal();
    }
});

// ========== رویداد دکمه شروع ==========
getStartedBtn.addEventListener('click', () => {
    showSnackbar('برای شروع لطفاً وارد حساب کاربری خود شوید');
    setTimeout(openModal, 1500);
});

// ========== رویداد دکمه اطلاعات بیشتر ==========
learnMoreBtn.addEventListener('click', () => {
    const featuresSection = document.querySelector('.features-section');
    featuresSection.scrollIntoView({ behavior: 'smooth' });
});

// ========== رویداد دکمه ثبت‌نام ==========
registerBtn.addEventListener('click', () => {
    showSnackbar('فرم ثبت‌نام به زودی فعال می‌شود');
});

// ========== رویداد دکمه دمو ==========
demoBtn.addEventListener('click', () => {
    showSnackbar('برای دریافت دمو با پشتیبانی تماس بگیرید');
});

// ========== لینک ثبت‌نام در مودال ==========
signupLink.addEventListener('click', (e) => {
    e.preventDefault();
    closeModal();
    showSnackbar('فرم ثبت‌نام به زودی فعال می‌شود');
});

// ========== فرم ورود ==========
loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = loginForm.querySelector('input[type="email"]').value;
    const password = loginForm.querySelector('input[type="password"]').value;
    
    if (!email || !password) {
        showSnackbar('لطفاً ایمیل و رمز عبور را وارد کنید');
        return;
    }
    
    showSnackbar('در حال ورود به سامانه...');
    
    // شبیه‌سازی درخواست به سرور
    setTimeout(() => {
        showSnackbar('ورود با موفقیت انجام شد');
        closeModal();
        loginForm.reset();
        
        // تغییر متن دکمه ورود بعد از ورود
        loginBtn.innerHTML = '<i class="fas fa-user-check"></i><span>پنل کاربری</span>';
        loginBtn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
        
        // می‌توانید به صفحه داشبورد ریدایرکت کنید
        // window.location.href = '/dashboard/';
    }, 1500);
});

// ========== انیمیشن شمارنده آمار ==========
const statNumbers = document.querySelectorAll('.stat-number');

function animateNumbers() {
    statNumbers.forEach(el => {
        const target = parseInt(el.getAttribute('data-target'));
        const isPercent = el.innerText.includes('%');
        let current = 0;
        const increment = target / 50;
        
        const updateNumber = () => {
            current += increment;
            if (current < target) {
                el.innerText = Math.floor(current) + (isPercent ? '%' : '');
                requestAnimationFrame(updateNumber);
            } else {
                el.innerText = target + (isPercent ? '%' : '');
            }
        };
        
        updateNumber();
    });
}

// مشاهده بخش آمار با Intersection Observer
const statsSection = document.querySelector('.stats-section');
let numbersAnimated = false;

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting && !numbersAnimated) {
            numbersAnimated = true;
            animateNumbers();
        }
    });
}, { threshold: 0.5 });

if (statsSection) {
    observer.observe(statsSection);
}

// ========== افکت اسکرول برای هدر ==========
let lastScroll = 0;
const header = document.querySelector('.main-header');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    if (currentScroll > 100) {
        header.style.boxShadow = '0 10px 25px -5px rgba(0, 0, 0, 0.1)';
    } else {
        header.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.05)';
    }
    lastScroll = currentScroll;
});

// ========== دکمه ESC برای بستن مودال ==========
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && loginModal.classList.contains('active')) {
        closeModal();
    }
});

// ========== انیمیشن کارت‌های ویژگی هنگام اسکرول ==========
const featureCards = document.querySelectorAll('.feature-card');

const cardObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, { threshold: 0.2 });

featureCards.forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = 'all 0.5s ease';
    cardObserver.observe(card);
});

// ========== لینک‌های فوتر ==========
const footerLinks = document.querySelectorAll('.footer-links a');
footerLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        showSnackbar('این صفحه در حال آماده‌سازی است');
    });
});

console.log('سایت آماده است ✅');