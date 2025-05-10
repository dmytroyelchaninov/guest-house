echo "Removing all migration files (except __init__.py) and __pycache__ directories..."

# 1) Remove all Python migration files except __init__.py
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

# 2) Remove all Python migration compiled files
find . -path "*/migrations/*.pyc" -delete

# 3) Remove all __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} +

echo "All migration files and __pycache__ folders have been removed."