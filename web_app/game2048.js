/**
 * Игра 2048 для Telegram Web App
 */
class Game2048 {
    constructor(boardEl, scoreEl) {
        this.boardEl = boardEl;
        this.scoreEl = scoreEl;
        this.size = 4;
        this.score = 0;
        this.grid = [];
        this.init();
    }

    init() {
        this.grid = Array.from({ length: this.size }, () => Array(this.size).fill(0));
        this.score = 0;
        this.addRandom();
        this.addRandom();
        this.render();
        this.setupInput();
    }

    addRandom() {
        const empty = [];
        for (let r = 0; r < this.size; r++) {
            for (let c = 0; c < this.size; c++) {
                if (this.grid[r][c] === 0) empty.push([r, c]);
            }
        }
        if (empty.length === 0) return;
        const [r, c] = empty[Math.floor(Math.random() * empty.length)];
        this.grid[r][c] = Math.random() < 0.9 ? 2 : 4;
    }

    render() {
        this.boardEl.innerHTML = '';
        for (let r = 0; r < this.size; r++) {
            for (let c = 0; c < this.size; c++) {
                const val = this.grid[r][c];
                const cell = document.createElement('div');
                cell.className = `game-cell cell-${val}`;
                cell.textContent = val || '';
                this.boardEl.appendChild(cell);
            }
        }
        this.scoreEl.textContent = this.score;
    }

    slide(row) {
        let arr = row.filter(v => v !== 0);
        const result = [];
        for (let i = 0; i < arr.length; i++) {
            if (i + 1 < arr.length && arr[i] === arr[i + 1]) {
                result.push(arr[i] * 2);
                this.score += arr[i] * 2;
                i++;
            } else {
                result.push(arr[i]);
            }
        }
        while (result.length < this.size) result.push(0);
        return result;
    }

    move(direction) {
        const prev = JSON.stringify(this.grid);
        if (direction === 'left') {
            for (let r = 0; r < this.size; r++) {
                this.grid[r] = this.slide(this.grid[r]);
            }
        } else if (direction === 'right') {
            for (let r = 0; r < this.size; r++) {
                this.grid[r] = this.slide(this.grid[r].reverse()).reverse();
            }
        } else if (direction === 'up') {
            for (let c = 0; c < this.size; c++) {
                const col = this.grid.map(row => row[c]);
                const slid = this.slide(col);
                for (let r = 0; r < this.size; r++) this.grid[r][c] = slid[r];
            }
        } else if (direction === 'down') {
            for (let c = 0; c < this.size; c++) {
                const col = this.grid.map(row => row[c]).reverse();
                const slid = this.slide(col).reverse();
                for (let r = 0; r < this.size; r++) this.grid[r][c] = slid[r];
            }
        }
        if (JSON.stringify(this.grid) !== prev) {
            this.addRandom();
            this.render();
            if (this.isGameOver()) {
                setTimeout(() => {
                    if (window.Telegram?.WebApp) {
                        window.Telegram.WebApp.showAlert(`Игра окончена! Счёт: ${this.score}`);
                    }
                }, 200);
            }
        }
    }

    isGameOver() {
        for (let r = 0; r < this.size; r++) {
            for (let c = 0; c < this.size; c++) {
                if (this.grid[r][c] === 0) return false;
                if (c + 1 < this.size && this.grid[r][c] === this.grid[r][c + 1]) return false;
                if (r + 1 < this.size && this.grid[r][c] === this.grid[r + 1][c]) return false;
            }
        }
        return true;
    }

    setupInput() {
        // Клавиатура
        document.addEventListener('keydown', (e) => {
            const map = { ArrowLeft: 'left', ArrowRight: 'right', ArrowUp: 'up', ArrowDown: 'down' };
            if (map[e.key]) {
                e.preventDefault();
                this.move(map[e.key]);
            }
        });

        // Свайпы
        let startX, startY;
        this.boardEl.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, { passive: true });

        this.boardEl.addEventListener('touchend', (e) => {
            if (!startX || !startY) return;
            const dx = e.changedTouches[0].clientX - startX;
            const dy = e.changedTouches[0].clientY - startY;
            const minSwipe = 30;

            if (Math.abs(dx) > Math.abs(dy)) {
                if (Math.abs(dx) > minSwipe) this.move(dx > 0 ? 'right' : 'left');
            } else {
                if (Math.abs(dy) > minSwipe) this.move(dy > 0 ? 'down' : 'up');
            }
            startX = startY = null;
        }, { passive: true });
    }
}
