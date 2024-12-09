import os
from sqlalchemy import Column, Float, ForeignKey, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

Base = declarative_base()
metadata = Base.metadata

class Aggregator(Base):
    __tablename__ = 'aggregators'
    aggregator_id = Column(Integer, primary_key=True)
    guid = Column(Text, nullable=False)
    name = Column(Text, nullable=False)

class MetricSnapshot(Base):
    __tablename__ = 'metric_snapshots'
    metric_snapshot_id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.device_id'), nullable=False)
    client_timestamp = Column(Integer, nullable=False)
    server_timestamp = Column(Integer, nullable=False)

class Device(Base):
    __tablename__ = 'devices'
    device_id = Column(Integer, primary_key=True)
    aggregator_id = Column(Integer, ForeignKey('aggregators.aggregator_id'), nullable=False)
    name = Column(Text, nullable=False)
    ordinal = Column(Integer, nullable=False)
    aggregator = relationship('Aggregator')

class DeviceMetricType(Base):
    __tablename__ = 'device_metric_types'
    device_metric_type_id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.device_id'), nullable=False)
    name = Column(Text, nullable=False)
    device = relationship('Device')

class MetricValue(Base):
    __tablename__ = 'metric_values'
    metric_value_id = Column(Integer, primary_key=True)
    metric_snapshot_id = Column(Integer, ForeignKey('metric_snapshots.metric_snapshot_id'), nullable=False)
    device_metric_type_id = Column(Integer, ForeignKey('device_metric_types.device_metric_type_id'), nullable=False)
    value = Column(Float, nullable=False)
    metric_snapshot = relationship('MetricSnapshot')
    device_metric_type = relationship('DeviceMetricType')

    
    