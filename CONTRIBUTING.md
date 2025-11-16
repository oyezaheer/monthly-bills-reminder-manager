# Contributing to Monthly Bills + Reminder Manager

Thank you for your interest in contributing to this project! 🎉

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Basic knowledge of Python, NumPy, and Streamlit

### Setup Development Environment

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/monthly-bills-reminder-manager.git
   cd monthly-bills-reminder-manager
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up demo data**:
   ```bash
   python setup_demo.py
   ```

5. **Run the application**:
   ```bash
   python -m streamlit run app.py
   ```

## 🛠️ Development Guidelines

### Code Style
- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Add docstrings for classes and functions
- Keep functions small and focused

### Architecture
- **Models**: Database models and business logic (`models/`)
- **Views**: Streamlit UI components (`views/`)
- **Utils**: Helper functions and utilities (`utils/`)

### Key Patterns Used
- **OOP**: Classes for Bill, ReminderEngine, PaymentHistory
- **Generator**: Efficient reminder production
- **Decorator**: Automatic payment logging
- **MVT**: Model-View-Template separation

## 📝 How to Contribute

### 1. Bug Reports
- Use GitHub Issues
- Include steps to reproduce
- Provide error messages and screenshots
- Specify your environment (OS, Python version)

### 2. Feature Requests
- Use GitHub Issues with "enhancement" label
- Describe the feature clearly
- Explain the use case and benefits
- Consider backward compatibility

### 3. Code Contributions

#### Pull Request Process
1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write clean, documented code
   - Follow existing patterns
   - Add tests if applicable

3. **Test your changes**:
   ```bash
   python setup_demo.py  # Reset demo data
   python -m streamlit run app.py  # Test UI
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

5. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

#### Commit Message Format
- **Add**: New features
- **Fix**: Bug fixes
- **Update**: Improvements to existing features
- **Refactor**: Code restructuring
- **Docs**: Documentation updates

### 4. Areas for Contribution

#### 🔥 High Priority
- Email/SMS notification integration
- Recurring bill automation
- Data export/import features
- Mobile responsiveness improvements

#### 🌟 Medium Priority
- Additional payment methods
- Budget planning features
- Advanced analytics
- Multi-currency support

#### 💡 Nice to Have
- Dark mode theme
- Custom reminder templates
- Integration with banking APIs
- Multi-user support

## 🧪 Testing

### Manual Testing Checklist
- [ ] Add new bills with different categories
- [ ] Record payments with various methods
- [ ] Check reminder generation
- [ ] Verify NumPy scoring calculations
- [ ] Test dashboard analytics
- [ ] Validate data persistence

### Code Quality
- Ensure no Python syntax errors
- Check for proper error handling
- Verify database operations work correctly
- Test with different data scenarios

## 📚 Resources

### Documentation
- [Streamlit Documentation](https://docs.streamlit.io/)
- [NumPy Documentation](https://numpy.org/doc/)
- [SQLite Documentation](https://docs.python.org/3/library/sqlite3.html)

### Project Structure
```
jiya/
├── models/           # Data models and business logic
├── views/            # Streamlit UI components
├── utils/            # Helper functions
├── app.py           # Main application
└── setup_demo.py   # Demo data generator
```

## 🤝 Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Share knowledge and best practices
- Provide constructive feedback
- Follow the code of conduct

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Code Review**: For feedback on contributions

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Special thanks for major features

Thank you for making this project better! 🚀
