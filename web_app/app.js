/**
 * Wall-e Web App — главный модуль
 */

const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

const API_BASE = '/api';
const initData = tg.initData || '';

// ====== Утилиты ======

function apiHeaders() {
    return { 'X-Telegram-Init-Data': initData };
}

async function apiFetch(path, options = {}) {
    try {
        const resp = await fetch(API_BASE + path, {
            ...options,
            headers: { ...apiHeaders(), ...(options.headers || {}) },
        });
        return await resp.json();
    } catch (e) {
        console.error('[API]', path, e);
        return null;
    }
}

function formatNumber(n) {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return String(n);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime(isoStr) {
    if (!isoStr) return '';
    const d = new Date(isoStr);
    const pad = n => String(n).padStart(2, '0');
    return `${pad(d.getDate())}.${pad(d.getMonth() + 1)} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

// ====== Навигация ======

const tabs = document.querySelectorAll('.tab');
const pages = document.querySelectorAll('.page');
const adminTab = document.querySelector('.tab[data-tab="admin"]');

if (adminTab) adminTab.style.display = 'none';

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const target = tab.dataset.tab;
        tabs.forEach(t => t.classList.remove('active'));
        pages.forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(target).classList.add('active');

        if (target === 'stats' && !statsLoaded) loadStats();
        if (target === 'profile' && !profileLoaded) loadProfile();
        if (target === 'admin' && !adminLoaded) loadAdmin();
    });
});

// ====== Статистика ======

let statsLoaded = false;

async function loadStats() {
    const [stats, top] = await Promise.all([
        apiFetch('/stats'),
        apiFetch('/top'),
    ]);

    if (stats && !stats.error) {
        document.getElementById('stat-users').textContent = formatNumber(stats.users);
        document.getElementById('stat-messages').textContent = formatNumber(stats.messages);
        document.getElementById('stat-chats').textContent = formatNumber(stats.chats);

        if (stats.is_admin && adminTab) {
            adminTab.style.display = '';
        }
    }

    const topEl = document.getElementById('top-users');
    if (top && top.top && top.top.length > 0) {
        const medals = ['🥇', '🥈', '🥉'];
        topEl.innerHTML = top.top.map((u, i) =>
            `<div class="top-item">
                <span class="top-rank">${medals[i] || (i + 1)}</span>
                <span class="top-name">${escapeHtml(u.name)}</span>
                <span class="top-count">${formatNumber(u.count)} сообщ.</span>
            </div>`
        ).join('');
    } else {
        topEl.innerHTML = '<div class="loading">Нет данных</div>';
    }

    statsLoaded = true;
}

// ====== Профиль ======

let profileLoaded = false;

async function loadProfile() {
    const user = tg.initDataUnsafe?.user;
    if (user) {
        const name = user.first_name + (user.last_name ? ' ' + user.last_name : '');
        document.getElementById('profile-name').textContent = name;
        document.getElementById('profile-username').textContent = user.username ? '@' + user.username : '';
        document.getElementById('profile-avatar').textContent = user.first_name.charAt(0).toUpperCase();
    }

    const profile = await apiFetch('/profile');
    if (profile && !profile.error) {
        document.getElementById('profile-messages').textContent = formatNumber(profile.messages_count);
        document.getElementById('profile-status').textContent = profile.is_admin ? '👑 Админ' : '👤 Пользователь';
    } else {
        document.getElementById('profile-messages').textContent = '?';
        document.getElementById('profile-status').textContent = '?';
    }

    profileLoaded = true;
}

// ====== Админ-панель ======

let adminLoaded = false;
let adminChats = [];

async function loadAdmin() {
    const data = await apiFetch('/chats');

    if (data && !data.error) {
        adminChats = data.chats;
        document.getElementById('admin-content').style.display = 'none';
        document.getElementById('admin-panel').style.display = 'block';

        // Заполняем оба селекта чатов
        const chatOptions = adminChats.map(c =>
            `<option value="${c.id}">${escapeHtml(c.title || String(c.id))} (${c.type})</option>`
        ).join('');

        const emptyOption = '<option disabled>Нет активных чатов</option>';
        document.getElementById('admin-chat').innerHTML = adminChats.length ? chatOptions : emptyOption;
        document.getElementById('admin-messages-chat').innerHTML = adminChats.length ? chatOptions : emptyOption;
    } else {
        document.getElementById('admin-content').style.display = 'none';
        document.getElementById('admin-denied').style.display = 'block';
    }

    adminLoaded = true;
}

// Отправка сообщения
document.getElementById('admin-send')?.addEventListener('click', async () => {
    const chatId = document.getElementById('admin-chat').value;
    const text = document.getElementById('admin-text').value.trim();

    if (!text) {
        showAdminStatus('Введите текст сообщения', 'error');
        return;
    }

    const result = await apiFetch('/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: chatId, text: text }),
    });

    if (result && result.ok) {
        showAdminStatus('Сообщение отправлено!', 'success');
        document.getElementById('admin-text').value = '';
    } else {
        showAdminStatus('Ошибка: ' + (result?.error || 'неизвестная'), 'error');
    }
});

function showAdminStatus(msg, type) {
    const el = document.getElementById('admin-status');
    el.textContent = msg;
    el.className = 'status ' + type;
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 4000);
}

// Просмотр сообщений
let messagesOffset = 0;
let currentMessagesChatId = null;

document.getElementById('admin-load-messages')?.addEventListener('click', () => {
    messagesOffset = 0;
    currentMessagesChatId = document.getElementById('admin-messages-chat').value;
    document.getElementById('messages-list').innerHTML = '';
    loadMessages();
});

document.getElementById('admin-load-more')?.addEventListener('click', () => {
    loadMessages();
});

function formatDuration(sec) {
    if (!sec) return '0:00';
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${String(s).padStart(2, '0')}`;
}

function formatFileSize(bytes) {
    if (!bytes) return '';
    if (bytes >= 1048576) return (bytes / 1048576).toFixed(1) + ' МБ';
    if (bytes >= 1024) return (bytes / 1024).toFixed(0) + ' КБ';
    return bytes + ' Б';
}

function mediaFileUrl(localPath) {
    if (!localPath) return null;
    return '/' + localPath.replace(/^media_files\//, 'media/');
}

function renderMessage(m) {
    const authQuery = `init_data=${encodeURIComponent(initData)}`;

    if (m.type === 'text') {
        return `<div class="msg-item">
            <div class="msg-header">
                <span class="msg-name">${escapeHtml(m.name)}</span>
                <span class="msg-time">${formatTime(m.created_at)}</span>
            </div>
            <div class="msg-text">${escapeHtml(m.text)}</div>
        </div>`;
    }

    if (m.type === 'voice') {
        const url = mediaFileUrl(m.local_path);
        const player = url
            ? `<audio controls preload="none" class="media-player"><source src="${url}?${authQuery}" type="audio/ogg"></audio>`
            : `<div class="media-no-file">Файл недоступен</div>`;
        return `<div class="msg-item msg-media">
            <div class="msg-header">
                <span class="msg-name">🎤 ${escapeHtml(m.name)}</span>
                <span class="msg-time">${formatTime(m.created_at)}</span>
            </div>
            <div class="media-info">Голосовое · ${formatDuration(m.duration)} · ${formatFileSize(m.file_size)}</div>
            ${player}
        </div>`;
    }

    if (m.type === 'video_note') {
        const url = mediaFileUrl(m.local_path);
        const player = url
            ? `<video controls preload="none" class="media-video-player" playsinline><source src="${url}?${authQuery}" type="video/mp4"></video>`
            : `<div class="media-no-file">Файл недоступен</div>`;
        return `<div class="msg-item msg-media">
            <div class="msg-header">
                <span class="msg-name">🎥 ${escapeHtml(m.name)}</span>
                <span class="msg-time">${formatTime(m.created_at)}</span>
            </div>
            <div class="media-info">Видеосообщение · ${formatDuration(m.duration)} · ${formatFileSize(m.file_size)}</div>
            ${player}
        </div>`;
    }

    return '';
}

async function loadMessages() {
    if (!currentMessagesChatId) return;

    const data = await apiFetch(`/messages?chat_id=${currentMessagesChatId}&offset=${messagesOffset}&limit=50`);
    if (!data || data.error) return;

    const listEl = document.getElementById('messages-list');
    const loadMoreBtn = document.getElementById('admin-load-more');
    listEl.style.display = 'block';

    if (messagesOffset === 0) {
        listEl.innerHTML = `<div class="msg-total">Всего: ${data.total}</div>`;
    }

    if (data.messages.length === 0 && messagesOffset === 0) {
        listEl.innerHTML = '<div class="loading">Нет сообщений</div>';
        loadMoreBtn.style.display = 'none';
        return;
    }

    const html = data.messages.map(renderMessage).join('');
    listEl.insertAdjacentHTML('beforeend', html);
    messagesOffset += data.messages.length;

    loadMoreBtn.style.display = messagesOffset < data.total ? 'block' : 'none';
}

// ====== Игра 2048 ======

const gameBoard = document.getElementById('game-board');
const gameScore = document.getElementById('game-score');
let game = null;

if (gameBoard && gameScore) {
    game = new Game2048(gameBoard, gameScore);
    document.getElementById('game-restart')?.addEventListener('click', () => game.init());
}

// ====== Инициализация ======

loadStats();
