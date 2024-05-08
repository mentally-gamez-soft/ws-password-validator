"""Configure the application with envs."""

from core.configuration.env.env_config import AppConfig, EnvLoader

# Expose Config object for app to import
env_loader = EnvLoader()
env_loader.get_env_config()
config = AppConfig(env_loader.env)
app_env = config.get_application_env()
