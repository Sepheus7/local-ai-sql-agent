# AI SQL Agent

This project is an AI-powered SQL agent that can generate SQL queries from natural language questions and execute them on a PostgreSQL database.

## Prerequisites

- Docker
- Docker Compose
- LM Studio (Ensure you have a server running on LM Studio)

## Setup

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/ai-sql-agent.git
    cd ai-sql-agent
    ```

2. Build and run the application using Docker Compose:

    ```sh
    docker-compose up --build
    ```

3. Access the application:

    Open your web browser and navigate to `http://localhost:8501`.

## Stopping the Application

To stop the application, press `Ctrl+C` in the terminal where Docker Compose is running, or run:

    ```sh
    docker-compose down
    ```

## Cleaning Up

To remove the Docker containers and volumes, run:

    ```sh
    docker-compose down -v
    ```

## Database Population

The database is automatically populated with synthetic data when the application starts. The `populate_db.py` script is executed to create the `employees` table and insert synthetic data.


## Project Structure

The project has the following structure:

```
ai-sql-agent/
├── docker-compose.yml
├── Dockerfile
├── README.md
├── app/
│   ├── __init__.py
│   ├── streamlit_app.py
│   ├── populate_db.py
│   ├── database.py
│   └── agent.py
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   └── test_database.py
└── requirements.txt
```

- **Dockerfile**: Defines the Docker image for the application.
- **docker-compose.yml**: Defines the services (application and PostgreSQL) and their configurations.
- **requirements.txt**: Lists the Python dependencies for the application.
- **streamlit_app.py**: The main Streamlit application.
- **populate_db.py**: Script to populate the PostgreSQL database with synthetic data.
- **README.md**: This file, providing setup and usage instructions.

## Contributing

Feel free to submit issues, fork the repository, and send pull requests. Contributions are welcome!

## License

This project is licensed under the MIT License.
