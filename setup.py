from setuptools import setup, find_packages

setup(
    name="solana_memecoin_bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "PyQt6"
    ],
    entry_points={
        "console_scripts": [
            "memecoin-bot=script:main",  # Change "script" to your actual script name
        ]
    },
    author="Your Name",
    description="A Solana Memecoin Trading Bot using DEX Screener & CoinGecko",
    url="https://github.com/yourusername/solana-memecoin-bot",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
