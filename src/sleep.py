import argparse
import logging.handlers
import requests
import configparser
import logging
import pandas as pd

import datetime

# python ./src/sleep.py -configfile_path "C:\Workspace\python\oura_ring\get_data_from_ouraring\config\config.ini" -start_date 2024-08-01 -end_date 2024-08-10 -output_path "C:/Workspace/python/oura_ring/get_data_from_ouraring/output"

# args
parser = argparse.ArgumentParser(description='')
parser.add_argument('-configfile_path', help="C:\Workspace\python\oura_ring\get_data_from_ouraring\config\config.ini")
parser.add_argument('-start_date', help='yyyy-MM-dd')
parser.add_argument('-end_date', help='yyyy-MM-dd')
parser.add_argument('-output_path', help="C:/Workspace/python/oura_ring/get_data_from_ouraring/output")
parser.add_argument('-timezone', required = False, default = "09:00", help="set timezone as 'HH:MM'format. default: '09:00'")
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

logger.info("start sleep")

URL = "https://api.ouraring.com/v2/usercollection/sleep"
HEADER = {
    "Authorization": "Bearer " + config_ini["DEFAULT"]["TOKEN"]
}
params = {
    "start_date": args.start_date,
    "end_date": args.end_date,
    "next_token": ""
}

# movement_30_sec のデータ取得用
MOVEMENT_INTERVAL = 30

# sleep_phase_5_min のデータ取得用
SLEEP_5_MIN_INTERVAL = 5

# タイムゾーンを表す文字列をAPIに合わせて指定しておく。
TIMEZONE = args.timezone

print(args.timezone)

basic_data ={
    "id": [],
    "average_breath": [],
    "average_heart_rate": [],
    "average_hrv": [],
    "awake_time": [],
    "bedtime_end": [],
    "bedtime_start": [],
    "day": [],
    "deep_sleep_duration": [],
    "efficiency": [],
    "latency": [],
    "light_sleep_duration": [],
    "low_battery_alert": [],
    "lowest_heart_rate": [],
    "period": [],
    "activity_balance": [],
    "body_temperature": [],
    "hrv_balance": [],
    "previous_day_activity": [],
    "previous_night": [],
    "recovery_index": [],
    "resting_heart_rate": [],
    "sleep_balance": [],
    "score": [],
    "temperature_deviation": [],
    "temperature_trend_deviation": [],
    "readiness_score_delta": [],
    "rem_sleep_duration": [],
    "restless_periods": [],
    "sleep_score_delta": [],
    "sleep_algorithm_version": [],
    "time_in_bed": [],
    "total_sleep_duration": [],
    "type": [],
}

heartrate_and_hrv = {
    "id": [],
    "interval": [],
    "start_recording": [],
    "end_recording": [],
    "heart_rate": [],
    "hrv": [],
}

movement_30_sec = {
    "id": [],
    "start_recording": [],
    "end_recording": [],
    "status_number": []
}

