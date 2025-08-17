from src.models import db, SyncQueue, SyncLog, Sale, SaleItem, Credit, CreditPayment, SalesGuide, GuideItem, Product, Customer
from datetime import datetime, date

class SyncService:
    @staticmethod
    def process_upload_operations(seller_id, operations, boss_id):
        sync_log = SyncLog(
            seller_id=seller_id,
            sync_type="UPLOAD",
            records_processed=len(operations),
            records_success=0,
            records_failed=0,
            sync_start=datetime.utcnow(),
            status="IN_PROGRESS"
        )
        db.session.add(sync_log)
        db.session.flush()
        
        results = []
        for op in operations:
            operation_type = op.get("operation_type")
            payload = op.get("payload")
            local_id = op.get("local_id")
            
            try:
                if operation_type == "CREATE_SALE":
                    new_sale = Sale(
                        seller_id=seller_id,
                        customer_id=payload.get("customer_id"),
                        payment_type=payload.get("payment_type"),
                        sale_date=datetime.fromisoformat(payload.get("sale_date")).date(),
                        total_amount=payload.get("total_amount"),
                        local_id=local_id,
                        sync_status="SYNCED"
                    )
                    db.session.add(new_sale)
                    db.session.flush()
                    
                    for item_data in payload.get("items", []):
                        new_sale_item = SaleItem(
                            sale_id=new_sale.id,
                            product_id=item_data.get("product_id"),
                            quantity=item_data.get("quantity"),
                            unit_price=item_data.get("unit_price"),
                            subtotal=item_data.get("subtotal")
                        )
                        db.session.add(new_sale_item)
                    
                    if new_sale.payment_type == "credit":
                        new_credit = Credit(
                            sale_id=new_sale.id,
                            customer_id=new_sale.customer_id,
                            amount=new_sale.total_amount,
                            local_id=local_id,
                            sync_status="SYNCED"
                        )
                        db.session.add(new_credit)
                    
                    db.session.commit()
                    results.append({"local_id": local_id, "status": "success", "server_id": new_sale.id})
                    sync_log.records_success += 1
                
                elif operation_type == "CREATE_CREDIT_PAYMENT":
                    credit = Credit.query.filter_by(id=payload.get("credit_id")).first()
                    if not credit:
                        raise ValueError("Credit not found for payment")
                    
                    new_payment = CreditPayment(
                        credit_id=credit.id,
                        amount=payload.get("amount"),
                        payment_date=datetime.fromisoformat(payload.get("payment_date")).date(),
                        local_id=local_id,
                        sync_status="SYNCED"
                    )
                    db.session.add(new_payment)
                    
                    credit.amount_paid += new_payment.amount
                    if credit.amount_paid >= credit.amount:
                        credit.is_paid = True
                        credit.amount_paid = credit.amount
                    
                    db.session.commit()
                    results.append({"local_id": local_id, "status": "success", "server_id": new_payment.id})
                    sync_log.records_success += 1
                
                elif operation_type == "CREATE_GUIDE":
                    new_guide = SalesGuide(
                        seller_id=seller_id,
                        guide_date=datetime.fromisoformat(payload.get("guide_date")).date(),
                        notes=payload.get("notes"),
                        total_taken_value=payload.get("total_taken_value"),
                        local_id=local_id,
                        sync_status="SYNCED"
                    )
                    db.session.add(new_guide)
                    db.session.flush()

                    for item_data in payload.get("items", []):
                        new_guide_item = GuideItem(
                            guide_id=new_guide.id,
                            product_id=item_data.get("product_id"),
                            quantity_taken=item_data.get("quantity_taken"),
                            quantity_remaining=item_data.get("quantity_remaining"),
                            unit_price=item_data.get("unit_price"),
                            total_taken_value=item_data.get("total_taken_value"),
                            total_sold_value=item_data.get("total_sold_value"),
                            total_remaining_value=item_data.get("total_remaining_value"),
                        )
                        db.session.add(new_guide_item)
                    db.session.commit()
                    results.append({"local_id": local_id, "status": "success", "server_id": new_guide.id})
                    sync_log.records_success += 1

                elif operation_type == "CLOSE_GUIDE":
                    guide = SalesGuide.query.filter_by(id=payload.get("server_id"), seller_id=seller_id).first()
                    if not guide:
                        raise ValueError("Sales Guide not found")
                    
                    guide.status = "CLOSED"
                    guide.closed_at = datetime.utcnow()
                    guide.total_sold_value = payload.get("total_sold_value")
                    guide.total_remaining_value = payload.get("total_remaining_value")
                    guide.sync_status = "SYNCED"

                    for item_data in payload.get("items", []):
                        guide_item = GuideItem.query.filter_by(id=item_data.get("server_id"), guide_id=guide.id).first()
                        if guide_item:
                            guide_item.quantity_remaining = item_data.get("quantity_remaining")
                            guide_item.total_sold_value = item_data.get("total_sold_value")
                            guide_item.total_remaining_value = item_data.get("total_remaining_value")
                    db.session.commit()
                    results.append({"local_id": local_id, "status": "success", "server_id": guide.id})
                    sync_log.records_success += 1

                else:
                    raise ValueError(f"Unknown operation type: {operation_type}")

            except Exception as e:
                db.session.rollback()
                results.append({"local_id": local_id, "status": "failed", "error": str(e)})
                sync_log.records_failed += 1
        
        sync_log.complete_sync()
        db.session.commit()
        
        return results, None

    @staticmethod
    def get_download_data(seller_id, boss_id):
        products = Product.query.filter_by(boss_id=boss_id, is_active=True).all()
        customers = Customer.query.filter_by(boss_id=boss_id).all()
        sales = Sale.query.filter_by(seller_id=seller_id).all()
        credits = Credit.query.join(Sale).filter(Sale.seller_id == seller_id).all()
        guides = SalesGuide.query.filter_by(seller_id=seller_id).all()
        
        products_data = [p.to_dict() for p in products]
        customers_data = [c.to_dict() for c in customers]
        sales_data = [s.to_dict() for s in sales]
        credits_data = [c.to_dict() for c in credits]
        guides_data = [g.to_dict() for g in guides]
        
        sync_log = SyncLog(
            seller_id=seller_id,
            sync_type="DOWNLOAD",
            records_processed=len(products_data) + len(customers_data) + len(sales_data) + len(credits_data) + len(guides_data),
            records_success=len(products_data) + len(customers_data) + len(sales_data) + len(credits_data) + len(guides_data),
            records_failed=0,
            sync_start=datetime.utcnow(),
            status="COMPLETED"
        )
        db.session.add(sync_log)
        db.session.commit()
        
        return {
            "products": products_data,
            "customers": customers_data,
            "sales": sales_data,
            "credits": credits_data,
            "guides": guides_data
        }, None


