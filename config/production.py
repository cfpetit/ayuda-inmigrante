import os
from .default import Config

class ProductionConfig(Config):
    DEBUG = False

