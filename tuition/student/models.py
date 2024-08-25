from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric
from decimal import Decimal
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, Text, Date
from tuition.database import Base


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    phone_number = Column(Text, nullable=False)
    hashed_password = Column(String, nullable=False)
    field_of_interest = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))

    # transactions = relationship('Transaction', back_populates='students')
    # payments = relationship('Payment', back_populates='students')

    def __repr__(self):
        return f"<User {self.full_name}>"
    
    
#exclude = True


# class Payment(Base):
#     __tablename__ = 'payments'

#     id = Column(Integer, primary_key=True, index=True)
#     student_id = Column(Integer, ForeignKey('students.id'))
#     transaction_id = Column(Integer, ForeignKey('transactions.id'))
#     amount = Column(Numeric, nullable=False)
#     payment_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
#     payment_status = Column(String, default='Completed')

#     student = relationship('Student', back_populates='payments')
#     transaction = relationship('Transaction', back_populates='payments')