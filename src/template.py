import argparse
import logging.handlers
import requests
import configparser
import logging

# python .\daily_activity.py -configfile_path "C:/Workspace/python/oura_ring/config/config.ini" -start_date 2024-08-01 -end_date 2024-08-10 -output_path "C:/Workspace/python/oura_ring/output"

# args
parser = argparse.ArgumentParser(description='')
parser.add_argument('-configfile_path', help="C:/Workspace/python/oura_ring/config/config.ini")
parser.add_argument('-start_date', help='yyyy-MM-dd')
parser.add_argument('-end_date', help='yyyy-MM-dd')
parser.add_argument('-output_path', help="C:/Workspace/python/oura_ring/output")
args = parser.parse_args()

# config
config_ini = configparser.ConfigParser()
config_ini.read(args.configfile_path, encoding='utf-8')

# logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

format = "%(levelname)-9s  %(asctime)s [%(filename)s:%(lineno)d] %(message)s"

st_handler = logging.StreamHandler()
st_handler.setLevel(logging.DEBUG)
st_handler.setFormatter(logging.Formatter(format))

fl_handler = logging.handlers.TimedRotatingFileHandler(filename= config_ini["LOG"]["PATH"] + "/" + config_ini["LOG"]["FILENAME"] + ".log", encoding="utf-8", when = "MIDNIGHT")
fl_handler.setLevel(logging.DEBUG)
fl_handler.setFormatter(logging.Formatter(format))

logger.addHandler(st_handler)
logger.addHandler(fl_handler)

logger.info("start daily_activity")

URL = "https://api.ouraring.com/v2/usercollection/daily_activity"
HEADER = {
    "Authorization": "Bearer " + config_ini["DEFAULT"]["TOKEN"]
}
PARAMS = {
    "start_date": args.start_date,
    "end_date": args.end_date
}

def main():
    start_date = args.start_date
    end_date = args.end_date

    res = requests.get(url = URL, headers = HEADER, params = PARAMS)
    print(res.status_code)
    print(res.text)

if __name__ == "__main__":
    main()