// api.js — Fetch wrapper with auth header + blob download

const API_BASE = '/api/v1';

function getToken() {
    return localStorage.getItem('token');
}

function setToken(token) {
    localStorage.setItem('token', token);
}

function clearToken() {
    localStorage.removeItem('token');
}

function isLoggedIn() {
    return !!getToken();
}

async function apiGet(path) {
    const res = await fetch(API_BASE + path, {
        headers: { Authorization: `Bearer ${getToken()}` }
    });
    if (res.status === 401) {
        clearToken();
        window.location.href = '/app/index.html';
        throw new Error('Session expired');
    }
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(err.detail || `Error ${res.status}`);
    }
    return res.json();
}

async function apiPost(path, body) {
    const res = await fetch(API_BASE + path, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${getToken()}`
        },
        body: JSON.stringify(body)
    });
    if (res.status === 401) {
        clearToken();
        window.location.href = '/app/index.html';
        throw new Error('Session expired');
    }
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(err.detail || `Error ${res.status}`);
    }
    return res.json();
}

async function apiPut(path, body) {
    const res = await fetch(API_BASE + path, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${getToken()}`
        },
        body: JSON.stringify(body)
    });
    if (res.status === 401) {
        clearToken();
        window.location.href = '/app/index.html';
        throw new Error('Session expired');
    }
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(err.detail || `Error ${res.status}`);
    }
    return res.json();
}

async function uploadAndDownload(formData) {
    const res = await fetch(API_BASE + '/process', {
        method: 'POST',
        headers: { Authorization: `Bearer ${getToken()}` },
        body: formData
    });
    if (res.status === 401) {
        clearToken();
        window.location.href = '/app/index.html';
        throw new Error('Session expired');
    }
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Processing failed' }));
        throw new Error(err.detail || `Error ${res.status}`);
    }
    return res;
}

function downloadBlob(response, filename) {
    return response.blob().then(blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
}
