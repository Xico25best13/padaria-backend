import os
import sys
# DON\'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.models import db
from src.routes.auth import auth_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string-change-in-production'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

# Configurar CORS para permitir requisições do frontend
CORS(app, origins='*')

# Configurar JWT
jwt = JWTManager(app)

from src.models import Boss, Seller

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    if identity["role"] == "boss":
        return Boss.query.get(identity["id"])
    elif identity["role"] == "seller":
        return Seller.query.get(identity["id"])
    return None

# Importar e registar blueprints
from src.routes.seller import seller_bp
from src.routes.product import product_bp
from src.routes.customer import customer_bp
from src.routes.sale import sale_bp
from src.routes.credit import credit_bp
from src.routes.guide import guide_bp
from src.routes.sync import sync_bp
from src.routes.init import init_bp

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(seller_bp, url_prefix="/api")
app.register_blueprint(product_bp, url_prefix="/api")
app.register_blueprint(customer_bp, url_prefix="/api")
app.register_blueprint(sale_bp, url_prefix="/api")
app.register_blueprint(credit_bp, url_prefix="/api")
app.register_blueprint(guide_bp, url_prefix="/api")
app.register_blueprint(sync_bp, url_prefix="/api")
app.register_blueprint(init_bp, url_prefix="/api")

# Configuração da base de dados
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://user:password@host:port/database")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Criar todas as tabelas
with app.app_context():
    db.create_all()

# Rota para servir o frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    # Se é um ficheiro específico que existe, servir esse ficheiro
    if path and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    
    # Caso contrário, servir o index.html (para Single Page Application)
    index_path = os.path.join(static_folder_path, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(static_folder_path, 'index.html')
    else:
        return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)


