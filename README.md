# Rainbox - syntax highlighter service

Rainbox is a syntax highlighting service that provides a simple API for converting code snippets into formatted HTML with syntax highlighting.

## Features

- RESTful API for syntax highlighting
- Support for multiple programming languages
- Various syntax highlighting themes to choose from
- User authentication with OAuth2

## Quick start

### Using Docker

1. Clone the repository
2. Run with Docker Compose:
   ```bash
   docker compose up
   ```
3. Access the API at http://localhost:8000

### Manual setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API usage

### Authentication

1. Register a new user:
   ```bash
   curl -X POST http://localhost:8000/register \
     -H "Content-Type: application/json" \
     -d '{"username":"your_username", "password":"your_password", "email":"your@email.com"}'
   ```

2. Get an access token:
   ```bash
   curl -X POST http://localhost:8000/token \
     -d "username=your_username&password=your_password" \
     -H "Content-Type: application/x-www-form-urlencoded"
   ```

### Highlighting code

```bash
curl -X POST http://localhost:8000/highlight \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello, World!\")",
    "language": "python",
    "theme": "monokai"
  }'
```

## Available themes

Rainbox uses Pygments for syntax highlighting and supports all Pygments themes, including:
- default
- monokai
- friendly
- colorful
- autumn
- murphy
- manni
- material
- perldoc
- pastie
- borland
- trac
- native
- fruity
- bw
- vim
- vs
- tango
- rrt
- xcode
- igor
- paraiso-light
- paraiso-dark
- lovelace
- algol
- algol_nu
- arduino
- rainbow_dash
- abap
- solarized-dark
- solarized-light

## Development

### Running tests

```bash
pytest
```

### Documentation

The API documentation is available at http://localhost:8000/docs when running the server.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
