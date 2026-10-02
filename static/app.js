/* Shared behaviour for every page: theme toggle, user dropdown, debounce.
   Load synchronously (before the header) so the theme class is set before first paint. */
(function () {
    'use strict';
    var root = document.documentElement;
    var KEY = 'theme';

    // Apply saved theme immediately (no flash)
    var light = false;
    try { light = localStorage.getItem(KEY) === 'light'; } catch (e) {}
    root.classList.toggle('light-mode', light);

    function syncIcon() {
        var use = document.getElementById('themeIcon');
        if (use) use.setAttribute('href', root.classList.contains('light-mode') ? '#i-sun' : '#i-moon');
    }

    window.toggleTheme = function () {
        var isLight = root.classList.toggle('light-mode');
        try { localStorage.setItem(KEY, isLight ? 'light' : 'dark'); } catch (e) {}
        syncIcon();
        document.dispatchEvent(new CustomEvent('themechange', { detail: { light: isLight } }));
    };

    window.debounce = function (fn, ms) {
        var t;
        return function () {
            var args = arguments, self = this;
            clearTimeout(t);
            t = setTimeout(function () { fn.apply(self, args); }, ms);
        };
    };

    document.addEventListener('DOMContentLoaded', syncIcon);

    // One delegated listener for the user dropdown
    document.addEventListener('click', function (e) {
        var box = document.getElementById('userDropdown');
        if (!box) return;
        if (e.target.closest('.profile-btn')) box.classList.toggle('active');
        else if (!box.contains(e.target)) box.classList.remove('active');
    });
})();
