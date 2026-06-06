// app.js — Main application logic

let selectedTemplate = null;
let selectedFile = null;

document.addEventListener('DOMContentLoaded', () => {
    if (!isLoggedIn()) return;

    loadUserInfo();
    loadTemplates();
    loadHistory();
    setupUploadZone();
    setupSettings();
    setupLogout();
});

// ===== VIEW SWITCHING =====
function showView(view) {
    const mainView      = document.getElementById('mainView');
    const settingsView  = document.getElementById('settingsView');
    const templateList  = document.getElementById('templateList');
    const navMain       = document.getElementById('navMain');
    const navSettings   = document.getElementById('navSettings');

    if (view === 'settings') {
        mainView.classList.add('hidden');
        settingsView.classList.remove('hidden');
        templateList.classList.add('hidden');
        navMain.classList.remove('active');
        navMain.setAttribute('aria-pressed', 'false');
        navSettings.classList.add('active');
        navSettings.setAttribute('aria-pressed', 'true');
    } else {
        settingsView.classList.add('hidden');
        mainView.classList.remove('hidden');
        templateList.classList.remove('hidden');
        navMain.classList.add('active');
        navMain.setAttribute('aria-pressed', 'true');
        navSettings.classList.remove('active');
        navSettings.setAttribute('aria-pressed', 'false');
    }
}

// ===== USER INFO =====
async function loadUserInfo() {
    try {
        const user = await apiGet('/auth/me');
        document.getElementById('displayName').textContent = user.username;
        document.getElementById('displayRole').textContent = user.role === 'admin' ? '(Admin)' : '';

        // Apply saved font size
        if (user.settings_json) {
            try {
                const settings = JSON.parse(user.settings_json);
                const size = settings.font_size || 'normal';
                applyFontSize(size);
                // Sync radio button to saved setting
                const radio = document.querySelector(`input[name="fontSize"][value="${size}"]`);
                if (radio) radio.checked = true;
            } catch (e) { /* ignore */ }
        }
    } catch (err) {
        console.error('Failed to load user info:', err);
    }
}

// ===== TEMPLATES =====
async function loadTemplates() {
    try {
        const templates = await apiGet('/templates');
        renderTemplates(templates);
    } catch (err) {
        console.error('Failed to load templates:', err);
    }
}

function renderTemplates(templates) {
    const container = document.getElementById('templateList');
    if (!templates.length) {
        container.innerHTML = '<div style="color:rgba(255,255,255,0.4);padding:1rem;font-size:0.85rem;">No templates available</div>';
        return;
    }

    // Group by category
    const grouped = {};
    templates.forEach(t => {
        const cat = t.category || 'other';
        if (!grouped[cat]) grouped[cat] = [];
        grouped[cat].push(t);
    });

    const categoryLabels = {
        bank_statement: 'Bank Statements',
        bank_clearance: 'Bank Clearance',
        invoice: 'Invoices',
        other: 'Other'
    };

    let html = '';
    for (const [cat, items] of Object.entries(grouped)) {
        html += `<div class="template-category">${categoryLabels[cat] || cat}</div>`;
        items.forEach(t => {
            html += `
                <div class="template-card" data-key="${t.key}" onclick="selectTemplate('${t.key}')">
                    <span class="t-icon">📄</span>
                    <div class="t-info">
                        <div class="t-name">${escapeHtml(t.name)}</div>
                        <div class="t-desc">${escapeHtml(t.description || '')}</div>
                    </div>
                </div>
            `;
        });
    }
    container.innerHTML = html;
}

function selectTemplate(key) {
    selectedTemplate = key;

    // Ensure we're on the main view when a template is selected
    showView('main');

    // UI feedback
    document.querySelectorAll('.template-card').forEach(c => c.classList.remove('active'));
    const card = document.querySelector(`.template-card[data-key="${key}"]`);
    if (card) card.classList.add('active');

    // Enable upload zone
    const zone = document.getElementById('uploadZone');
    zone.classList.add('enabled');
    document.getElementById('uploadIcon').textContent = '📤';
    document.getElementById('uploadText').textContent = 'Drop your file here';
    document.getElementById('uploadHint').textContent = 'or click SELECT FILE below';
}

// ===== UPLOAD ZONE =====
function setupUploadZone() {
    const zone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const selectBtn = document.getElementById('selectFileBtn');

    selectBtn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            onFileSelected(fileInput.files[0]);
        }
    });

    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        if (selectedTemplate) zone.classList.add('dragover');
    });

    zone.addEventListener('dragleave', () => {
        zone.classList.remove('dragover');
    });

    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        if (!selectedTemplate) return;
        const file = e.dataTransfer.files[0];
        if (file) onFileSelected(file);
    });
}

