// Конфигурация Mini App
const CONFIG = {
    // URL вашего API сервера (замените на ваш домен)
    API_BASE_URL: 'https://garant-bot-mini-app-b961dcec28c0.herokuapp.com',
    
    // URL Mini App (замените на ваш домен)
    MINI_APP_URL: 'https://your-domain.com/mini_app/',
    
    // Настройки Telegram
    BOT_TOKEN: '8273905158:AAHgvQ6mniKm6i_Ceb_mNzPnxVvgd-K9RDs',
    ADMIN_ID: 7690554747,
    
    // Настройки кошелька
    TON_WALLET_ADDRESS: 'UQCow0sO7p9izwbvm8XMYlEfEirNEW-yXPqyS_rcTmS-GUtg',
    
    // Настройки приложения
    APP_NAME: 'Гарант-Бот',
    APP_VERSION: '1.0.0',
    
    // Лимиты
    MAX_TOPUP_AMOUNT: 1000,
    MIN_DEAL_AMOUNT: 0.01,
    COMMISSION_RATE: 0.05, // 5%
    
    // Настройки UI
    THEME: {
        PRIMARY_COLOR: '#007AFF',
        SUCCESS_COLOR: '#34C759',
        ERROR_COLOR: '#FF3B30',
        WARNING_COLOR: '#FF9500'
    },
    
    // Настройки API
    API_TIMEOUT: 10000, // 10 секунд
    RETRY_ATTEMPTS: 3,
    
    // Настройки уведомлений
    TOAST_DURATION: 5000, // 5 секунд
    AUTO_REFRESH_INTERVAL: 30000 // 30 секунд
};

// Экспортируем конфигурацию
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
} else {
    window.CONFIG = CONFIG;
}
