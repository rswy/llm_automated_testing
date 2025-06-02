Conda Packing and Distribution Plan
This plan details how to package your LLM evaluation tool using Conda, making it easy for end-users to install and run.

A. Core Principles
Self-Contained: The distributed package should contain everything needed to run the application (Python, dependencies, models, scripts).

Automated Setup: Minimize manual steps for the end-user. A single script should handle environment creation and application launch.

Reproducible: Ensure the environment is identical across different user machines.

Version Control: Clearly define dependency versions.

B. Project Structure for Distribution
Ensure your project directory is organized as follows before zipping:

llm_eval_tool_dist/         # This is the folder you will zip and distribute
├── streamlit_app.py        # Main Streamlit GUI entry point
├── main.py                 # New CLI entry point
├── environment.yml         # Conda environment definition
├── run_app.bat             # Windows batch file to install/run GUI
├── run_app.sh              # (Optional) Linux/macOS shell script to install/run GUI
├── run_cli.bat             # (Optional) Windows batch file to install/run CLI
├── run_cli.sh              # (Optional) Linux/macOS shell script to install/run CLI
├── llm_eval_package/       # Your modularized Python package
│   ├── __init__.py
│   ├── config.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   └── generator.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   └── reporting.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── data_view.py
│   │   ├── results_view.py
│   │   ├── sidebar_view.py
│   │   └── tutorial_view.py
│   ├── metrics/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── completeness.py
│   │   ├── conciseness.py
│   │   ├── fluency_similarity.py
│   │   ├── safety.py
│   │   └── trust_factuality.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── registry.py
│   └── utils.py
├── data/                   # Directory for mock data / example data
│   └── llm_eval_mock_data_generated.csv
│   └── ...
└── models/                 # Crucial: Contains your Sentence-BERT model
    └── all-MiniLM-L6-v2/
        ├── config.json
        ├── pytorch_model.bin
        ├── tokenizer.json
        └── ... (all other model files)

C. Finalizing environment.yml
Ensure your environment.yml is clean and comprehensive. It should list all direct and indirect dependencies.

name: llm_eval_env
channels:
  - defaults
  - conda-forge # Recommend conda-forge for broader package availability
dependencies:
  - python=3.9 # Or your exact Python version used for development
  - pip
  - pandas
  - numpy
  - streamlit
  - tqdm
  - scikit-learn # Commonly used in NLP, good to include if any metric relies on it
  - sentence-transformers # Often best installed via pip, but sometimes available on conda-forge
  - pip:
    # Add any other packages that are *only* available via pip here
    # - some-pip-only-package==1.0.0

To generate this: Run conda env export --no-builds > environment.yml in your active development environment, then manually clean up the output to remove unnecessary version specifics (like build hashes) and ensure it's concise.

D. Automation Scripts for End-Users
These scripts will be placed in the root directory (llm_eval_tool_dist/).

D1. run_app.bat (for Windows - GUI Version)
This script will install/update the Conda environment and launch the Streamlit GUI.

@echo off
setlocal

REM --- Configuration ---
set ENV_NAME=llm_eval_env
set STREAMLIT_SCRIPT=streamlit_app.py
set CONDA_INSTALLER_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
set MINICONDA_PATH=%USERPROFILE%\Miniconda3

REM --- Check for Conda Installation ---
echo Checking for Conda installation...
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo Conda not found. Attempting to install Miniconda...
    echo.
    echo Please follow the Miniconda installer prompts.
    echo IMPORTANT: During installation, select "Install for me only" and
    echo "Add Miniconda3 to my PATH environment variable" (or ensure it's added manually later).
    echo.
    powershell -Command "Invoke-WebRequest -Uri '%CONDA_INSTALLER_URL%' -OutFile 'Miniconda3-latest-Windows-x86_64.exe'"
    start /wait Miniconda3-latest-Windows-x86_64.exe /S /D=%MINICONDA_PATH%
    del Miniconda3-latest-Windows-x86_64.exe
    
    REM Re-check if conda is in PATH after installation
    where conda >nul 2>nul
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Miniconda installation failed or was not added to PATH.
        echo Please ensure Conda is installed and its 'Scripts' directory is in your system's PATH.
        echo You might need to restart your command prompt or computer.
        pause
        exit /b 1
    )
    echo Conda installed successfully.
) else (
    echo Conda found.
)

