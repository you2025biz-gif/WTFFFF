// Telegram WebApp API Integration
class TelegramMiniApp {
    constructor() {
        this.tg = window.Telegram.WebApp;
        this.user = null;
        this.balance = 0;
        this.frozen = 0;
        this.deals = [];
        this.history = [];
        
        this.init();
    }

    init() {
        // Initialize Telegram WebApp
        this.tg.ready();
        this.tg.expand();
        
        // Get user data from Telegram
        this.user = this.tg.initDataUnsafe?.user || {
            id: 123456789,
            first_name: 'Пользователь',
            username: 'user'
        };

        // Set up theme
        this.setupTheme();
        
        // Initialize UI
        this.initializeUI();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load user data
        this.loadUserData();
        
        // Show welcome message
        this.showToast('Добро пожаловать в Гарант-Бот!', 'success');
    }

    setupTheme() {
        // Apply Telegram theme colors
        const theme = this.tg.themeParams;
        if (theme) {
            document.documentElement.style.setProperty('--tg-theme-bg-color', theme.bg_color);
            document.documentElement.style.setProperty('--tg-theme-text-color', theme.text_color);
            document.documentElement.style.setProperty('--tg-theme-hint-color', theme.hint_color);
            document.documentElement.style.setProperty('--tg-theme-link-color', theme.link_color);
            document.documentElement.style.setProperty('--tg-theme-button-color', theme.button_color);
            document.documentElement.style.setProperty('--tg-theme-button-text-color', theme.button_text_color);
        }
    }

    initializeUI() {
        // Set user info
        document.getElementById('userName').textContent = this.user.first_name || 'Пользователь';
        document.getElementById('userId').textContent = `ID: ${this.user.id}`;
        
        // Set wallet address from config
        document.getElementById('walletAddress').textContent = window.CONFIG?.TON_WALLET_ADDRESS || 'UQCow0sO7p9izwbvm8XMYlEfEirNEW-yXPqyS_rcTmS-GUtg';
    }