function onFileSelected(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    const allowed = ['pdf', 'csv', 'xlsx'];

    if (!allowed.includes(ext)) {
        showError(`File type ".${ext}" is not supported. Please upload a PDF, CSV, or Excel (.xlsx) file.`);
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        showError('File is too large. Maximum size is 10 MB.');
        return;
    }

    selectedFile = file;
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSelected').classList.add('visible');
    document.getElementById('uploadBtn').classList.remove('hidden');
    document.getElementById('uploadIcon').textContent = '✅';
    document.getElementById('uploadText').textContent = 'File ready';
    document.getElementById('uploadHint').textContent = '';
}

// ===== PROCESS =====
async function handleUpload() {
    if (!selectedFile || !selectedTemplate) return;

    const spinner = document.getElementById('spinner');
    const errorCard = document.getElementById('errorCard');

    spinner.classList.add('visible');
    errorCard.classList.remove('visible');

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('template_name', selectedTemplate);

    try {
        const response = await uploadAndDownload(formData);
        const filename = selectedFile.name.replace(/\.[^.]+$/, '_extracted.xlsx');
        await downloadBlob(response, filename);

        spinner.classList.remove('visible');
        resetUpload();
        loadHistory();
    } catch (err) {
        spinner.classList.remove('visible');
        showError(err.message);
    }
}

function resetUpload() {
    selectedFile = null;
    document.getElementById('fileInput').value = '';
    document.getElementById('fileSelected').classList.remove('visible');
    document.getElementById('uploadBtn').classList.add('hidden');
    document.getElementById('uploadIcon').textContent = '📤';
    document.getElementById('uploadText').textContent = 'Drop your file here';
    document.getElementById('uploadHint').textContent = 'or click SELECT FILE below';
}

function showError(message) {
    const card = document.getElementById('errorCard');
    document.getElementById('errorMessage').textContent = message;
    card.classList.add('visible');
}

function dismissError() {
    document.getElementById('errorCard').classList.remove('visible');
}

// ===== HISTORY =====
async function loadHistory() {
    try {
        const data = await apiGet('/jobs?page=1&page_size=10');
        renderHistory(data.jobs);
    } catch (err) {
        console.error('Failed to load history:', err);
    }
}

function renderHistory(jobs) {
    const tbody = document.getElementById('historyBody');
    const empty = document.getElementById('emptyHistory');

    if (!jobs.length) {
        tbody.innerHTML = '';
        empty.classList.remove('hidden');
        return;
    }

    empty.classList.add('hidden');
    tbody.innerHTML = jobs.map(j => `
        <tr>
            <td>${escapeHtml(j.original_filename)}</td>
            <td>${escapeHtml(j.template_name)}</td>
            <td>${formatDate(j.created_at)}</td>
            <td>${j.rows_extracted}</td>
            <td>
                <button class="btn btn-primary btn-small" onclick="downloadJob(${j.id}, '${escapeHtml(j.original_filename)}')">
                    ⬇ Download
                </button>
            </td>
        </tr>
    `).join('');
}

async function downloadJob(jobId, filename) {
    try {
        const downloadName = filename.replace(/\.[^.]+$/, '_extracted.xlsx');
        // Direct download via anchor
        const a = document.createElement('a');
        a.href = `${API_BASE}/download/${jobId}?token=${getToken()}`;
        a.download = downloadName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    } catch (err) {
        showError('Failed to download file');
    }
}

// ===== SETTINGS =====
function setupSettings() {
    document.getElementById('changePasswordForm').addEventListener('submit', handleChangePassword);
}

async function handleChangePassword(e) {
    e.preventDefault();
    const msgEl = document.getElementById('passwordMsg');
    const oldPw = document.getElementById('oldPassword').value;
    const newPw = document.getElementById('newPassword').value;

    msgEl.classList.remove('visible', 'error-msg', 'success-msg');

    if (newPw.length < 6) {
        msgEl.classList.add('error-msg', 'visible');
        msgEl.textContent = 'New password must be at least 6 characters.';
        return;
    }

    try {
        await apiPut('/auth/change-password', { old_password: oldPw, new_password: newPw });
        msgEl.classList.add('success-msg', 'visible');
        msgEl.textContent = '✓ Password changed successfully';
        document.getElementById('oldPassword').value = '';
        document.getElementById('newPassword').value = '';
    } catch (err) {
        msgEl.classList.add('error-msg', 'visible');
        msgEl.textContent = err.message;
    }
}

function applyFontSize(size) {
    const sizes = { normal: '18px', large: '22px', xlarge: '26px' };
    document.documentElement.style.fontSize = sizes[size] || '18px';
    // Persist
    apiPut('/auth/settings', { font_size: size }).catch(() => {});
}

function setupLogout() {
    document.getElementById('logoutBtn').addEventListener('click', logout);
}

// ===== HELPERS =====
function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}
