from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    environment: str = "development"

    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    s3_bucket_name: str = "echohire-reports"

    # Minimum number of candidates in a cohort before we'll compute/display
    # aggregate bias statistics. Protects against re-identifying individuals
    # in small departments/roles.
    min_cohort_size: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
