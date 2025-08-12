# ThreatForge - AI-Enhanced Security Attack Simulation Platform

A comprehensive SaaS platform for running security attack simulations using various open-source security tools, enhanced with AI-powered analysis and reporting. Built with FastAPI, SQLAlchemy, Celery, and LangChain.

## 🚀 **New in Version 2.0: AI Orchestration Layer**

### ✨ **AI-Powered Features:**

- **🤖 Intelligent Vulnerability Analysis**: Uses LangChain + Groq API for advanced security assessment
- **📊 AI-Generated Risk Scoring**: Dynamic risk calculation (1-100) with confidence metrics
- **🛡️ Automated Mitigation Recommendations**: Actionable security improvements with implementation steps
- **💰 Cost-Optimized Processing**: Keeps costs under $0.01 per job using efficient models
- **🔄 Smart Fallback System**: Rule-based analysis when AI services are unavailable
- **📈 Enhanced PDF Reports**: Comprehensive AI-enhanced security documentation

### 🔧 **AI Configuration:**

```bash
# Set your Groq API key for AI analysis
GROQ_API_KEY=your-groq-api-key-here

# Configure AI model preferences
AI_MODEL_PROVIDER=groq  # groq, openai, or local
AI_MODEL_NAME=llama3-8b-8192  # Fast and cost-effective
AI_COST_LIMIT_PER_JOB=0.01  # Maximum $0.01 per analysis
AI_FALLBACK_ENABLED=true  # Always available
```

## Features

- **User Authentication**: JWT-based authentication with refresh tokens
- **Attack Simulation Jobs**: Create and manage security simulation jobs
- **Multiple Security Tools**: Support for Metasploit, OpenVAS, Caldera, Nmap, SQLMap
- **Docker Integration**: Run security tools in isolated containers
- **AI-Enhanced Analysis**: Intelligent vulnerability assessment and risk scoring
- **Smart Mitigation**: Automated security recommendations with implementation steps
- **Enhanced PDF Reports**: Comprehensive AI-powered security documentation
- **Async Processing**: Background job processing with Celery and Redis
- **Configurable Tools**: Add new security tools without code changes
- **Cost Optimization**: AI analysis within strict budget constraints

## Architecture

- **Backend**: FastAPI with async support
- **Database**: SQLAlchemy ORM with PostgreSQL/SQLite support
- **Authentication**: JWT tokens with passlib password hashing
- **Job Queue**: Celery with Redis backend
- **Security Tools**: Docker-based execution
- **AI Layer**: LangChain + Groq API with intelligent fallbacks
- **Reports**: Enhanced PDF generation with AI insights
- **Storage**: Local file system with S3 support

## Prerequisites

