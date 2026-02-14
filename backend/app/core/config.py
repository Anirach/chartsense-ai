from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://chartsense:chartsense_secret_2026@localhost:5432/chartsense_db"
    redis_url: str = "redis://localhost:6379/0"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "chartsense_neo4j_2026"
    secret_key: str = "chartsense-secret"
    demo_mode: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
