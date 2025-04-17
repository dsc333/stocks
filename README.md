# Tech stock data aggregator and dashboard

This repo consists of two Python files:

stock-agg.py: A data aggregator of tech stocks that uses Yahoo finance to retrieve stock data every minute for a week of trading (2100 data points for each stock).  Stock prices are stored in PyMongo collection "stocks".  Given the long execution time, it's best to run on VM (in the background.  

To run stock-agg.py (commands are in []:
* Clone the repo to your VM and go to the folder: [cd stocks]
* Create virtual environment and activate it: [python3 -m venv env] and then [source env/bin/activate]
* Pip install libraries in requirements.txt: [pip3 install -r requirements.txt]
* Go to PyMongo Network settings and add your VM's public IP address to the allow list.
* Replace the connection string with your connection string.
* Execute the program using the command:  [nohup python3 stock-agg.py &]
* nohup allows the program to continue running even after you disconnect from your VM.  The program will run for 5 weekdays.  If you want to stop it sooner you'll need to kill the process.  Type [ps ux] to get the list of processes, and then [kill -9 PID] where PID is the process ID associated with python.  
