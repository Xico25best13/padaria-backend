from flask import Blueprint, jsonify
from werkzeug.security import generate_password_hash
from src.models import db, Boss, Seller, Product, Customer
import secrets
import string

init_bp = Blueprint('init', __name__)

def generate_token(length=16):
    """Gerar token aleatório para vendedores"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@init_bp.route('/init', methods=['POST'])
def initialize_data():
    """Inicializar a base de dados com dados de teste"""
    try:
        # Verificar se já existem dados
        if Boss.query.first() or Seller.query.first():
            return jsonify({'message': 'Dados já existem na base de dados'}), 400

        # Criar patrão de teste
        boss = Boss(
            name='João Silva',
            email='joao@padaria.com',
            password_hash=generate_password_hash('123456')
        )
        db.session.add(boss)
        db.session.flush()  # Para obter o ID

        # Criar vendedores de teste
        sellers_data = [
            {'name': 'Maria Santos', 'token': generate_token()},
            {'name': 'António Costa', 'token': generate_token()},
            {'name': 'Ana Ferreira', 'token': generate_token()}
        ]

        sellers = []
        for seller_data in sellers_data:
            seller = Seller(
                name=seller_data['name'],
                token=seller_data['token'],
                boss_id=boss.id
            )
            sellers.append(seller)
            db.session.add(seller)

        # Criar produtos de teste
        products_data = [
            {'name': 'Pão de Forma', 'price': 1.20},
            {'name': 'Pão Integral', 'price': 1.50},
            {'name': 'Croissant', 'price': 0.80},
            {'name': 'Bolo de Chocolate', 'price': 12.00},
            {'name': 'Pastel de Nata', 'price': 1.00},
            {'name': 'Broa de Milho', 'price': 2.50}
        ]

        products = []
        for product_data in products_data:
            product = Product(
                name=product_data['name'],
                price=product_data['price'],
                boss_id=boss.id
            )
            products.append(product)
            db.session.add(product)

        # Criar clientes de teste
        customers_data = [
            {'name': 'Carlos Mendes', 'address': 'Rua das Flores, 123', 'phone': '912345678'},
            {'name': 'Isabel Rodrigues', 'address': 'Av. da Liberdade, 456', 'phone': '923456789'},
            {'name': 'Pedro Oliveira', 'address': 'Praça da República, 789', 'phone': '934567890'},
            {'name': 'Luísa Pereira', 'address': 'Rua do Comércio, 321', 'phone': '945678901'}
        ]

        customers = []
        for customer_data in customers_data:
            customer = Customer(
                name=customer_data['name'],
                address=customer_data['address'],
                phone=customer_data['phone'],
                boss_id=boss.id
            )
            customers.append(customer)
            db.session.add(customer)

        # Confirmar todas as alterações
        db.session.commit()

        # Preparar resposta com os dados criados
        response_data = {
            'message': 'Dados de teste criados com sucesso!',
            'boss': {
                'id': boss.id,
                'name': boss.name,
                'email': boss.email
            },
            'sellers': [
                {
                    'id': seller.id,
                    'name': seller.name,
                    'token': seller.token
                } for seller in sellers
            ],
            'products': [
                {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price
                } for product in products
            ],
            'customers': [
                {
                    'id': customer.id,
                    'name': customer.name,
                    'address': customer.address,
                    'phone': customer.phone
                } for customer in customers
            ]
        }

        return jsonify(response_data), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao criar dados de teste: {str(e)}'}), 500

@init_bp.route('/reset', methods=['POST'])
def reset_database():
    """Limpar toda a base de dados"""
    try:
        # Eliminar todos os dados (em ordem devido às foreign keys)
        from src.models import Sale, SaleItem, Credit, CreditPayment, SalesGuide, GuideItem, SyncOperation
        
        SaleItem.query.delete()
        Sale.query.delete()
        CreditPayment.query.delete()
        Credit.query.delete()
        GuideItem.query.delete()
        SalesGuide.query.delete()
        SyncOperation.query.delete()
        Customer.query.delete()
        Product.query.delete()
        Seller.query.delete()
        Boss.query.delete()
        
        db.session.commit()
        
        return jsonify({'message': 'Base de dados limpa com sucesso!'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao limpar base de dados: {str(e)}'}), 500

@init_bp.route('/status', methods=['GET'])
def database_status():
    """Verificar o estado da base de dados"""
    try:
        boss_count = Boss.query.count()
        seller_count = Seller.query.count()
        product_count = Product.query.count()
        customer_count = Customer.query.count()
        
        return jsonify({
            'database_status': 'connected',
            'counts': {
                'bosses': boss_count,
                'sellers': seller_count,
                'products': product_count,
                'customers': customer_count
            }
        }), 200

    except Exception as e:
        return jsonify({'message': f'Erro ao verificar base de dados: {str(e)}'}), 500