sleep_phase_5_min = {
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
                        if(key == "bedtime_start" or key == "bedtime_end"):
                            tmp_timestamp = datetime.datetime.strptime(b_data[key], '%Y-%m-%dT%H:%M:%S+' + TIMEZONE)
                            basic_data[key].append(tmp_timestamp)
                        else:
                            basic_data[key].append(value)
                    elif(key == "readiness"):
                        for r_key, r_v in b_data["readiness"].items():
                            if(r_key in basic_data):
                                basic_data[r_key].append(r_v)
                            elif(r_key == "contributors"):
                                for cntr_k, cntr_v in b_data["readiness"]["contributors"].items():
                                    if(cntr_k in basic_data):
                                        basic_data[cntr_k].append(cntr_v)
            output_file_path = args.output_path + "/sleep_" + args.start_date + "~" + args.end_date + ".csv"
            print(output_file_path)
            pd.DataFrame(data = basic_data).to_csv(output_file_path, encoding = "utf-8", index = False)

            # heartrate_and_hrv
            for b_data in data:
                interval_sec = b_data["heart_rate"]["interval"]
                start_timestamp = datetime.datetime.strptime(b_data["heart_rate"]["timestamp"], '%Y-%m-%dT%H:%M:%S.%f+' + TIMEZONE)
                end_timestamp = datetime.datetime.strptime(b_data["heart_rate"]["timestamp"], '%Y-%m-%dT%H:%M:%S.%f+' + TIMEZONE) + datetime.timedelta(seconds = interval_sec)
                for v_heart_rate, v_hrv in zip(b_data["heart_rate"]["items"], b_data["hrv"]["items"]):
                    heartrate_and_hrv["id"].append(b_data["id"])
                    heartrate_and_hrv["interval"].append(interval_sec)
                    heartrate_and_hrv["start_recording"].append(start_timestamp)
                    heartrate_and_hrv["end_recording"].append(end_timestamp)
                    heartrate_and_hrv["heart_rate"].append(v_heart_rate)
                    heartrate_and_hrv["hrv"].append(v_hrv)
                    start_timestamp = start_timestamp + datetime.timedelta(seconds = interval_sec)
                    end_timestamp = end_timestamp + datetime.timedelta(seconds = interval_sec)
            output_file_path = args.output_path + "/sleep_heartrate_and_hrv_" + args.start_date + "~" + args.end_date + ".csv"
            pd.DataFrame(data = heartrate_and_hrv).to_csv(output_file_path, encoding = "utf-8", index = False)

            # movement_30_sec
            for b_data in data:
                start_timestamp = datetime.datetime.strptime(b_data["bedtime_start"], '%Y-%m-%dT%H:%M:%S+' + TIMEZONE)
                end_timestamp = datetime.datetime.strptime(b_data["bedtime_start"], '%Y-%m-%dT%H:%M:%S+' + TIMEZONE) + datetime.timedelta(seconds = MOVEMENT_INTERVAL)
                for status_number in b_data["movement_30_sec"]:
                    movement_30_sec["id"].append(b_data["id"])
                    movement_30_sec["start_recording"].append(start_timestamp)
                    movement_30_sec["end_recording"].append(end_timestamp)
                    movement_30_sec["status_number"].append(status_number)
                    start_timestamp = start_timestamp + datetime.timedelta(seconds = MOVEMENT_INTERVAL)
                    end_timestamp = end_timestamp + datetime.timedelta(seconds = MOVEMENT_INTERVAL)
            output_file_path = args.output_path + "/sleep_movement30sec_" + args.start_date + "~" + args.end_date + ".csv"
            pd.DataFrame(data = movement_30_sec).to_csv(output_file_path, encoding = "utf-8", index = False)

            # sleep_phase_5_min
            for b_data in data:
                start_timestamp = datetime.datetime.strptime(b_data["bedtime_start"], '%Y-%m-%dT%H:%M:%S+' + TIMEZONE)
                end_timestamp = datetime.datetime.strptime(b_data["bedtime_start"], '%Y-%m-%dT%H:%M:%S+' + TIMEZONE) + datetime.timedelta(minutes = SLEEP_5_MIN_INTERVAL)
                for status_number in b_data["sleep_phase_5_min"]:
                    sleep_phase_5_min["id"].append(b_data["id"])
                    sleep_phase_5_min["start_recording"].append(start_timestamp)
                    sleep_phase_5_min["end_recording"].append(end_timestamp)
                    sleep_phase_5_min["status_number"].append(status_number)
                    start_timestamp = start_timestamp + datetime.timedelta(minutes = SLEEP_5_MIN_INTERVAL)
                    end_timestamp = end_timestamp + datetime.timedelta(minutes = SLEEP_5_MIN_INTERVAL)
            output_file_path = args.output_path + "/sleep_sleepphase5min_" + args.start_date + "~" + args.end_date + ".csv"
            pd.DataFrame(data = sleep_phase_5_min).to_csv(output_file_path, encoding = "utf-8", index = False)
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