# Notes for a developer using this code

Start docker daemon
Set env variable AWS_PROFILE
aws sso --profile dev
yawsso -p dev
make dev
make lint
make complex
make deploy


The tools:

1. yapf - It is a formatter for python files
2. pydantic - data validator 
3. AWS AppConfig, a feature of AWS Systems Manager, makes it easy for customers to quickly and safely configure, validate, and deploy feature flags and application configuration. Your feature flag and configurations data can be validated syntactically or semantically in the pre-deployment phase, and can be monitored and automatically rolled back if an alarm that you have configured is triggered. Using AWS AppConfig, you can make application changes safely, avoid errors in configuration changes, deploy changes across a set of targets quickly, and control deployment of changes across your applications.
4. mypy - static type checking (https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html#cheat-sheet-py3) 
5. mkdocs - MkDocs is a fast, simple and downright gorgeous static site generator that's geared towards building project documentation. Documentation source files are written in Markdown, and configured with a single YAML configuration file.
6. PyMdown Extensions is a collection of extensions for Python Markdown. They were originally written to make writing documentation more enjoyable. They cover a wide range of solutions, and while not every extension is needed by all people, there is usually at least one useful extension for everybody. (https://facelessuser.github.io/pymdown-extensions/)

pip install -U pydantic


1. LINT -  `make lint` - flake8 and mypy
2. COMPLEXITY SCANNING - `make complex` - xenon and radon
Xenon - a monitoring tool based on Radon. It monitors your code's complexity. Ideally, Xenon is run every time you commit code. Radon - a tool that computes various metrics from the Python source code.
3. 
