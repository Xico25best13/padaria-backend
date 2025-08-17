from datetime import datetime
from . import db


class SyncQueue(db.Model):
    __tablename__ = 'sync_queue'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=False)
    operation_type = db.Column(db.Enum('CREATE_SALE', 'UPDATE_SALE', 'CREATE_CREDIT_PAYMENT', 'CREATE_GUIDE', 'UPDATE_GUIDE', 'CLOSE_GUIDE', name='operation_type'), nullable=False)
    data = db.Column(db.JSON, nullable=False)
    local_id = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='sync_status'), default='PENDING')
    attempts = db.Column(db.Integer, default=0)
    last_attempt = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    error_message = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'seller_id': self.seller_id,
            'operation_type': self.operation_type,
            'data': self.data,
            'local_id': self.local_id,
            'status': self.status,
            'attempts': self.attempts,
            'last_attempt': self.last_attempt.isoformat() if self.last_attempt else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'error_message': self.error_message
        }
    
    def mark_processing(self):
        """Marca a operação como em processamento"""
        self.status = 'PROCESSING'
        self.attempts += 1
        self.last_attempt = datetime.utcnow()
    
    def mark_completed(self):
        """Marca a operação como concluída"""
        self.status = 'COMPLETED'
        self.error_message = None
    
    def mark_failed(self, error_message):
        """Marca a operação como falhada"""
        self.status = 'FAILED'
        self.error_message = error_message
    
    def __repr__(self):
        return f'<SyncQueue {self.id} - {self.operation_type} ({self.status})>'


class SyncLog(db.Model):
    __tablename__ = 'sync_log'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=False)
    sync_type = db.Column(db.Enum('UPLOAD', 'DOWNLOAD', name='sync_type'), nullable=False)
    records_processed = db.Column(db.Integer, nullable=False)
    records_success = db.Column(db.Integer, nullable=False)
    records_failed = db.Column(db.Integer, nullable=False)
    sync_start = db.Column(db.DateTime, nullable=False)
    sync_end = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum('IN_PROGRESS', 'COMPLETED', 'FAILED', name='sync_log_status'), nullable=False)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'seller_id': self.seller_id,
            'sync_type': self.sync_type,
            'records_processed': self.records_processed,
            'records_success': self.records_success,
            'records_failed': self.records_failed,
            'sync_start': self.sync_start.isoformat() if self.sync_start else None,
            'sync_end': self.sync_end.isoformat() if self.sync_end else None,
            'status': self.status,
            'duration_seconds': (self.sync_end - self.sync_start).total_seconds() if self.sync_end and self.sync_start else None
        }
    
    def complete_sync(self):
        """Marca a sincronização como concluída"""
        self.sync_end = datetime.utcnow()
        self.status = 'COMPLETED'
    
    def fail_sync(self):
        """Marca a sincronização como falhada"""
        self.sync_end = datetime.utcnow()
        self.status = 'FAILED'
    
    def __repr__(self):
        return f'<SyncLog {self.id} - {self.sync_type} ({self.status})>'

