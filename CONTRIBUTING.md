# Contributing to SKYNET

Thank you for your interest in contributing to **SKYNET: AI-Powered Infrastructure Monitoring System**.

---

## 1. Code of Conduct
We are committed to providing a welcoming, inclusive, and professional environment. All participants are expected to uphold standards of mutual respect and constructive collaboration.

---

## 2. Development Workflow

### Branching Model
- `main`: Production-ready releases.
- `develop`: Primary integration branch for upcoming releases.
- `feature/<feature-name>`: Dedicated feature development.
- `bugfix/<issue-name>`: Targeted bug fixes.

### Contribution Steps
1. **Fork the repository** on GitHub.
2. **Clone your fork**:
   ```bash
   git clone https://github.com/<your-username>/skynet.git
   cd skynet
   ```
3. **Create a topic branch**:
   ```bash
   git checkout -b feature/hardware-metrics-enhancement
   ```
4. **Install development dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   pip install -r windows-agent/requirements.txt
   cd frontend && npm install && cd ..
   ```
5. **Run the automated test suite**:
   ```bash
   pytest tests/ -v
   pytest backend/tests/ -v
   ```
6. **Commit with descriptive messages** following Conventional Commits format (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
7. **Push to your fork** and submit a Pull Request against `develop`.

---

## 3. Pull Request Guidelines
- Ensure all automated unit and integration tests pass without failure.
- Ensure no hardcoded secrets, private keys, or credentials are introduced.
- Include corresponding unit/integration tests for any new API endpoint or agent collector feature.
- Maintain documentation parity in `docs/` and inline docstrings.