REM --- Initialize Conda (important for fresh installs or specific environments) ---
call conda init cmd.exe >nul 2>nul

REM --- Activate Base Environment (ensure conda commands are available) ---
call conda activate base >nul 2>nul

REM --- Create/Update Conda Environment ---
echo.
echo Creating/Updating Conda environment '%ENV_NAME%' from environment.yml...
conda env create -f environment.yml -n %ENV_NAME% || conda env update -f environment.yml -n %ENV_NAME%
if %errorlevel% neq 0 (
    echo ERROR: Failed to create or update Conda environment.
    echo Please check the error messages above.
    pause
    exit /b 1
)
echo Conda environment '%ENV_NAME%' is ready.

REM --- Activate the specific environment and run the Streamlit app ---
echo.
echo Activating environment and starting Streamlit app...
call conda activate %ENV_NAME%
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate Conda environment '%ENV_NAME%'.
    pause
    exit /b 1
)

REM Navigate to the directory where streamlit_app.py is located (same as this batch file)
cd /d "%~dp0"

streamlit run %STREAMLIT_SCRIPT% --server.port 8501 --server.enableCORS false --server.enableXsrfProtection false

echo.
echo Application finished or closed.
pause
endlocal

D2. run_cli.bat (for Windows - CLI Version)
This script will install/update the Conda environment and provide instructions on how to use the CLI.

@echo off
setlocal

REM --- Configuration ---
set ENV_NAME=llm_eval_env
set CLI_SCRIPT=main.py
set CONDA_INSTALLER_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
set MINICONDA_PATH=%USERPROFILE%\Miniconda3

REM --- Check for Conda Installation (same as run_app.bat) ---
echo Checking for Conda installation...
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo Conda not found. Attempting to install Miniconda...
    echo.
    echo Please follow the Miniconda installer prompts.
    echo IMPORTANT: During installation, select "Install for me only" and
    echo "Add Miniconda3 to my PATH environment variable" (or ensure it's added manually later).
    echo.
    powershell -Command "Invoke-WebRequest -Uri '%CONDA_INSTALLER_URL%' -OutFile 'Miniconda3-latest-Windows-x86_64.exe'"
    start /wait Miniconda3-latest-Windows-x86_64.exe /S /D=%MINICONDA_PATH%
    del Miniconda3-latest-Windows-x86_64.exe
    
    where conda >nul 2>nul
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Miniconda installation failed or was not added to PATH.
        pause
        exit /b 1
    )
    echo Conda installed successfully.
) else (
    echo Conda found.
)

REM --- Initialize Conda ---
call conda init cmd.exe >nul 2>nul

REM --- Activate Base Environment ---
call conda activate base >nul 2>nul

REM --- Create/Update Conda Environment ---
echo.
echo Creating/Updating Conda environment '%ENV_NAME%' from environment.yml...
conda env create -f environment.yml -n %ENV_NAME% || conda env update -f environment.yml -n %ENV_NAME%
if %errorlevel% neq 0 (
    echo ERROR: Failed to create or update Conda environment.
    echo Please check the error messages above.
    pause
    exit /b 1
)
echo Conda environment '%ENV_NAME%' is ready.

REM --- Provide instructions for using the CLI ---
echo.
echo Conda environment '%ENV_NAME%' is set up.
echo To run the LLM Evaluation CLI, open a new command prompt, activate the environment,
echo and then run the '%CLI_SCRIPT%' script with your desired arguments.
echo.
echo Example usage:
echo   conda activate %ENV_NAME%
echo   python %CLI_SCRIPT% --input_file data\your_data.csv --output_file results.csv --metrics "Semantic Similarity"
echo.
echo For more options, run:
echo   conda activate %ENV_NAME%
echo   python %CLI_SCRIPT% --help
echo.
pause
endlocal

