from app.models.user import User
from app.models.order import Order
from app import db
from sqlalchemy import desc

class UserService:
    @staticmethod
    def get_user_by_id(user_id):
        """Get a user by their ID"""
        return User.query.get(user_id)

    @staticmethod
    def update_user(user_id, data):
        """Update a user's profile information"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError('User not found')

        # Update allowed fields
        allowed_fields = ['name', 'email', 'phone']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])

        # Handle password update separately if provided
        if 'password' in data:
            user.set_password(data['password'])

        try:
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'Failed to update user: {str(e)}')

    @staticmethod
    def get_user_preferences(user_id):
        """Get a user's notification preferences"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError('User not found')

        return {
            'email_notifications': user.email_notifications,
            'push_notifications': user.push_notifications,
            'sms_notifications': user.sms_notifications
        }

    @staticmethod
    def update_user_preferences(user_id, data):
        """Update a user's notification preferences"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError('User not found')

        # Update notification preferences
        if 'email_notifications' in data:
            user.email_notifications = data['email_notifications']
        if 'push_notifications' in data:
            user.push_notifications = data['push_notifications']
        if 'sms_notifications' in data:
            user.sms_notifications = data['sms_notifications']

        try:
            db.session.commit()
            return self.get_user_preferences(user_id)
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'Failed to update preferences: {str(e)}')

    @staticmethod
    def get_user_orders(user_id, page=1, per_page=10):
        """Get a user's order history with pagination"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError('User not found')

        # Get orders based on user role
        if user.role == 'customer':
            orders = Order.query.filter_by(customer_id=user_id)
        elif user.role == 'hawker':
            orders = Order.query.filter_by(hawker_id=user_id)
        else:
            raise ValueError('Invalid user role')

        # Apply pagination
        paginated_orders = orders.order_by(desc(Order.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            'orders': [order.to_dict() for order in paginated_orders.items],
            'total': paginated_orders.total,
            'pages': paginated_orders.pages,
            'current_page': page
        } 