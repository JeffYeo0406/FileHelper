// auth.js — Login/logout helpers

document.addEventListener('DOMContentLoaded', () => {
    // If we're on the login page
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        // Redirect if already logged in
        if (isLoggedIn()) {
            window.location.href = '/app.html';
            return;
        }
        loginForm.addEventListener('submit', handleLogin);
    }

    // If we're on the main app, check auth
    if (!loginForm && window.location.pathname.includes('app.html')) {
        if (!isLoggedIn()) {
            window.location.href = '/';
        }
    }
});

async function handleLogin(e) {
    e.preventDefault();
    const errorEl = document.getElementById('loginError');
    const btn = document.getElementById('loginBtn');

    errorEl.classList.remove('visible');
    btn.disabled = true;
    btn.textContent = 'Signing in...';

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    try {
        const data = await apiPost('/auth/login', { username, password });
        setToken(data.access_token);
        window.location.href = '/app.html';
    } catch (err) {
        errorEl.textContent = err.message;
        errorEl.classList.add('visible');
        btn.disabled = false;
        btn.textContent = 'Sign In';
    }
}

function logout() {
    clearToken();
    window.location.href = '/';
}
