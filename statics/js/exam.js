// static/js/exam-timer.js
// با قابلیت ذخیره خودکار و ثبت خودکار

document.addEventListener('DOMContentLoaded', function() {
    console.log("Exam timer with auto-save loaded");
    
    // دریافت زمان باقیمانده
    let remainingSeconds = 0;
    const timerElement = document.getElementById('timer');
    if (timerElement && timerElement.dataset.remainingSeconds) {
        remainingSeconds = parseInt(timerElement.dataset.remainingSeconds);
    }
    
    if (isNaN(remainingSeconds) || remainingSeconds <= 0) {
        console.error("No valid remaining seconds found");
        remainingSeconds = 3600; // 1 ساعت پیش‌فرض
    }
    
    const examForm = document.getElementById('examForm');
    if (!examForm) {
        console.error("Exam form not found");
        return;
    }
    
    let timerInterval = null;
    let autoSaveInterval = null;
    let isSubmitting = false;
    let hasAutoSaved = false;
    const AUTO_SAVE_INTERVAL = 10 * 60 * 1000; // 10 دقیقه به میلی‌ثانیه
    
    // ========== توابع کمکی ==========
    
    function formatTime(seconds) {
        if (isNaN(seconds) || seconds < 0) seconds = 0;
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) {
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
    function updateDisplay() {
        if (timerElement) {
            timerElement.textContent = formatTime(remainingSeconds);
            
            // تغییر رنگ در زمان کم
            if (remainingSeconds <= 300 && remainingSeconds > 0) {
                timerElement.classList.add('timer-warning');
            } else {
                timerElement.classList.remove('timer-warning');
            }
            
            // بروزرسانی title صفحه
            const originalTitle = document.title.replace(/^\([0-9:]+\)\s*/, '');
            document.title = `(${formatTime(remainingSeconds)}) ${originalTitle || 'Exam'}`;
        }
    }
    
    // ========== تابع ذخیره خودکار ==========
    async function autoSaveAnswers() {
        if (isSubmitting) return;
        
        console.log("Auto-saving answers...");
        
        // جمع‌آوری پاسخ‌ها از فرم
        const formData = new FormData(examForm);
        formData.append('auto_save', 'true'); // علامت برای تشخیص ذخیره خودکار
        
        try {
            const response = await fetch(examForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest' // برای تشخیص درخواست AJAX
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log("Auto-save successful:", data);
                
                // نمایش نوتیفیکیشن
                showNotification('پاسخ‌ها با موفقیت ذخیره شد', 'success');
                hasAutoSaved = true;
            } else {
                console.error("Auto-save failed:", response.status);
                showNotification('خطا در ذخیره خودکار', 'error');
            }
        } catch (error) {
            console.error("Auto-save error:", error);
            showNotification('خطا در ارتباط با سرور', 'error');
        }
    }
    
    // ========== تابع ثبت نهایی ==========
    async function finalSubmit() {
        if (isSubmitting) return;
        isSubmitting = true;
        
        console.log("Final auto-submit triggered");
        
        if (timerInterval) clearInterval(timerInterval);
        if (autoSaveInterval) clearInterval(autoSaveInterval);
        
        if (timerElement) {
            timerElement.textContent = 'در حال ثبت...';
        }
        
        try {
            // ثبت نهایی فرم
            const formData = new FormData(examForm);
            formData.append('final_submit', 'true');
            
            const response = await fetch(examForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log("Final submit successful:", data);
                showNotification('آزمون با موفقیت ثبت شد', 'success');
                
                // هدایت به صفحه نتیجه یا ریفرش
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else {
                    // غیرفعال کردن فرم
                    disableForm();
                    alert('زمان آزمون به پایان رسید. پاسخ‌های شما ثبت شد.');
                    window.location.reload();
                }
            } else {
                console.error("Final submit failed");
                alert('خطا در ثبت آزمون. لطفاً با پشتیبانی تماس بگیرید.');
                isSubmitting = false;
            }
        } catch (error) {
            console.error("Final submit error:", error);
            alert('خطا در ثبت آزمون. لطفاً با پشتیبانی تماس بگیرید.');
            isSubmitting = false;
        }
    }
    
    function disableForm() {
        const inputs = examForm.querySelectorAll('input, textarea, select, button');
        inputs.forEach(input => {
            input.disabled = true;
        });
    }
    
    function showNotification(message, type = 'info') {
        // حذف نوتیفیکیشن قبلی
        const existingNotif = document.querySelector('.auto-save-notification');
        if (existingNotif) existingNotif.remove();
        
        // ایجاد نوتیفیکیشن جدید
        const notification = document.createElement('div');
        notification.className = `auto-save-notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 9999;
            animation: slideIn 0.3s ease;
            ${type === 'success' ? 'background: linear-gradient(135deg, #10b981, #059669);' : 'background: linear-gradient(135deg, #ef4444, #dc2626);'}
        `;
        
        document.body.appendChild(notification);
        
        // حذف بعد از ۳ ثانیه
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    // ========== توابع تایمر ==========
    function handleExpiry() {
        console.log("Timer expired! Auto-submitting...");
        
        if (timerInterval) clearInterval(timerInterval);
        if (autoSaveInterval) clearInterval(autoSaveInterval);
        
        finalSubmit();
    }
    
    function startTimer() {
        if (remainingSeconds <= 0) {
            handleExpiry();
            return;
        }
        
        updateDisplay();
        
        timerInterval = setInterval(() => {
            if (remainingSeconds <= 0) {
                handleExpiry();
            } else {
                remainingSeconds--;
                updateDisplay();
                
                // ذخیره خودکار در لحظات پایانی (۱۰ ثانیه آخر)
                if (remainingSeconds === 10 && !hasAutoSaved) {
                    autoSaveAnswers();
                }
                
                if (remainingSeconds === 0) {
                    handleExpiry();
                }
            }
        }, 1000);
    }
    
    // ========== شروع ذخیره خودکار ==========
    function startAutoSave() {
        // ذخیره خودکار اولیه بعد از ۱۰ دقیقه
        autoSaveInterval = setInterval(() => {
            if (!isSubmitting && remainingSeconds > 0) {
                autoSaveAnswers();
            }
        }, AUTO_SAVE_INTERVAL);
        
        // همچنین ذخیره خودکار هنگام خروج از صفحه (اختیاری)
        window.addEventListener('beforeunload', function(e) {
            if (remainingSeconds > 0 && !isSubmitting && !hasAutoSaved) {
                // تلاش برای ذخیره همگام (synchronous)
                const formData = new FormData(examForm);
                formData.append('auto_save', 'true');
                navigator.sendBeacon(examForm.action, formData);
            }
        });
    }
    

    
    function addBeforeUnloadWarning() {
        window.addEventListener('beforeunload', function(e) {
            if (remainingSeconds > 0 && !isSubmitting) {
                e.preventDefault();
                e.returnValue = 'آزمون شما نهایی نشده است. آیا مطمئن هستید؟';
                return e.returnValue;
            }
        });
    }
    
    function handleFormSubmission() {
        examForm.addEventListener('submit', function(e) {
            if (!isSubmitting) {
                isSubmitting = true;
                if (timerInterval) clearInterval(timerInterval);
                if (autoSaveInterval) clearInterval(autoSaveInterval);
            }
        });
    }
    
    // اضافه کردن استایل انیمیشن
    function addAnimationStyles() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
            .timer-warning {
                color: #eab308 !important;
                animation: pulse 1s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
        `;
        document.head.appendChild(style);
    }
    
    // ========== مقداردهی اولیه ==========
    addAnimationStyles();
    startTimer();
    startAutoSave();
    addBeforeUnloadWarning();
    handleFormSubmission();
    addManualSaveButton(); // دکمه ذخیره دستی (اختیاری)
});