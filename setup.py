from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="agentmemory-openai",
    version="0.1.0",
    author="Devasish Banerjee",
    author_email="your_email@gmail.com",
    description="Persistent memory for OpenAI agents — store, recall, and forget.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bdeva1975/agentmemory",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
    install_requires=[
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.27.0",
    ],
)