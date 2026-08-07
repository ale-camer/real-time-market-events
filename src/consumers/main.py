# Entrypoint for the Faust application
# Import agents to ensure they are registered with the Faust app
import src.consumers.agents  # noqa: F401
from src.consumers.app import app

if __name__ == "__main__":
    app.main()
