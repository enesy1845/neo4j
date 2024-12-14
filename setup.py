# setup.py

from setuptools import setup, find_packages
import os

setup(
    name='quiznexusai',
    version='1.0.0',
    description='A comprehensive quiz and exam management system.',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'bcrypt>=3.1.7,<4.0.0',
        'python-dotenv>=0.15.0,<1.0.0',
        'pycryptodome>=3.9.0,<4.0.0',
        'PyJWT>=2.0.0,<3.0.0',  # PyJWT bağımlılığı
        'pytz>=2021.1,<2024.0',  # pytz bağımlılığı
        # Diğer runtime bağımlılıklar...
    ],
    extras_require={
        'dev': [
            'pytest>=6.2.0,<7.0.0',
            # Diğer geliştirme bağımlılıkları...
        ],
    },
    entry_points={
        'console_scripts': [
            'quiznexusai=quiznexusai.main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
