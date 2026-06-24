"""Environment-backed application configuration."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ASSESSMENT_NUMBER = "+18054398008"


class Settings(BaseSettings):
    """Runtime settings loaded from a local ``.env`` file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    target_phone_number: str = ASSESSMENT_NUMBER
    max_call_seconds: int = Field(default=300, ge=30, le=1000)

    # Public URL (set to your ngrok HTTPS URL)
    public_base_url: str = ""

    # Anthropic
    anthropic_api_key: str = ""
    claude_conversation_model: str = "claude-sonnet-4-6"
    claude_evaluation_model: str = "claude-sonnet-4-6"

    # Conversation behaviour
    response_delay_ms: int = Field(default=500, ge=0, le=3000)

    @property
    def http_base_url(self) -> str:
        return self.public_base_url.rstrip("/")

    @property
    def websocket_base_url(self) -> str:
        if self.http_base_url.startswith("https://"):
            return f"wss://{self.http_base_url.removeprefix('https://')}"
        if self.http_base_url.startswith("http://"):
            return f"ws://{self.http_base_url.removeprefix('http://')}"
        return self.http_base_url

    def validate_call_configuration(self) -> None:
        """Fail early and clearly before any paid call is attempted."""

        if self.target_phone_number != ASSESSMENT_NUMBER:
            raise ValueError(
                f"Calls are restricted to the assessment number {ASSESSMENT_NUMBER}. "
                f"Got: {self.target_phone_number}"
            )

        required = {
            "TWILIO_ACCOUNT_SID": self.twilio_account_sid,
            "TWILIO_AUTH_TOKEN": self.twilio_auth_token,
            "TWILIO_PHONE_NUMBER": self.twilio_phone_number,
            "PUBLIC_BASE_URL": self.public_base_url,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                "Copy .env.example to .env and fill in all values."
            )

        if not self.public_base_url.startswith("https://"):
            raise ValueError(
                "PUBLIC_BASE_URL must start with https://\n"
                "Run ngrok and use the https URL it provides."
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()
