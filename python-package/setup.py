from pathlib import Path
from setuptools import setup, find_packages

cwd = Path(__file__).resolve().parent
requirements = (cwd / 'employee_events' / 'requirements.txt').read_text().split('\n')

setup_args = dict(
    name='employee_events',
    version='0.0',
    description='SQL Query API for the employee_events database',
    packages=find_packages(),
    package_data={'': ['employee_events.db', 'requirements.txt']},
    install_requires=[r for r in requirements if r.strip()],
    )

if __name__ == "__main__":
    setup(**setup_args)
