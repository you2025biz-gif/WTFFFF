#!/usr/bin/env python3
"""
Backend API для Telegram Mini App
Обрабатывает запросы от веб-интерфейса
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional

from aiohttp import web, ClientSession
from aiohttp.web import Request, Response
import aiohttp_cors

# Импортируем функции из основного бота
from config import load_data, save_data, users, deals, pending_topups, pending_withdrawals, init_user

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация
API_TOKEN = '8273905158:AAHgvQ6mniKm6i_Ceb_mNzPnxVvgd-K9RDs'
ADMIN_ID = 7690554747
TON_WALLET_ADDRESS = 'UQCow0sO7p9izwbvm8XMYlEfEirNEW-yXPqyS_rcTmS-GUtg'

class MiniAppAPI:
    def __init__(self):
        self.app = web.Application()
        self.setup_cors()
        self.setup_routes()
        load_data()  # Загружаем данные при инициализации

    def setup_cors(self):
        """Настройка CORS для веб-интерфейса"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })

        # Добавляем CORS ко всем маршрутам
        for route in list(self.app.router.routes()):
            cors.add(route)

    def setup_routes(self):
        """Настройка маршрутов API"""
        # Статические файлы
        self.app.router.add_get('/', self.serve_index)
        self.app.router.add_get('/index.html', self.serve_index)
        self.app.router.add_get('/styles.css', self.serve_css)
        self.app.router.add_get('/app.js', self.serve_js)
        self.app.router.add_get('/config.js', self.serve_config)
        
        # API маршруты
        self.app.router.add_post('/api/user', self.get_user_data)
        self.app.router.add_post('/api/deals', self.get_deals)
        self.app.router.add_post('/api/history', self.get_history)
        self.app.router.add_post('/api/topup', self.create_topup)
        self.app.router.add_post('/api/withdraw', self.create_withdraw)
        self.app.router.add_post('/api/create-deal', self.create_deal)
        self.app.router.add_post('/api/deal-action', self.deal_action)
        self.app.router.add_post('/api/sync-data', self.sync_data)
        self.app.router.add_get('/api/health', self.health_check)

    async def serve_index(self, request: Request) -> Response:
        """Обслуживание главной страницы"""
        try:
            with open('index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        except FileNotFoundError:
            return web.Response(text='<h1>Mini App не найден</h1>', status=404)
    
    async def serve_css(self, request: Request) -> Response:
        """Обслуживание CSS файла"""
        try:
            with open('styles.css', 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/css')
        except FileNotFoundError:
            return web.Response(text='/* CSS не найден */', status=404)
    
    async def serve_js(self, request: Request) -> Response:
        """Обслуживание JavaScript файла"""
        try:
            with open('app.js', 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='application/javascript')
        except FileNotFoundError:
            return web.Response(text='// JS не найден', status=404)
    
    async def serve_config(self, request: Request) -> Response:
        """Обслуживание конфигурационного файла"""
        try:
            with open('config.js', 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='application/javascript')
        except FileNotFoundError:
            return web.Response(text='// Config не найден', status=404)

    async def sync_data(self, request: Request) -> Response:
        """Синхронизация данных с основным ботом"""
        try:
            data = await request.json()
            
            # Обновляем глобальные переменные
            global users, deals, pending_topups, pending_withdrawals
            
            users.clear()
            users.update(data.get('users', {}))
            
            deals.clear()
            deals.update(data.get('deals', {}))
            
            pending_topups.clear()
            pending_topups.update(data.get('pending_topups', {}))
            
            pending_withdrawals.clear()
            pending_withdrawals.update(data.get('pending_withdrawals', {}))
            
            # Сохраняем данные
            save_data()
            
            logger.info(f"Данные синхронизированы: users={len(users)}, deals={len(deals)}")
            
            return web.json_response({
                'status': 'success',
                'message': 'Данные успешно синхронизированы',
                'users_count': len(users),
                'deals_count': len(deals),
                'admin_balance': users.get(str(ADMIN_ID), {}).get('balance', 0)
            })
            
        except Exception as e:
            logger.error(f"Ошибка синхронизации данных: {e}")
            return web.json_response({
                'status': 'error',
                'message': str(e)
            }, status=500)

    async def health_check(self, request: Request) -> Response:
        """Проверка здоровья API"""
        return web.json_response({
            'status': 'ok',
            'timestamp': time.time(),
            'version': '1.0.0'
        })

    async def get_user_data(self, request: Request) -> Response:
        """Получение данных пользователя"""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            
            if not user_id:
                return web.json_response({
                    'success': False,
                    'message': 'User ID is required'
                }, status=400)

            # Инициализируем пользователя если не существует
            init_user(user_id, save_immediately=True)
            
            user_data = users.get(user_id, {'balance': 0.0, 'frozen': 0.0})
            
            return web.json_response({
                'success': True,
                'data': {
                    'balance': user_data['balance'],
                    'frozen': user_data['frozen'],
                    'available': user_data['balance'] - user_data['frozen']
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            return web.json_response({
                'success': False,
                'message': 'Internal server error'
            }, status=500)

    async def get_deals(self, request: Request) -> Response:
        """Получение сделок пользователя"""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            
            if not user_id:
                return web.json_response({
                    'success': False,
                    'message': 'User ID is required'
                }, status=400)

            # Получаем сделки пользователя
            user_deals = []
            for deal_id, deal in deals.items():
                if (deal.get('creator_id') == user_id or 
                    deal.get('buyer_id') == user_id):
                    user_deals.append({
                        'id': deal_id,
                        'name': deal.get('name', ''),
                        'type': deal.get('type', ''),
                        'sum': deal.get('sum', 0),
                        'status': deal.get('status', ''),
                        'creator_id': deal.get('creator_id'),
                        'buyer_id': deal.get('buyer_id'),
                        'created_at': deal.get('created_at', ''),
                        'link': f"https://t.me/your_bot?start=deal_{deal_id}"
                    })
            
            return web.json_response({
                'success': True,
                'data': {
                    'deals': user_deals
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting deals: {e}")
            return web.json_response({
                'success': False,
                'message': 'Internal server error'
            }, status=500)

    async def get_history(self, request: Request) -> Response:
        """Получение истории операций"""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            
            if not user_id:
                return web.json_response({
                    'success': False,
                    'message': 'User ID is required'
                }, status=400)

            # Генерируем историю операций
            history = []
            
            # Добавляем пополнения
            if user_id in pending_topups:
                topup = pending_topups[user_id]
                history.append({
                    'type': 'topup',
                    'title': 'Заявка на пополнение',
                    'description': f"TX: {topup.get('tx_hash', 'Ожидается...')}",
                    'amount': topup.get('amount', 0),
                    'date': datetime.fromtimestamp(topup.get('timestamp', time.time())).isoformat(),
                    'status': 'pending'
                })
            
            # Добавляем выводы
            if user_id in pending_withdrawals:
                withdrawal = pending_withdrawals[user_id]
                history.append({
                    'type': 'withdraw',
                    'title': 'Заявка на вывод',
                    'description': f"Адрес: {withdrawal.get('address', '')[:20]}...",
                    'amount': -withdrawal.get('amount', 0),
                    'date': datetime.fromtimestamp(withdrawal.get('timestamp', time.time())).isoformat(),
                    'status': 'pending'
                })
            
            # Добавляем сделки
            for deal_id, deal in deals.items():
                if deal.get('creator_id') == user_id or deal.get('buyer_id') == user_id:
                    deal_type = deal.get('type', '')
                    deal_name = deal.get('name', '')
                    deal_sum = deal.get('sum', 0)
                    
                    if deal.get('status') == 'completed':
                        if deal_type == 'sell' and deal.get('creator_id') == user_id:
                            # Продавец получил деньги
                            history.append({
                                'type': 'deal',
                                'title': 'Продажа подарка',
                                'description': deal_name,
                                'amount': deal_sum * 0.95,  # Минус комиссия 5%
                                'date': deal.get('completed_at', ''),
                                'status': 'completed'
                            })
                        elif deal_type == 'buy' and deal.get('buyer_id') == user_id:
                            # Покупатель получил подарок
                            history.append({
                                'type': 'deal',
                                'title': 'Покупка подарка',
                                'description': deal_name,
                                'amount': -deal_sum,
                                'date': deal.get('completed_at', ''),
                                'status': 'completed'
                            })
                    elif deal.get('status') == 'frozen':
                        if deal_type == 'sell' and deal.get('creator_id') == user_id:
                            # Продавец заморозил средства
                            history.append({
                                'type': 'deal',
                                'title': 'Создание сделки',
                                'description': deal_name,
                                'amount': -deal_sum,
                                'date': deal.get('created_at', ''),
                                'status': 'frozen'
                            })
                        elif deal_type == 'buy' and deal.get('buyer_id') == user_id:
                            # Покупатель заморозил средства
                            history.append({
                                'type': 'deal',
                                'title': 'Участие в сделке',
                                'description': deal_name,
                                'amount': -deal_sum,
                                'date': deal.get('joined_at', ''),
                                'status': 'frozen'
                            })
            
            # Сортируем по дате (новые сверху)
            history.sort(key=lambda x: x['date'], reverse=True)
            
            return web.json_response({
                'success': True,
                'data': {
                    'history': history
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return web.json_response({
                'success': False,
                'message': 'Internal server error'
            }, status=500)

    async def create_topup(self, request: Request) -> Response:
        """Создание заявки на пополнение"""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            amount = data.get('amount')
            tx_hash = data.get('tx_hash')
            
            if not all([user_id, amount, tx_hash]):
                return web.json_response({
                    'success': False,
                    'message': 'Missing required fields'
                }, status=400)

            amount = float(amount)
            if amount <= 0 or amount > 1000:
                return web.json_response({
                    'success': False,
                    'message': 'Invalid amount'
                }, status=400)

            # Проверяем, нет ли уже активной заявки
            if user_id in pending_topups:
                return web.json_response({
                    'success': False,
                    'message': 'У вас уже есть активная заявка на пополнение'
                }, status=400)

            # Создаем заявку на пополнение
            pending_topups[user_id] = {
                'amount': amount,
                'tx_hash': tx_hash,
                'timestamp': time.time()
            }
            
            save_data()
            
            # Уведомляем админа (здесь можно добавить отправку уведомления)
            logger.info(f"New topup request: User {user_id}, Amount {amount}, TX {tx_hash}")
            
            return web.json_response({
                'success': True,
                'message': 'Заявка на пополнение создана'
            })
            
        except Exception as e:
            logger.error(f"Error creating topup: {e}")
            return web.json_response({
                'success': False,
                'message': 'Internal server error'
            }, status=500)

    async def create_withdraw(self, request: Request) -> Response:
        """Создание заявки на вывод"""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            amount = data.get('amount')
            address = data.get('address')
            
            if not all([user_id, amount, address]):
                return web.json_response({
                    'success': False,
                    'message': 'Missing required fields'
                }, status=400)

            amount = float(amount)
            if amount <= 0:
                return web.json_response({
                    'success': False,
                    'message': 'Invalid amount'
                }, status=400)

            # Инициализируем пользователя
            init_user(user_id, save_immediately=True)
            
            # Проверяем баланс
            available = users[user_id]['balance'] - users[user_id]['frozen']
            if amount > available:
                return web.json_response({
                    'success': False,
                    'message': 'Недостаточно средств'
                }, status=400)

            # Проверяем, нет ли уже активной заявки
            if user_id in pending_withdrawals:
                return web.json_response({
                    'success': False,
                    'message': 'У вас уже есть активная заявка на вывод'
                }, status=400)

            # Создаем заявку на вывод
            pending_withdrawals[user_id] = {
                'amount': amount,
                'address': address,
                'timestamp': time.time()
            }
            
            save_data()
            
            # Уведомляем админа
            logger.info(f"New withdrawal request: User {user_id}, Amount {amount}, Address {address}")
            
            return web.json_response({
                'success': True,
                'message': 'Заявка на вывод создана'
            })
            
        except Exception as e:
            logger.error(f"Error creating withdraw: {e}")
            return web.json_response({
                'success': False,
                'message': 'Internal server error'
            }, status=500)

    async def create_deal(self, request: Request) -> Response:
        """Создание сделки"""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            deal_type = data.get('type')
            name = data.get('name')
            amount = data.get('amount')
            
            if not all([user_id, deal_type, name, amount]):
                return web.json_response({
                    'success': False,
                    'message': 'Missing required fields'
                }, status=400)

            amount = float(amount)
            if amount <= 0:
                return web.json_response({
                    'success': False,
                    'message': 'Invalid amount'
                }, status=400)

            # Инициализируем пользователя
            init_user(user_id, save_immediately=True)
            
            # Проверяем баланс для продажи
            if deal_type == 'sell':
                available = users[user_id]['balance'] - users[user_id]['frozen']
                if amount > available:
                    return web.json_response({
                        'success': False,
                        'message': 'Недостаточно средств для создания сделки'
                    }, status=400)

            # Создаем сделку
            deal_id = len(deals) + 1
            deals[deal_id] = {
                'creator_id': user_id,
                'type': deal_type,
                'name': name,
                'sum': amount,
                'status': 'waiting',
                'created_at': datetime.now().isoformat(),
                'buyer_id': None
            }
            
            # Замораживаем средства для продажи
            if deal_type == 'sell':
                users[user_id]['frozen'] += amount
            
            save_data()
            
            logger.info(f"New deal created: ID {deal_id}, Type {deal_type}, Amount {amount}")
            
            return web.json_response({
                'success': True,
                'message': 'Сделка создана успешно',
                'data': {
                    'deal_id': deal_id
                }
            })
            
        except Exception as e:
            logger.error(f"Error creating deal: {e}")
            return web.json_response({
                'success': False,
                'message': 'Internal server error'
            }, status=500)

    async def deal_action(self, request: Request) -> Response:
        """Выполнение действия со сделкой"""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            deal_id = data.get('deal_id')
            action = data.get('action')
            
            if not all([user_id, deal_id, action]):
                return web.json_response({
                    'success': False,
                    'message': 'Missing required fields'
                }, status=400)

            deal_id = int(deal_id)
            if deal_id not in deals:
                return web.json_response({
                    'success': False,
                    'message': 'Сделка не найдена'
                }, status=404)

            deal = deals[deal_id]
            
            # Выполняем действие в зависимости от типа
            if action == 'join':
                if deal['status'] != 'waiting' or deal['creator_id'] == user_id:
                    return web.json_response({
                        'success': False,
                        'message': 'Невозможно присоединиться к сделке'
                    }, status=400)

                # Инициализируем пользователя
                init_user(user_id, save_immediately=True)
                
                # Проверяем баланс
                available = users[user_id]['balance'] - users[user_id]['frozen']
                if deal['sum'] > available:
                    return web.json_response({
                        'success': False,
                        'message': 'Недостаточно средств'
                    }, status=400)

                # Присоединяемся к сделке
                deal['buyer_id'] = user_id
                deal['status'] = 'joined'
                deal['joined_at'] = datetime.now().isoformat()
                
                # Замораживаем средства для покупки
                if deal['type'] == 'buy':
                    users[user_id]['frozen'] += deal['sum']
                
                save_data()
                
                return web.json_response({
                    'success': True,
                    'message': 'Вы присоединились к сделке'
                })

            elif action == 'cancel':
                if deal['creator_id'] != user_id or deal['status'] != 'waiting':
                    return web.json_response({
                        'success': False,
                        'message': 'Невозможно отменить сделку'
                    }, status=400)

                # Отменяем сделку
                deal['status'] = 'cancelled'
                deal['cancelled_at'] = datetime.now().isoformat()
                
                # Размораживаем средства
                if deal['type'] == 'sell':
                    users[user_id]['frozen'] -= deal['sum']
                
                save_data()
                
                return web.json_response({
                    'success': True,
                    'message': 'Сделка отменена'
                })

            elif action == 'send-gift':
                # Логика передачи подарка
                if deal['status'] not in ['joined', 'frozen']:
                    return web.json_response({
                        'success': False,
                        'message': 'Невозможно передать подарок'
                    }, status=400)

                # Проверяем, кто может передать подарок
                can_send = False
                if deal['type'] == 'sell' and deal['creator_id'] == user_id:
                    can_send = True
                elif deal['type'] == 'buy' and deal['buyer_id'] == user_id:
                    can_send = True

                if not can_send:
                    return web.json_response({
                        'success': False,
                        'message': 'Вы не можете передать подарок в этой сделке'
                    }, status=400)

                # Обновляем статус
                deal['status'] = 'gift_sent'
                deal['gift_sent_at'] = datetime.now().isoformat()
                
                save_data()
                
                return web.json_response({
                    'success': True,
                    'message': 'Подарок передан'
                })

            elif action == 'confirm':
                # Логика подтверждения получения
                if deal['status'] != 'gift_sent':
                    return web.json_response({
                        'success': False,
                        'message': 'Невозможно подтвердить получение'
                    }, status=400)

                # Проверяем, кто может подтвердить
                can_confirm = False
                if deal['type'] == 'sell' and deal['buyer_id'] == user_id:
                    can_confirm = True
                elif deal['type'] == 'buy' and deal['creator_id'] == user_id:
                    can_confirm = True

                if not can_confirm:
                    return web.json_response({
                        'success': False,
                        'message': 'Вы не можете подтвердить получение в этой сделке'
                    }, status=400)

                # Завершаем сделку
                deal['status'] = 'completed'
                deal['completed_at'] = datetime.now().isoformat()
                
                # Переводим средства
                commission = deal['sum'] * 0.05  # 5% комиссия
                
                if deal['type'] == 'sell':
                    # Продавец получает деньги (минус комиссия)
                    seller_id = deal['creator_id']
                    buyer_id = deal['buyer_id']
                    
                    # Размораживаем средства покупателя
                    users[buyer_id]['frozen'] -= deal['sum']
                    
                    # Зачисляем продавцу
                    users[seller_id]['frozen'] -= deal['sum']
                    users[seller_id]['balance'] += deal['sum'] - commission
                    
                    # Комиссия идет админу
                    users[ADMIN_ID]['balance'] += commission
                    
                else:  # buy
                    # Покупатель получает подарок
                    buyer_id = deal['buyer_id']
                    seller_id = deal['creator_id']
                    
                    # Размораживаем средства покупателя
                    users[buyer_id]['frozen'] -= deal['sum']
                    
                    # Зачисляем продавцу
                    users[seller_id]['balance'] += deal['sum'] - commission
                    
                    # Комиссия идет админу
                    users[ADMIN_ID]['balance'] += commission
                
                save_data()
                
                return web.json_response({
                    'success': True,
                    'message': 'Сделка завершена успешно'
                })

            else:
                return web.json_response({
                    'success': False,
                    'message': 'Неизвестное действие'
                }, status=400)
                
        except Exception as e:
            logger.error(f"Error handling deal action: {e}")
            return web.json_response({
                'success': False,
                'message': 'Internal server error'
            }, status=500)

    def run(self, host='0.0.0.0', port=8080):
        """Запуск API сервера"""
        logger.info(f"Starting Mini App API server on {host}:{port}")
        web.run_app(self.app, host=host, port=port)

if __name__ == '__main__':
    api = MiniAppAPI()
    port = int(os.getenv('PORT', 8080))
    api.run(port=port)
