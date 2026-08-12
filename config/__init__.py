from .development import DevelopmentConfig
from .production import ProductionConfig

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
