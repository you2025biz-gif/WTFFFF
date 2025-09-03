import logging
import json
import os
import time
import string
import random
import asyncio
import shutil
from datetime import datetime
from collections import defaultdict

# Конфигурация
API_TOKEN = os.getenv('API_TOKEN', '8273905158:AAHgvQ6mniKm6i_Ceb_mNzPnxVvgd-K9RDs')
ADMIN_ID = int(os.getenv('ADMIN_ID', '7690554747'))
TON_WALLET_ADDRESS = 'UQCow0sO7p9izwbvm8XMYlEfEirNEW-yXPqyS_rcTmS-GUtg'
COMMISSION = 0.05  # 5%
DATA_FILE = 'bot_data.json'
SPAM_TIMEOUT = 2  # секунды между действиями

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Анти-спам система
user_last_action = defaultdict(float)

def check_spam(user_id):
    current_time = time.time()
    if current_time - user_last_action[user_id] < SPAM_TIMEOUT:
        return True
    user_last_action[user_id] = current_time
    return False

def log_security_event(event_type, user_id, details):
    """Логирование событий безопасности"""
    logging.warning(f"SECURITY: {event_type} - User {user_id} - {details}")

def generate_deal_id():
    """Генерирует случайный ID сделки типа 'GA7X9M2P' (8 символов)"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=8))

def create_backup():
    """Создание резервной копии данных"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_bot_data_{timestamp}.json"
    
    try:
        if os.path.exists(DATA_FILE):
            shutil.copy2(DATA_FILE, backup_file)
            logging.info(f"Backup created: {backup_file}")
            
            # Удаляем старые бэкапы (оставляем только последние 10)
            backup_files = [f for f in os.listdir('.') if f.startswith('backup_bot_data_')]
            backup_files.sort(reverse=True)
            
            for old_backup in backup_files[10:]:
                os.remove(old_backup)
                logging.info(f"Old backup removed: {old_backup}")
                
    except Exception as e:
        logging.error(f"Backup failed: {e}")

# Хранилище данных
users = {}  # user_id: {'balance': float, 'frozen': float}
deals = {}  # deal_id: {...}
pending_topups = {}  # user_id: tx_hash
pending_withdrawals = {}  # user_id: {'amount': float, 'address': str, 'timestamp': float}

def load_data():
    """Загрузка данных из файла"""
    global users, deals, pending_topups, pending_withdrawals
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                users = data.get('users', {})
                # Конвертируем ключи обратно в int
                users = {int(k): v for k, v in users.items()}
                deals = data.get('deals', {})
                pending_topups = data.get('pending_topups', {})
                pending_topups = {int(k): v for k, v in pending_topups.items()}
                pending_withdrawals = data.get('pending_withdrawals', {})
                pending_withdrawals = {int(k): v for k, v in pending_withdrawals.items()}
                logging.info("Данные загружены успешно")
        else:
            # Если файл не существует, создаем его с админом
            users = {}
            deals = {}
            pending_topups = {}
            pending_withdrawals = {}
            logging.info("Файл данных не найден, создаем новый")
        
        # Убеждаемся, что админ существует с балансом 7000 TON
        if ADMIN_ID not in users:
            users[ADMIN_ID] = {'balance': 7000.0, 'frozen': 0.0}
            logging.info(f"Создан админ {ADMIN_ID} с балансом 7000 TON")
        elif users[ADMIN_ID].get('balance', 0) != 7000.0:
            users[ADMIN_ID]['balance'] = 7000.0
            logging.info(f"Обновлен баланс админа {ADMIN_ID} до 7000 TON")
        
        # Сохраняем данные после инициализации админа
        save_data()
        
    except Exception as e:
        logging.error(f"Ошибка загрузки данных: {e}")

def save_data():
    """Сохранение данных в файл"""
    try:
        # Создаем резервную копию перед сохранением (только если файл существует)
        if os.path.exists(DATA_FILE):
            create_backup()
        
        data = {
            'users': {str(k): v for k, v in users.items()},
            'deals': deals,
            'pending_topups': {str(k): v for k, v in pending_topups.items()},
            'pending_withdrawals': {str(k): v for k, v in pending_withdrawals.items()}
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Данные сохранены: users={len(users)}, deals={len(deals)}, pending_topups={len(pending_topups)}, pending_withdrawals={len(pending_withdrawals)}")
        
    except Exception as e:
        logging.error(f"Ошибка сохранения данных: {e}")

def get_balance(user_id):
    """Получить баланс пользователя"""
    if user_id not in users:
        init_user(user_id)
    balance = users.get(user_id, {}).get('balance', 0.0)
    logging.info(f"get_balance: user_id={user_id}, balance={balance}")
    return balance

def get_frozen(user_id):
    """Получить замороженную сумму пользователя"""
    if user_id not in users:
        init_user(user_id)
    return users.get(user_id, {}).get('frozen', 0.0)

def init_user(user_id, save_immediately=False):
    """Инициализация нового пользователя"""
    if user_id not in users:
        logging.info(f"init_user: создаем нового пользователя {user_id}")
        users[user_id] = {'balance': 0.0, 'frozen': 0.0}
        if save_immediately:
            save_data()
    else:
        logging.info(f"init_user: пользователь {user_id} уже существует, balance={users[user_id].get('balance', 0)}")

def get_menu_for_user(user_id):
    """Получить меню для пользователя (админ или обычное)"""
    return user_id == ADMIN_ID
