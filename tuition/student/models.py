from sqlalchemy import Column, String, Text, DateTime, func, ForeignKey, Numeric, Date, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from tuition.database import Base


class Student(Base):
    __tablename__ = 'students'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    bio = Column(Text, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    address = Column(Text, nullable=True)

    full_name = Column(String(255), nullable=False)
    email = Column(Text, unique=True, nullable=False)
    role = Column(String, nullable=False, default = 'user')
    phone_number = Column(Text, nullable=False)
    hashed_password = Column(String, nullable=False)
    field_of_interest = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # timezone-aware
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # timezone-aware

    applications = relationship('Application', back_populates= 'student')

    # transactions = relationship('Transaction', back_populates='students')
    # payments = relationship('Payment', back_populates='students')


    
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


class Transaction(Base):

    __tablename__ = 'transactions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_id = Column(UUID, ForeignKey('students.id'))
    transaction_date = Column(DateTime, default=func.now())
    transaction_type = Column(String, nullable=False)
    amount = Column(Numeric, nullable=False)
    status = Column(String, default='Completed')

    # institution_id = Column(UUID, ForeignKey('institutions.id'))
    # payments = relationship('Payment', back_populates='transactions')


class Application(Base):
    __tablename__ = 'applications'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    application_date = Column(DateTime, default=func.now(), nullable=False)
    updated_date = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)  
    status = Column(String, default='Pending', nullable=False)
    custom_fields = Column(JSON, default={}, nullable=True)  

    student_id = Column(UUID, ForeignKey('students.id'), nullable=False)  
    application_type_id = Column(UUID, ForeignKey('programs.id'), nullable=True)  

    application_type = Column(String(255), nullable=False)

    program = relationship("Program", back_populates="applications")
    student = relationship("Student", back_populates="applications")

    



