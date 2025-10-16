## Create a venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    flag_created_venv=true
fi

## Activate the venv
## If this is a git bash shell on Windows, use source venv/Scripts/activate
## Otherwise, use source venv/bin/activate
if [[ "$OSTYPE" == "msys" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

if [ "$flag_created_venv" = true ]; then
    echo "Virtual environment created and activated."
    echo "Installing required packages..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "Virtual environment activated."
fi

## get args from command line
if [ ${#@} -ne "4" ]; then
    echo " "
    echo "No service specified. Usage: ./fetch_simulation_data.sh <ticker> <timeframe>  <initial_date> <end_date>"
    echo " "
    echo "For CLI, provide the following arguments:"
    echo "  Ticker: The stock ticker symbol (e.g., AAPL)"
    echo "  Timeframe: The time interval for the data (e.g., D1)"
    echo "  Initial Date: The start date for the data (YYYY-MM-DD)"
    echo "  End Date: The end date for the data (YYYY-MM-DD)"
    exit 1
fi

echo "Fetching Data..."
python3 market_data.py $1 $2 $3 $4