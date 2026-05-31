document.addEventListener('DOMContentLoaded', function () {

    const sidebarItems = document.querySelectorAll('.sidebar-item');
    sidebarItems.forEach(function (item) {
        item.addEventListener('click', function () {
            sidebarItems.forEach(function (i) {
                i.classList.remove('active');
            });
            item.classList.add('active');
        });
    });

    const goToUserInfoBtn = document.getElementById('goToUserInfoBtn');
    if (goToUserInfoBtn) {
        goToUserInfoBtn.addEventListener('click', function () {
        });
    }

});
// دریافت المان‌ها
        const messageBox = document.getElementById('notificationBox');
        const messageText = document.getElementById('messageText');
        const closeBtn = document.getElementById('closeMessageBtn');

        // تابع نمایش پیام عمومی
        function showMessage(message, type = 'error') {
            // تنظیم متن پیام
            messageText.textContent = message;
            
            // حذف کلاس‌های قبلی و اضافه کردن کلاس جدید
            messageBox.classList.remove('error', 'success', 'warning', 'show');
            
            if (type === 'error') {
                messageBox.classList.add('error');
                // تغییر آیکون برای خطا
                const iconSvg = messageBox.querySelector('.message-icon svg');
                iconSvg.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />';
            } else if (type === 'success') {
                messageBox.classList.add('success');
                const iconSvg = messageBox.querySelector('.message-icon svg');
                iconSvg.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />';
            } else if (type === 'warning') {
                messageBox.classList.add('warning');
                const iconSvg = messageBox.querySelector('.message-icon svg');
                iconSvg.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />';
            }
            
            // نمایش باکس
            setTimeout(() => {
                messageBox.classList.add('show');
            }, 10);
            
            // بعد از 5 ثانیه خودکار مخفی شود
            setTimeout(() => {
                messageBox.classList.remove('show');
            }, 5000);
        }

        // تابع نمایش پیام خطا (قرمز)
        function showErrorMessage(message) {
            showMessage(message, 'error');
        }

        // تابع نمایش پیام موفقیت (سبز)
        function showSuccessMessage(message) {
            showMessage(message, 'success');
        }

        // تابع نمایش پیام هشدار (نارنجی)
        function showWarningMessage(message) {
            showMessage(message, 'warning');
        }

        // دکمه بستن دستی
        closeBtn.addEventListener('click', () => {
            messageBox.classList.remove('show');
        });

