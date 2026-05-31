/* ============================================
   LOGIN PAGE JS - FORM VALIDATION & INTERACTIONS
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    // المنت‌ها
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const togglePasswordBtn = document.getElementById('togglePassword');
    const submitBtn = document.getElementById('submitBtn');
    const guestBtn = document.getElementById('guestBtn');
    const forgotLink = document.getElementById('forgotLink');
    const registerLink = document.getElementById('registerLink');
    const forgotModal = document.getElementById('forgotModal');
    const modalClose = document.querySelector('.modal-close');
    const resetBtn = document.getElementById('resetBtn');
    const resetEmail = document.getElementById('resetEmail');
    const snackbar = document.getElementById('snackbar');
    const rememberCheckbox = document.getElementById('remember');

    // ========== توابع کمکی ==========
    function showSnackbar(message, type = 'error') {
        snackbar.textContent = message;
        snackbar.classList.add('show');
        if (type === 'error') {
            snackbar.classList.add('error');
        } else if (type === 'success') {
            snackbar.classList.add('success');
        }
        
        setTimeout(() => {
            snackbar.classList.remove('show');
            snackbar.classList.remove('error', 'success');
        }, 3000);
    }

    function showError(input, message) {
        const errorDiv = input.parentElement.querySelector('.input-error') || 
                        document.getElementById(input.id + 'Error');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.add('show');
            input.classList.add('error');
        }
    }

    function clearError(input) {
        const errorDiv = input.parentElement.querySelector('.input-error') ||
                        document.getElementById(input.id + 'Error');
        if (errorDiv) {
            errorDiv.classList.remove('show');
            input.classList.remove('error');
        }
    }

    function validateEmail(email) {
        const re = /^[^\s@]+@([^\s@.,]+\.)+[^\s@.,]{2,}$/;
        return re.test(email);
    }

    function validateUsername(username) {
        if (username.length < 3) {
            return 'نام کاربری باید حداقل 3 کاراکتر باشد';
        }
        if (username.length > 50) {
            return 'نام کاربری نمی‌تواند بیشتر از 50 کاراکتر باشد';
        }
        return null;
    }

    function validatePassword(password) {
        if (password.length < 6) {
            return 'رمز عبور باید حداقل 6 کاراکتر باشد';
        }
        if (password.length > 100) {
            return 'رمز عبور نمی‌تواند بیشتر از 100 کاراکتر باشد';
        }
        return null;
    }

    // ========== اعتبارسنجی فرم ==========
    function validateForm() {
        let isValid = true;
        const username = usernameInput.value.trim();
        const password = passwordInput.value;

        // اعتبارسنجی نام کاربری
        if (!username) {
            showError(usernameInput, 'لطفاً نام کاربری یا ایمیل خود را وارد کنید');
            isValid = false;
        } else if (!validateEmail(username) && username.length < 3) {
            showError(usernameInput, 'لطفاً نام کاربری معتبر یا ایمیل صحیح وارد کنید');
            isValid = false;
        } else {
            clearError(usernameInput);
        }

        // اعتبارسنجی رمز عبور
        if (!password) {
            showError(passwordInput, 'لطفاً رمز عبور خود را وارد کنید');
            isValid = false;
        } else if (password.length < 6) {
            showError(passwordInput, 'رمز عبور باید حداقل 6 کاراکتر باشد');
            isValid = false;
        } else {
            clearError(passwordInput);
        }

        return isValid;
    }

    // ========== ذخیره اطلاعات در localStorage ==========
    function saveCredentials(username, password, remember) {
        if (remember) {
            localStorage.setItem('saved_username', username);
            localStorage.setItem('saved_password', btoa(password)); // رمزنگاری ساده
            localStorage.setItem('remember_me', 'true');
        } else {
            localStorage.removeItem('saved_username');
            localStorage.removeItem('saved_password');
            localStorage.removeItem('remember_me');
        }
    }

    function loadSavedCredentials() {
        const remember = localStorage.getItem('remember_me');
        if (remember === 'true') {
            const savedUsername = localStorage.getItem('saved_username');
            if (savedUsername) {
                usernameInput.value = savedUsername;
                rememberCheckbox.checked = true;
            }
        }
    }

    // ========== شبیه‌سازی درخواست لاگین به سرور ==========
    async function sendLoginRequest(username, password) {
        // اینجا می‌توانید درخواست AJAX به سرور خود ارسال کنید
        // مثال با fetch:
        /*
        try {
            const response = await fetch('/api/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ username, password })
            });
            const data = await response.json();
            if (response.ok) {
                return { success: true, data };
            } else {
                return { success: false, error: data.message };
            }
        } catch (error) {
            return { success: false, error: 'خطا در ارتباط با سرور' };
        }
        */

        // شبیه‌سازی درخواست (برای دمو)
        return new Promise((resolve) => {
            setTimeout(() => {
                if (username === 'admin' || (username === 'test@example.com' && password === '123456')) {
                    resolve({ success: true, message: 'ورود با موفقیت انجام شد' });
                } else {
                    resolve({ success: false, message: 'نام کاربری یا رمز عبور اشتباه است' });
                }
            }, 1000);
        });
    }

    // ========== لاگین کردن ==========
    async function handleLogin(e) {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }

        const username = usernameInput.value.trim();
        const password = passwordInput.value;
        const remember = rememberCheckbox.checked;

        // ذخیره اطلاعات اگر مرا به خاطر بسپار فعال باشد
        saveCredentials(username, password, remember);

        // تغییر状态 دکمه
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> در حال ورود...';
        submitBtn.disabled = true;

        // ارسال درخواست
        const result = await sendLoginRequest(username, password);

        // بازگرداندن دکمه
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;

        if (result.success) {
            showSnackbar(result.message, 'success');
            
            // ذخیره توکن یا اطلاعات کاربر در sessionStorage
            sessionStorage.setItem('isLoggedIn', 'true');
            sessionStorage.setItem('username', username);
            
            // ریدایرکت به صفحه اصلی یا داشبورد بعد از 1 ثانیه
            setTimeout(() => {
                window.location.href = '/dashboard/'; // آدرس داشبورد خود را وارد کنید
            }, 1000);
        } else {
            showSnackbar(result.message, 'error');
            passwordInput.value = '';
            passwordInput.focus();
        }
    }

    // ========== نمایش/مخفی کردن رمز عبور ==========
    function togglePassword() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        const icon = togglePasswordBtn.querySelector('i');
        icon.classList.toggle('fa-eye');
        icon.classList.toggle('fa-eye-slash');
    }

    // ========== ورود مهمان ==========
    function guestLogin() {
        showSnackbar('در حال ورود به حالت مهمان...', 'success');
        setTimeout(() => {
            sessionStorage.setItem('isGuest', 'true');
            window.location.href = '/exam/'; // آدرس صفحه آزمون مهمان
        }, 1000);
    }

    // ========== مودال فراموشی رمز ==========
    function openForgotModal() {
        forgotModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeForgotModal() {
        forgotModal.classList.remove('active');
        document.body.style.overflow = '';
        resetEmail.value = '';
    }

    function sendResetLink() {
        const email = resetEmail.value.trim();
        if (!email) {
            showSnackbar('لطفاً ایمیل خود را وارد کنید', 'error');
            return;
        }
        if (!validateEmail(email)) {
            showSnackbar('لطفاً یک ایمیل معتبر وارد کنید', 'error');
            return;
        }
        
        showSnackbar('لینک بازیابی به ایمیل شما ارسال شد', 'success');
        setTimeout(() => {
            closeForgotModal();
        }, 2000);
    }

    // ========== ثبت‌نام ==========
    function goToRegister() {
        showSnackbar('در حال انتقال به صفحه ثبت‌نام...', 'success');
        setTimeout(() => {
            window.location.href = '/register/'; // آدرس صفحه ثبت‌نام
        }, 500);
    }

    // ========== ورود با کلید Enter ==========
    function handleEnterKey(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleLogin(e);
        }
    }

    // ========== رویدادهای ورودی ==========
    usernameInput.addEventListener('input', () => clearError(usernameInput));
    passwordInput.addEventListener('input', () => clearError(passwordInput));
    usernameInput.addEventListener('keypress', handleEnterKey);
    passwordInput.addEventListener('keypress', handleEnterKey);

    // ========== رویدادها ==========
    loginForm.addEventListener('submit', handleLogin);
    togglePasswordBtn.addEventListener('click', togglePassword);
    guestBtn.addEventListener('click', guestLogin);
    forgotLink.addEventListener('click', (e) => {
        e.preventDefault();
        openForgotModal();
    });
    registerLink.addEventListener('click', (e) => {
        e.preventDefault();
        goToRegister();
    });
    modalClose.addEventListener('click', closeForgotModal);
    resetBtn.addEventListener('click', sendResetLink);
    
    // کلیک خارج از مودال
    forgotModal.addEventListener('click', (e) => {
        if (e.target === forgotModal) {
            closeForgotModal();
        }
    });

    // دکمه ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && forgotModal.classList.contains('active')) {
            closeForgotModal();
        }
    });

    // بارگذاری اطلاعات ذخیره شده
    loadSavedCredentials();

    // افکت ورود با انیمیشن
    const loginCard = document.querySelector('.login-card');
    if (loginCard) {
        loginCard.style.opacity = '0';
        loginCard.style.transform = 'translateY(20px)';
        setTimeout(() => {
            loginCard.style.transition = 'all 0.5s ease';
            loginCard.style.opacity = '1';
            loginCard.style.transform = 'translateY(0)';
        }, 100);
    }

    console.log('صفحه لاگین آماده است ✅');
});