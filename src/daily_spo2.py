import argparse
import logging.handlers
import requests
import configparser
import logging
import pandas as pd

import datetime

# python .\src\daily_spo2.py -configfile_path "C:\Workspace\python\oura_ring\get_data_from_ouraring\config\config.ini" -start_date 2024-08-01 -end_date 2024-08-10 -output_path "C:/Workspace/python/oura_ring/get_data_from_ouraring/output"

# args
parser = argparse.ArgumentParser(description='')
parser.add_argument('-configfile_path', help="C:\Workspace\python\oura_ring\get_data_from_ouraring\config\config.ini")
parser.add_argument('-start_date', help='yyyy-MM-dd')
parser.add_argument('-end_date', help='yyyy-MM-dd')
parser.add_argument('-output_path', help="C:/Workspace/python/oura_ring/get_data_from_ouraring/output")
args = parser.parse_args()

# config
config_ini = configparser.ConfigParser()
config_ini.read(args.configfile_path, encoding='utf-8')
print(config_ini)

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

logger.info("start daily_spo2")

URL = "https://api.ouraring.com/v2/usercollection/daily_spo2"
HEADER = {
    "Authorization": "Bearer " + config_ini["DEFAULT"]["TOKEN"]
}
params = {
    "start_date": args.start_date,
    "end_date": args.end_date,
    "next_token": ""
}

basic_data ={
    "id": [],
    "day": [],
    "average": [],
}

def main():
    status_code = 200
    next_token_flag = True
    loop_cnt = 0
    while(status_code == 200 and next_token_flag is True):
        res = requests.get(url = URL, headers = HEADER, params = params)

        status_code = res.status_code

        if(res.status_code == 200):
            data = res.json()["data"]
            print(res.json()["next_token"])
            if res.json()["next_token"] is None:
                next_token_flag = False
                params["next_token"] = ""
            else:
                next_token_flag = True
                params["next_token"] = res.json()["next_token"]
            print(loop_cnt, status_code, next_token_flag)

            # basic info
            for b_data in data:
                for key, value in b_data.items():
                    if(key in basic_data):
                        basic_data[key].append(value)
                    elif(key == "spo2_percentage"):
                        for cntr_k, cntr_v in b_data["spo2_percentage"].items():
                            if(cntr_k in basic_data):
                                basic_data[cntr_k].append(cntr_v)
            output_file_path = args.output_path + "/daily_spo2_" + args.start_date + "~" + args.end_date + ".csv"
            print(output_file_path)
            pd.DataFrame(data = basic_data).to_csv(output_file_path, encoding = "utf-8", index = False)
            loop_cnt+=1
        else:
            logger.error(f"status code {res.status_code}: {res.reason}")
            logger.info(f"configfile path:{args.configfile_path}")
            logger.info(f"start date:{args.start_date}")
            logger.info(f"end date:{args.end_date}")
            logger.info(f"output path:{args.output_path}")
            Exception(f"status code {res.status_code}: {res.reason}")

if __name__ == "__main__":
    main()