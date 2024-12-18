import os
from sqlalchemy import Column, Float, ForeignKey, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

# Create a new declarative base
Base = declarative_base()
metadata = Base.metadata

class Device(Base):
    __tablename__ = 'devices'
    device_id = Column(Integer, primary_key=True)
    device_type = Column(Text, nullable=False)
    name = Column(Text, nullable=False)

    metric_types = relationship("MetricType", back_populates="device")

class MetricType(Base):
    __tablename__ = 'metric_types'
    metric_type_id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.device_id'), nullable=False)
    name = Column(Text, nullable=False)

    device = relationship("Device", back_populates="metric_types")
    metrics = relationship("Metric", back_populates="metric_type")

class Metric(Base):
    __tablename__ = 'metrics'
    metric_id = Column(Integer, primary_key=True)
    metric_type_id = Column(Integer, ForeignKey('metric_types.metric_type_id'), nullable=False)
    value = Column(Float, nullable=False)
    client_timestamp = Column(Integer, nullable=False)
    server_timestamp = Column(Integer, nullable=False)

    metric_type = relationship("MetricType", back_populates="metrics")
