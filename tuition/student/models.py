from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import json

from sqlalchemy import Column, String, Boolean, Text
from tuition.database import Base


class Student(Base):
    __tablename__ = 'students'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(Text, unique=True, nullable=False)
    role = Column(String, nullable=False, default = 'user')
    phone_number = Column(Text, nullable=False)
    hashed_password = Column(String, nullable=False)
    field_of_interest = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # timezone-aware
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # timezone-aware

    # transactions = relationship('Transaction', back_populates='students')
    # payments = relationship('Payment', back_populates='students')
    # def to_json(self):
    #     """Convert the instance to a JSON string"""
    #     return json.dumps(self.to_dict(), default=str)

    # def __repr__(self):
    #     """Representation method can return the object as a dict or JSON instead of a string"""
    #     return self.to_json()
    
#exclude = True


# class Payment(Base):
#     __tablename__ = 'payments'

#     id = Column(Integer, primary_key=True, index=True)
#     student_id = Column(Integer, ForeignKey('students.id'))
#     transaction_id = Column(Integer, ForeignKey('transactions.id'))
#     amount = Column(Numeric, nullable=False)
#     payment_date = Column(DateTime, default=lambda: datetime.now)
#     payment_status = Column(String, default='Completed')

#     student = relationship('Student', back_populates='payments')
#     transaction = relationship('Transaction', back_populates='payments')