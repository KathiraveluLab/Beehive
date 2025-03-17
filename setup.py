from setuptools import setup, find_packages

setup(
    name="beehive",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "pymongo",
        "python-dotenv",
        "authlib",
        "google-auth-oauthlib",
    ],
    python_requires=">=3.8",
) 