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
