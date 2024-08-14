import argparse
import logging.handlers
import requests
import configparser
import logging
import pandas as pd

import datetime

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
params = {
    "start_date": args.start_date,
    "end_date": args.end_date,
    "next_token": ""
}

# class_5_min のデータ取得用
OURA_RING_INTERVAL = 5

basic_data ={
    "id": [],
    "score": [],
    "active_calories": [],
    "average_met_minutes": [],
    "meet_daily_targets": [],
    "move_every_hour": [],
    "recovery_time": [],
    "stay_active": [],
    "training_frequency": [],
    "training_volume": [],
    "equivalent_walking_distance": [],
    "high_activity_met_minutes": [],
    "high_activity_time": [],
    "inactivity_alerts": [],
    "low_activity_met_minutes": [],
    "low_activity_time": [],
    "medium_activity_met_minutes": [],
    "medium_activity_time": [],
    "meters_to_target": [],
    "non_wear_time": [],
    "resting_time": [],
    "sedentary_met_minutes": [],
    "sedentary_time": [],
    "steps": [],
    "target_calories": [],
    "target_meters": [],
    "total_calories": [],
    "day": [],
    "timestamp" : []
}

activity_per_5_min = {
    "id": [],
    "start_recording": [],
    "end_recording": [],
    "status_number": []
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
                    elif(key == "contributors"):
                        for cntr_k, cntr_v in b_data["contributors"].items():
                            if(cntr_k in basic_data):
                                basic_data[cntr_k].append(cntr_v)
            output_file_path = args.output_path + "/" + args.start_date + "~" + args.end_date + ".csv"
            print(output_file_path)
            pd.DataFrame(data = basic_data).to_csv(output_file_path, encoding = "utf-8", index = False)
            # activity_per_5_min
            for b_data in data:
                start_timestamp = datetime.datetime.strptime(b_data["day"], '%Y-%m-%d')
                end_timestamp = datetime.datetime.strptime(b_data["day"], '%Y-%m-%d') + datetime.timedelta(minutes = OURA_RING_INTERVAL)
                for status_number in b_data["class_5_min"]:
                    activity_per_5_min["id"].append(b_data["id"])
                    activity_per_5_min["start_recording"].append(start_timestamp)
                    activity_per_5_min["end_recording"].append(end_timestamp)
                    activity_per_5_min["status_number"].append(status_number)
                    start_timestamp = start_timestamp + datetime.timedelta(minutes = OURA_RING_INTERVAL)
                    end_timestamp = end_timestamp + datetime.timedelta(minutes = OURA_RING_INTERVAL)
            output_file_path = args.output_path + "/" + args.start_date + "~" + args.end_date + "_per5min.csv"
            pd.DataFrame(data = activity_per_5_min).to_csv(output_file_path, encoding = "utf-8", index = False)
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