- Python 3.8+
- Docker
- Redis (for Celery)
- PostgreSQL (optional, SQLite by default)
- Groq API key (for AI features)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ThreatForge
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp env.example .env
   # Edit .env with your configuration, especially AI settings
   ```

5. **Database setup**
   ```bash
   # Initialize Alembic
   alembic init alembic
   
   # Create initial migration
   alembic revision --autogenerate -m "Initial migration"
   
   # Apply migration
   alembic upgrade head
   ```

6. **Start Redis** (for Celery)
   ```bash
   # On Windows, use WSL or Docker
   docker run -d -p 6379:6379 redis:alpine
   
   # On Linux/Mac
   redis-server
   ```

## Running the Application

### Development Mode

1. **Start the FastAPI server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Celery worker** (in another terminal)
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

3. **Start Celery beat** (optional, for scheduled tasks)
   ```bash
   celery -A app.celery_app beat --loglevel=info
   ```

### Production Mode

1. **Using Gunicorn**
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

2. **Using Docker Compose**
   ```bash
   docker-compose up -d
   ```

## API Documentation

Once the server is running, you can access:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **AI Health Check**: http://localhost:8000/api/v1/ai/health

## API Endpoints

### Authentication (`/api/v1/auth`)

- `POST /register` - User registration
- `POST /login` - User login
- `POST /refresh` - Refresh access token
- `GET /me` - Get current user info

### Jobs (`/api/v1/jobs`)

- `POST /` - Create new simulation job
- `GET /` - List user's jobs
- `GET /{job_id}` - Get specific job details
- `DELETE /{job_id}` - Delete job
- `PUT /{job_id}/status` - Update job status

### AI Analysis (`/api/v1/ai`) 🆕

- `GET /models` - Get available AI models
- `POST /analyze/{job_id}` - Request AI analysis for a job
- `GET /status/{job_id}` - Check AI analysis status
- `GET /costs` - Get AI analysis cost summary
- `POST /batch-analyze` - Request batch AI analysis
- `GET /health` - Check AI service health

## AI Orchestration Features

### 🤖 **Intelligent Analysis Pipeline**

1. **Simulation Execution**: Run security tools in Docker containers
2. **AI Processing**: Analyze results using LangChain + Groq
3. **Vulnerability Assessment**: Identify and classify security issues
4. **Risk Scoring**: Calculate dynamic risk scores (1-100)
5. **Mitigation Generation**: Create actionable security recommendations
6. **Enhanced Reporting**: Generate comprehensive PDF reports

### 💰 **Cost Optimization**

- **Per-Job Limit**: Maximum $0.01 per analysis
- **Model Selection**: Uses cost-effective Groq models
- **Batch Processing**: Optimize costs for multiple jobs
- **Fallback System**: Rule-based analysis when AI unavailable

### 🛡️ **Security Intelligence**

- **CVSS Scoring**: Industry-standard vulnerability ratings
- **Attack Vector Analysis**: Identify potential exploitation paths
- **Impact Assessment**: Evaluate business risk implications
- **Implementation Guidance**: Step-by-step remediation steps

## Security Tools Configuration

The platform supports configurable security tools through the `tools_config.json` file in the `security_tools` directory.

### Example Configuration

```json
{
  "metasploit": {
    "image": "rapid7/metasploit-framework:latest",
    "command": ["msfconsole", "-q", "-x"],
    "environment": {},
    "volumes": {},
    "timeout": 1800
  },
  "openvas": {
    "image": "immauss/openvas:latest",
    "command": ["gvm-start"],
    "environment": {},
    "volumes": {},
    "timeout": 3600
  }
}
```

### Adding New Tools

1. Create a Docker image for your tool
2. Add configuration to `tools_config.json`
3. Implement tool-specific parameter preparation in `SecurityToolRunner`
4. Add output parsing logic

## Database Models

### Users
- `id`: Primary key
- `email`: Unique email address
- `hashed_password`: Bcrypt hashed password
- `created_at`: Account creation timestamp

### Attack Simulation Jobs
- `id`: Primary key
- `user_id`: Foreign key to users
- `target_system_description`: Target system details
- `simulation_tool`: Selected security tool
- `severity_level`: Simulation severity
- `number_of_attack_vectors`: Number of attack vectors
- `status`: Job status (pending, running, completed, failed)
- `created_at`, `started_at`, `completed_at`: Timestamps

### Simulation Results
- `id`: Primary key
- `job_id`: Foreign key to jobs
- `tool_output`: Raw tool output
- `vulnerabilities_found`: JSON array of vulnerabilities
- `risk_score`: AI-calculated risk score (0-100)
- `pdf_report_url`: URL to generated PDF report

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./threatforge.db` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-here` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `TOOLS_DIRECTORY` | Security tools config directory | `./security_tools` |
| `AWS_ACCESS_KEY_ID` | AWS S3 access key | None |
| `AWS_SECRET_ACCESS_KEY` | AWS S3 secret key | None |
| `S3_BUCKET_NAME` | S3 bucket for reports | `threatforge-reports` |
| `GROQ_API_KEY` | Groq API key for AI analysis | None |
| `AI_MODEL_PROVIDER` | AI service provider | `groq` |
| `AI_COST_LIMIT_PER_JOB` | Maximum cost per job | `0.01` |
| `AI_FALLBACK_ENABLED` | Enable fallback analysis | `true` |

## Development

### Code Structure

```
ThreatForge/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication utilities
│   ├── celery_app.py        # Celery configuration
│   ├── tasks.py             # Background tasks with AI
│   ├── security_tools.py    # Security tool runner
│   ├── report_generator.py  # PDF report generator
│   ├── enhanced_report_generator.py  # AI-enhanced reports
│   ├── ai_service.py        # AI orchestration service
│   ├── storage.py           # File storage manager
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Authentication endpoints
│       ├── jobs.py          # Job management endpoints
│       └── ai.py            # AI analysis endpoints
├── alembic/                 # Database migrations
├── security_tools/          # Security tools configuration
├── storage/                 # Local file storage
├── requirements.txt         # Python dependencies
├── alembic.ini             # Alembic configuration
└── README.md               # This file
```

### Running Tests

```bash
# Test basic setup
python test_setup.py

# Test AI functionality
python test_ai_setup.py

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Formatting

```bash
# Install formatting tools
pip install black isort

# Format code
black app/
isort app/
```

## AI Testing and Validation

### Test AI Setup

```bash
# Verify AI orchestration layer
python test_ai_setup.py
```

### AI Cost Monitoring

```bash
# Check AI analysis costs
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/v1/ai/costs
```

### AI Service Health

```bash
# Check AI service status
curl http://localhost:8000/api/v1/ai/health
```

## Deployment

### Docker Deployment

1. **Build the image**
   ```bash
   docker build -t threatforge .
   ```

2. **Run the container**
   ```bash
   docker run -d -p 8000:8000 \
     -e DATABASE_URL=postgresql://user:pass@host/db \
     -e REDIS_URL=redis://redis-host:6379 \
     -e GROQ_API_KEY=your-groq-key \
     threatforge
   ```

### Production Considerations

- Use environment variables for sensitive configuration
- Set up proper logging and monitoring
- Configure CORS appropriately for production
- Use HTTPS in production
- Set up database connection pooling
- Configure Redis persistence
- Set up backup strategies for database and files
- Monitor AI API costs and usage
- Configure AI fallback systems

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs for debugging information
- Test AI functionality with `test_ai_setup.py`

## Security

- All passwords are hashed using bcrypt
- JWT tokens are used for authentication
- CORS is configured for security
- Input validation using Pydantic schemas
- SQL injection protection through SQLAlchemy ORM
- AI API keys are securely managed
- Cost limits prevent excessive AI usage

## Roadmap

- [x] AI orchestration layer with LangChain + Groq
- [x] Intelligent vulnerability analysis
- [x] Automated mitigation recommendations
- [x] Cost-optimized AI processing
- [x] Enhanced PDF reporting
- [ ] WebSocket support for real-time AI updates
- [ ] Additional AI model providers
- [ ] Advanced AI analytics and insights
- [ ] Multi-tenant AI cost management
- [ ] AI-powered threat intelligence
- [ ] Integration with SIEM systems
- [ ] Machine learning model training 