D3. run_app.sh (for Linux/macOS - GUI Version - Optional)
For Linux/macOS users, a shell script would be similar. Users would need to have Conda/Miniconda installed.

#!/bin/bash

ENV_NAME="llm_eval_env"
STREAMLIT_SCRIPT="streamlit_app.py"

echo "Checking for Conda installation..."
if ! command -v conda &> /dev/null
then
    echo "Conda not found. Please install Miniconda or Anaconda first."
    echo "Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "Activating base Conda environment..."
# Source conda.sh to ensure 'conda' command is available in new shell sessions
# This is crucial for non-interactive scripts or if conda init hasn't been run
eval "$(conda shell.bash hook)"
conda activate base

echo "Creating/Updating Conda environment '$ENV_NAME' from environment.yml..."
conda env create -f environment.yml -n "$ENV_NAME" || conda env update -f environment.yml -n "$ENV_NAME"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create or update Conda environment."
    exit 1
fi
echo "Conda environment '$ENV_NAME' is ready."

echo "Activating environment and starting Streamlit app..."
conda activate "$ENV_NAME"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate Conda environment '$ENV_NAME'."
    exit 1
fi

# Navigate to the directory where streamlit_app.py is located
# This assumes the script is in the root of your project
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
cd "$SCRIPT_DIR"

streamlit run "$STREAMLIT_SCRIPT" --server.port 8501 --server.enableCORS false --server.enableXsrfProtection false

echo "Application finished or closed."
read -p "Press Enter to continue..."

D4. run_cli.sh (for Linux/macOS - CLI Version - Optional)
#!/bin/bash

ENV_NAME="llm_eval_env"
CLI_SCRIPT="main.py"

echo "Checking for Conda installation..."
if ! command -v conda &> /dev/null
then
    echo "Conda not found. Please install Miniconda or Anaconda first."
    echo "Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "Activating base Conda environment..."
eval "$(conda shell.bash hook)"
conda activate base

echo "Creating/Updating Conda environment '$ENV_NAME' from environment.yml..."
conda env create -f environment.yml -n "$ENV_NAME" || conda env update -f environment.yml -n "$ENV_NAME"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create or update Conda environment."
    exit 1
fi
echo "Conda environment '$ENV_NAME' is ready."

echo ""
echo "Conda environment '$ENV_NAME' is set up."
echo "To run the LLM Evaluation CLI, open a new terminal, activate the environment,"
echo "and then run the '$CLI_SCRIPT' script with your desired arguments."
echo ""
echo "Example usage:"
echo "  conda activate $ENV_NAME"
echo "  python $CLI_SCRIPT --input_file data/your_data.csv --output_file results.csv --metrics \"Semantic Similarity\""
echo ""
echo "For more options, run:"
echo "  conda activate $ENV_NAME"
echo "  python $CLI_SCRIPT --help"
echo ""
read -p "Press Enter to continue..."

E. Distribution Process
Prepare the Directory: Create a new directory (e.g., llm_eval_tool_dist).

Copy Files: Copy all necessary files and folders into llm_eval_tool_dist/:

streamlit_app.py

main.py

environment.yml

run_app.bat

run_cli.bat (and .sh versions if providing for Linux/macOS)

The entire llm_eval_package/ directory (with all its subfolders and __init__.py files).

The data/ directory (with any example/mock data).

The models/ directory (crucially, the all-MiniLM-L6-v2 folder and its contents).

Zip the Directory: Compress the llm_eval_tool_dist folder into a .zip file (e.g., LLMEvalTool.zip).

Provide Instructions: Give your end-users simple instructions:

"Download and unzip LLMEvalTool.zip."

"Navigate into the unzipped folder."

"To run the graphical interface, double-click run_app.bat (Windows) or execute bash run_app.sh (Linux/macOS) in a terminal."

"To use the command-line interface, double-click run_cli.bat (Windows) or execute bash run_cli.sh (Linux/macOS) and follow the instructions in the console."

"The first time you run it, it might take several minutes to set up the environment and download models. Please be patient."

This comprehensive approach will provide a robust and user-friendly deployment for your LLM evaluation tool.