    setupEventListeners() {
        // Navigation tabs
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.currentTarget.dataset.tab;
                this.switchTab(tabName);
            });
        });

        // Action buttons
        document.getElementById('topupBtn').addEventListener('click', () => this.showTopupModal());
        document.getElementById('withdrawBtn').addEventListener('click', () => this.showWithdrawModal());
        document.getElementById('createDealBtn').addEventListener('click', () => this.showCreateDealModal());
        document.getElementById('createDealBtn2').addEventListener('click', () => this.showCreateDealModal());
        document.getElementById('createFirstDealBtn').addEventListener('click', () => this.showCreateDealModal());
        document.getElementById('myDealsBtn').addEventListener('click', () => this.switchTab('deals'));

        // Modal controls
        this.setupModalControls();

        // Form submissions
        this.setupFormSubmissions();

        // Copy wallet address
        document.getElementById('copyWalletBtn').addEventListener('click', () => {
            const walletAddress = window.CONFIG?.TON_WALLET_ADDRESS || 'UQCow0sO7p9izwbvm8XMYlEfEirNEW-yXPqyS_rcTmS-GUtg';
            this.copyToClipboard(walletAddress);
        });

        // Deal type selection
        document.querySelectorAll('.deal-type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.deal-type-btn').forEach(b => b.classList.remove('active'));
                e.currentTarget.classList.add('active');
            });
        });

        // History filters
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.currentTarget.classList.add('active');
                this.filterHistory(e.currentTarget.dataset.filter);
            });
        });
    }

    setupModalControls() {
        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.currentTarget.closest('.modal');
                this.hideModal(modal.id);
            });
        });

        // Close modal on backdrop click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal.id);
                }
            });
        });

        // Cancel buttons
        document.getElementById('cancelTopupBtn').addEventListener('click', () => this.hideModal('topupModal'));
        document.getElementById('cancelWithdrawBtn').addEventListener('click', () => this.hideModal('withdrawModal'));
        document.getElementById('cancelDealBtn').addEventListener('click', () => this.hideModal('createDealModal'));
    }

    setupFormSubmissions() {
        // Topup form
        document.getElementById('submitTopupBtn').addEventListener('click', () => this.submitTopup());
        
        // Withdraw form
        document.getElementById('submitWithdrawBtn').addEventListener('click', () => this.submitWithdraw());
        
        // Create deal form
        document.getElementById('submitDealBtn').addEventListener('click', () => this.submitCreateDeal());
    }

    switchTab(tabName) {
        // Update navigation
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        // Load tab-specific data
        if (tabName === 'deals') {
            this.loadDeals();
        } else if (tabName === 'history') {
            this.loadHistory();
        }
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.remove('active');
        document.body.style.overflow = '';
        
        // Clear form data
        if (modalId === 'topupModal') {
            document.getElementById('topupAmount').value = '';
            document.getElementById('txHash').value = '';
        } else if (modalId === 'withdrawModal') {
            document.getElementById('withdrawAmount').value = '';
            document.getElementById('withdrawAddress').value = '';
        } else if (modalId === 'createDealModal') {
            document.getElementById('dealName').value = '';
            document.getElementById('dealAmount').value = '';
            document.querySelectorAll('.deal-type-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelector('.deal-type-btn[data-type="sell"]').classList.add('active');
        }
    }

    showTopupModal() {
        this.showModal('topupModal');
    }

    showWithdrawModal() {
        this.showModal('withdrawModal');
    }

    showCreateDealModal() {
        this.showModal('createDealModal');
    }

    async loadUserData() {
        try {
            this.showLoading(true);
            
            // Simulate API call - replace with actual API endpoint
            const response = await this.apiCall('/api/user', {
                user_id: this.user.id
            });
            
            if (response.success) {
                this.balance = response.data.balance || 0;
                this.frozen = response.data.frozen || 0;
                this.updateBalanceDisplay();
            }
        } catch (error) {
            console.error('Error loading user data:', error);
            this.showToast('Ошибка загрузки данных пользователя', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async loadDeals() {
        try {
            this.showLoading(true);
            
            const response = await this.apiCall('/api/deals', {
                user_id: this.user.id
            });
            
            if (response.success) {
                this.deals = response.data.deals || [];
                this.renderDeals();
            }
        } catch (error) {
            console.error('Error loading deals:', error);
            this.showToast('Ошибка загрузки сделок', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async loadHistory() {
        try {
            this.showLoading(true);
            
            const response = await this.apiCall('/api/history', {
                user_id: this.user.id
            });
            
            if (response.success) {
                this.history = response.data.history || [];
                this.renderHistory();
            }
        } catch (error) {
            console.error('Error loading history:', error);
            this.showToast('Ошибка загрузки истории', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    updateBalanceDisplay() {
        const available = this.balance - this.frozen;
        
        document.getElementById('userBalance').textContent = `${this.balance.toFixed(2)} TON`;
        document.getElementById('availableBalance').textContent = `${available.toFixed(2)} TON`;
        document.getElementById('frozenBalance').textContent = `${this.frozen.toFixed(2)} TON`;
    }

    renderDeals() {
        const dealsList = document.getElementById('dealsList');
        
        if (this.deals.length === 0) {
            dealsList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-handshake"></i>
                    <p>Нет активных сделок</p>
                    <button class="btn-primary" id="createFirstDealBtn">Создать первую сделку</button>
                </div>
            `;
            
            // Re-attach event listener
            document.getElementById('createFirstDealBtn').addEventListener('click', () => this.showCreateDealModal());
            return;
        }

        dealsList.innerHTML = this.deals.map(deal => `
            <div class="deal-card">
                <div class="deal-header">
                    <div class="deal-title">${deal.name}</div>
                    <div class="deal-amount">${deal.sum} TON</div>
                </div>
                <div class="deal-info">
                    <div class="deal-type">
                        <i class="fas ${deal.type === 'sell' ? 'fa-gift' : 'fa-shopping-cart'}"></i>
                        ${deal.type === 'sell' ? 'Продажа подарка' : 'Покупка подарка'}
                    </div>
                    <div class="deal-status ${deal.status}">
                        <i class="fas ${this.getStatusIcon(deal.status)}"></i>
                        ${this.getStatusText(deal.status)}
                    </div>
                </div>
                <div class="deal-actions">
                    ${this.getDealActions(deal)}
                </div>
            </div>
        `).join('');

        // Attach event listeners to deal actions
        this.attachDealActionListeners();
    }

    renderHistory() {
        const historyList = document.getElementById('historyList');
        
        if (this.history.length === 0) {
            historyList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-history"></i>
                    <p>История операций пуста</p>
                </div>
            `;
            return;
        }

        historyList.innerHTML = this.history.map(item => `
            <div class="history-item">
                <div class="history-icon ${item.type}">
                    <i class="fas ${this.getHistoryIcon(item.type)}"></i>
                </div>
                <div class="history-details">
                    <div class="history-title">${item.title}</div>
                    <div class="history-description">${item.description}</div>
                </div>
                <div class="history-amount ${item.amount > 0 ? 'positive' : 'negative'}">
                    ${item.amount > 0 ? '+' : ''}${item.amount.toFixed(2)} TON
                </div>
            </div>
        `).join('');
    }

    getStatusIcon(status) {
        const icons = {
            waiting: 'fa-clock',
            joined: 'fa-user-check',
            frozen: 'fa-lock',
            completed: 'fa-check-circle',
            cancelled: 'fa-times-circle'
        };
        return icons[status] || 'fa-question';
    }

    getStatusText(status) {
        const texts = {
            waiting: 'Ожидает участника',
            joined: 'Участник найден',
            frozen: 'Средства заморожены',
            completed: 'Завершена',
            cancelled: 'Отменена'
        };
        return texts[status] || 'Неизвестно';
    }

    getDealActions(deal) {
        const actions = [];
        
        if (deal.status === 'waiting' && deal.creator_id === this.user.id) {
            actions.push('<button class="deal-btn secondary" data-action="cancel" data-deal-id="' + deal.id + '">Отменить</button>');
        }
        
        if (deal.status === 'waiting' && deal.creator_id !== this.user.id) {
            actions.push('<button class="deal-btn primary" data-action="join" data-deal-id="' + deal.id + '">Присоединиться</button>');
        }
        
        if (deal.status === 'joined' || deal.status === 'frozen') {
            if (deal.type === 'sell' && deal.creator_id === this.user.id) {
                actions.push('<button class="deal-btn primary" data-action="send-gift" data-deal-id="' + deal.id + '">Передать подарок</button>');
            } else if (deal.type === 'buy' && deal.buyer_id === this.user.id) {
                actions.push('<button class="deal-btn primary" data-action="send-gift" data-deal-id="' + deal.id + '">Передать подарок</button>');
            }
            
            if (deal.type === 'sell' && deal.buyer_id === this.user.id) {
                actions.push('<button class="deal-btn secondary" data-action="confirm" data-deal-id="' + deal.id + '">Подтвердить получение</button>');
            } else if (deal.type === 'buy' && deal.creator_id === this.user.id) {
                actions.push('<button class="deal-btn secondary" data-action="confirm" data-deal-id="' + deal.id + '">Подтвердить получение</button>');
            }
        }
        
        return actions.join('');
    }

    attachDealActionListeners() {
        document.querySelectorAll('[data-action]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                const dealId = e.currentTarget.dataset.dealId;
                this.handleDealAction(action, dealId);
            });
        });
    }

    async handleDealAction(action, dealId) {
        try {
            this.showLoading(true);
            
            const response = await this.apiCall('/api/deal-action', {
                user_id: this.user.id,
                deal_id: dealId,
                action: action
            });
            
            if (response.success) {
                this.showToast(response.message || 'Действие выполнено успешно', 'success');
                this.loadDeals(); // Refresh deals list
                this.loadUserData(); // Refresh balance
            } else {
                this.showToast(response.message || 'Ошибка выполнения действия', 'error');
            }
        } catch (error) {
            console.error('Error handling deal action:', error);
            this.showToast('Ошибка выполнения действия', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    getHistoryIcon(type) {
        const icons = {
            topup: 'fa-plus',
            withdraw: 'fa-minus',
            deal: 'fa-handshake',
            commission: 'fa-percentage'
        };
        return icons[type] || 'fa-question';
    }

    filterHistory(filter) {
        const items = document.querySelectorAll('.history-item');
        
        items.forEach(item => {
            const itemType = item.querySelector('.history-icon').classList[1];
            
            if (filter === 'all' || itemType === filter) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }

    async submitTopup() {
        const amount = parseFloat(document.getElementById('topupAmount').value);
        const txHash = document.getElementById('txHash').value.trim();
        
        if (!amount || amount <= 0) {
            this.showToast('Введите корректную сумму', 'error');
            return;
        }
        
        if (amount > 1000) {
            this.showToast('Максимальная сумма пополнения: 1000 TON', 'error');
            return;
        }
        
        if (!txHash) {
            this.showToast('Введите TX hash транзакции', 'error');
            return;
        }
        
        try {
            this.showLoading(true);
            
            const response = await this.apiCall('/api/topup', {
                user_id: this.user.id,
                amount: amount,
                tx_hash: txHash
            });
            
            if (response.success) {
                this.showToast('Заявка на пополнение отправлена', 'success');
                this.hideModal('topupModal');
                this.loadUserData();
            } else {
                this.showToast(response.message || 'Ошибка создания заявки', 'error');
            }
        } catch (error) {
            console.error('Error submitting topup:', error);
            this.showToast('Ошибка создания заявки', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async submitWithdraw() {
        const amount = parseFloat(document.getElementById('withdrawAmount').value);
        const address = document.getElementById('withdrawAddress').value.trim();
        
        if (!amount || amount <= 0) {
            this.showToast('Введите корректную сумму', 'error');
            return;
        }
        
        if (amount > (this.balance - this.frozen)) {
            this.showToast('Недостаточно средств', 'error');
            return;
        }
        
        if (!address) {
            this.showToast('Введите адрес кошелька', 'error');
            return;
        }
        
        try {
            this.showLoading(true);
            
            const response = await this.apiCall('/api/withdraw', {
                user_id: this.user.id,
                amount: amount,
                address: address
            });
            
            if (response.success) {
                this.showToast('Заявка на вывод создана', 'success');
                this.hideModal('withdrawModal');
                this.loadUserData();
            } else {
                this.showToast(response.message || 'Ошибка создания заявки', 'error');
            }
        } catch (error) {
            console.error('Error submitting withdraw:', error);
            this.showToast('Ошибка создания заявки', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async submitCreateDeal() {
        const type = document.querySelector('.deal-type-btn.active').dataset.type;
        const name = document.getElementById('dealName').value.trim();
        const amount = parseFloat(document.getElementById('dealAmount').value);
        
        if (!name) {
            this.showToast('Введите название подарка', 'error');
            return;
        }
        
        if (!amount || amount <= 0) {
            this.showToast('Введите корректную сумму', 'error');
            return;
        }
        
        if (type === 'sell' && amount > (this.balance - this.frozen)) {
            this.showToast('Недостаточно средств для создания сделки', 'error');
            return;
        }
        
        try {
            this.showLoading(true);
            
            const response = await this.apiCall('/api/create-deal', {
                user_id: this.user.id,
                type: type,
                name: name,
                amount: amount
            });
            
            if (response.success) {
                this.showToast('Сделка создана успешно', 'success');
                this.hideModal('createDealModal');
                this.loadDeals();
                this.loadUserData();
            } else {
                this.showToast(response.message || 'Ошибка создания сделки', 'error');
            }
        } catch (error) {
            console.error('Error creating deal:', error);
            this.showToast('Ошибка создания сделки', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async apiCall(endpoint, data) {
        // Используем URL из конфигурации
        const baseUrl = window.CONFIG?.API_BASE_URL || 'https://your-api-domain.com';
        
        try {
            const response = await fetch(baseUrl + endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            
            // Return mock data for development
            return this.getMockResponse(endpoint, data);
        }
    }

    getMockResponse(endpoint, data) {
        // Mock responses for development
        switch (endpoint) {
            case '/api/user':
                return {
                    success: true,
                    data: {
                        balance: 150.75,
                        frozen: 25.00
                    }
                };
                
            case '/api/deals':
                return {
                    success: true,
                    data: {
                        deals: [
                            {
                                id: 1,
                                name: 'Steam Gift Card $50',
                                type: 'sell',
                                sum: 25.00,
                                status: 'waiting',
                                creator_id: data.user_id,
                                buyer_id: null
                            },
                            {
                                id: 2,
                                name: 'PlayStation Store Gift Card',
                                type: 'buy',
                                sum: 15.00,
                                status: 'joined',
                                creator_id: 123456,
                                buyer_id: data.user_id
                            }
                        ]
                    }
                };
                
            case '/api/history':
                return {
                    success: true,
                    data: {
                        history: [
                            {
                                type: 'topup',
                                title: 'Пополнение баланса',
                                description: 'TX: abc123...',
                                amount: 100.00,
                                date: new Date().toISOString()
                            },
                            {
                                type: 'deal',
                                title: 'Создание сделки',
                                description: 'Steam Gift Card $50',
                                amount: -25.00,
                                date: new Date().toISOString()
                            },
                            {
                                type: 'commission',
                                title: 'Комиссия сервиса',
                                description: 'За сделку #1',
                                amount: -1.25,
                                date: new Date().toISOString()
                            }
                        ]
                    }
                };
                
            case '/api/topup':
                return {
                    success: true,
                    message: 'Заявка на пополнение отправлена'
                };
                
            case '/api/withdraw':
                return {
                    success: true,
                    message: 'Заявка на вывод создана'
                };
                
            case '/api/create-deal':
                return {
                    success: true,
                    message: 'Сделка создана успешно'
                };
                
            case '/api/deal-action':
                return {
                    success: true,
                    message: 'Действие выполнено успешно'
                };
                
            default:
                return {
                    success: false,
                    message: 'Неизвестная ошибка'
                };
        }
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) {
            overlay.classList.add('active');
        } else {
            overlay.classList.remove('active');
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        }[type] || 'fa-info-circle';
        
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="fas ${icon}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-title">${type === 'success' ? 'Успешно' : type === 'error' ? 'Ошибка' : type === 'warning' ? 'Внимание' : 'Информация'}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add close functionality
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        });
        
        container.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
    }

    copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                this.showToast('Адрес скопирован в буфер обмена', 'success');
            }).catch(() => {
                this.fallbackCopyToClipboard(text);
            });
        } else {
            this.fallbackCopyToClipboard(text);
        }
    }

    fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showToast('Адрес скопирован в буфер обмена', 'success');
        } catch (err) {
            this.showToast('Ошибка копирования', 'error');
        }
        
        document.body.removeChild(textArea);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new TelegramMiniApp();
});

// Handle Telegram WebApp events
window.addEventListener('beforeunload', () => {
    if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.close();
    }
});
