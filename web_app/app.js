/**
 * Wall-e Web App — главный модуль
 */

// Инициализация Telegram Web App
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

// ====== Навигация ======

const tabs = document.querySelectorAll('.tab');
const pages = document.querySelectorAll('.page');
const adminTab = document.querySelector('.tab[data-tab="admin"]');

// Скрываем админ-таб по умолчанию
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

    if (stats) {
        // Показываем название чата если есть
        const title = document.getElementById('stats-title');
        if (stats.chat_title) {
            title.textContent = '📊 ' + stats.chat_title;
        }

        document.getElementById('stat-users').textContent = formatNumber(stats.users);
        document.getElementById('stat-messages').textContent = formatNumber(stats.messages);

        // Скрываем карточку "Чатов" если мы внутри чата
        const chatsCard = document.getElementById('stat-chats-card');
        if (stats.chats <= 1 && stats.chat_title) {
            chatsCard.style.display = 'none';
        } else {
            document.getElementById('stat-chats').textContent = formatNumber(stats.chats);
        }

        // Показываем админ-таб если пользователь — админ
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

async function loadAdmin() {
    const data = await apiFetch('/chats');

    if (data && !data.error) {
        document.getElementById('admin-content').style.display = 'none';
        document.getElementById('admin-panel').style.display = 'block';

        const select = document.getElementById('admin-chat');
        select.innerHTML = data.chats.map(c =>
            `<option value="${c.id}">${escapeHtml(c.title || String(c.id))} (${c.type})</option>`
        ).join('');

        if (data.chats.length === 0) {
            select.innerHTML = '<option disabled>Нет активных чатов</option>';
        }
    } else {
        document.getElementById('admin-content').style.display = 'none';
        document.getElementById('admin-denied').style.display = 'block';
    }

    adminLoaded = true;
}

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
