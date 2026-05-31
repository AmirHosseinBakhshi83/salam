document.addEventListener('DOMContentLoaded', function() {
        // ========== منوی تب ==========
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabId = btn.getAttribute('data-tab');
                
                tabBtns.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                btn.classList.add('active');
                document.getElementById(`${tabId}Tab`).classList.add('active');
            });
        });

        // ========== اسنک بار ==========
        function showSnackbar(message, type = 'success') {
            const snackbar = document.getElementById('snackbar');
            snackbar.textContent = message;
            snackbar.style.background = type === 'success' ? '#10b981' : '#ef4444';
            snackbar.classList.add('show');
            setTimeout(() => {
                snackbar.classList.remove('show');
            }, 3000);
        }

        // ========== ذخیره اطلاعات ==========
        document.getElementById('saveInfoBtn').addEventListener('click', () => {
            const firstName = document.getElementById('firstName').value;
            const lastName = document.getElementById('lastName').value;
            const email = document.getElementById('email').value;
            
            document.getElementById('userFullName').textContent = `${firstName} ${lastName}`;
            showSnackbar('اطلاعات با موفقیت ذخیره شد');
        });

        // ========== تغییر رمز ==========
        document.getElementById('changePasswordBtn').addEventListener('click', () => {
            const currentPass = document.getElementById('currentPassword').value;
            const newPass = document.getElementById('newPassword').value;
            const confirmPass = document.getElementById('confirmPassword').value;
            
            if (!currentPass || !newPass || !confirmPass) {
                showSnackbar('لطفاً تمام فیلدها را پر کنید', 'error');
                return;
            }
            
            if (newPass !== confirmPass) {
                showSnackbar('رمز عبور جدید و تکرار آن مطابقت ندارند', 'error');
                return;
            }
            
            if (newPass.length < 6) {
                showSnackbar('رمز عبور باید حداقل ۶ کاراکتر باشد', 'error');
                return;
            }
            
            showSnackbar('رمز عبور با موفقیت تغییر کرد');
            document.getElementById('currentPassword').value = '';
            document.getElementById('newPassword').value = '';
            document.getElementById('confirmPassword').value = '';
        });

        // ========== مودال آواتار ==========
        const avatarModal = document.getElementById('avatarModal');
        const editAvatarBtn = document.getElementById('editAvatarBtn');
        const modalClose = document.querySelectorAll('.modal-close, .btn-cancel');

        editAvatarBtn.addEventListener('click', () => {
            avatarModal.classList.add('active');
        });

        modalClose.forEach(btn => {
            btn.addEventListener('click', () => {
                avatarModal.classList.remove('active');
            });
        });

        avatarModal.addEventListener('click', (e) => {
            if (e.target === avatarModal) {
                avatarModal.classList.remove('active');
            }
        });

        // ========== ESC کلید ==========
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && avatarModal.classList.contains('active')) {
                avatarModal.classList.remove('active');
            }
        });

        console.log('✅ صفحه پروفایل آماده است');
    });