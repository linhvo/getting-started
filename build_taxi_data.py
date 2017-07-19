import json
import os
import sys
import csv
import datetime
import requests
import math
TIME_FORMAT = "%Y-%m-%dT%H:%S"


class TaxiData:
    xmin = -74.27
    xmax = -73.69
    xres = 100
    ymin = 40.48
    ymax = 40.93
    yres = 100
    definition = {}
    definition["frames"] = [
        {
            "name": "cab_type"
        },
        {
            "name": "dist_miles"
        },
        {
            "name": "drop_day",
        },
        {
            "name": "drop_grid_id"
        },
        {
            "name": "drop_month"
        },
        {
            "name": "drop_time"
        },
        {
            "name": "drop_year"
        },
        {
            "name": "duration_minutes"
        },
        {
            "name": "passenger_count"
        },
        {
            "name": "pickup_day"
        },
        {
            "name": "pickup_grid_id"
        },
        {
            "name": "pickup_month"
        },
        {
            "name": "pickup_time"
        },
        {
            "name": "pickup_year"
        },
        {
            "name": "speed_mph"
        },
        {
            "name": "total_amount_dollars"
        }
    ]

    def build(self, path, lines=None):

        bits_string = []
        fields = []
        try:
            with open(path) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    field = {}
                    pickup = datetime.datetime.strptime(row["Trip_Pickup_DateTime"], '%Y-%m-%d %H:%M:%S')
                    field["id"] = reader.line_num

                    setbits = []
                    field["pickup_year"] = pickup.year
                    setbits.append(self.get_setbit_string("pickup_year", pickup.year, reader.line_num))

                    field["pickup_month"] = pickup.month
                    setbits.append(self.get_setbit_string("pickup_month", pickup.month, reader.line_num))

                    field["pickup_day"] = pickup.day
                    setbits.append(self.get_setbit_string("pickup_day", pickup.day, reader.line_num))

                    field["pickup_time"] = self.get_time(pickup)
                    setbits.append(self.get_setbit_string("pickup_time", field["pickup_time"], reader.line_num))

                    drop = datetime.datetime.strptime(row["Trip_Dropoff_DateTime"], '%Y-%m-%d %H:%M:%S')
                    field["drop_year"] = drop.year
                    setbits.append(self.get_setbit_string("drop_year", drop.year, reader.line_num))

                    field["drop_month"] = drop.month
                    setbits.append(self.get_setbit_string("drop_month", drop.month, reader.line_num))

                    field["drop_day"] = drop.day
                    setbits.append(self.get_setbit_string("drop_day", drop.day, reader.line_num))

                    field["drop_time"] = self.get_time(drop)
                    setbits.append(self.get_setbit_string("drop_time", field["drop_time"], reader.line_num))

                    field["dist_miles"] = int(round(float(row["Trip_Distance"])))
                    setbits.append(self.get_setbit_string("dist_miles", field["dist_miles"], reader.line_num))

                    field["total_amount_dollars"] = int(round(float(row["Total_Amt"])))
                    setbits.append(self.get_setbit_string("total_amount_dollars", field["total_amount_dollars"], reader.line_num))

                    field["passenger_count"] = int(row["Passenger_Count"])
                    setbits.append(self.get_setbit_string("passenger_count", field["passenger_count"], reader.line_num))

                    field["pickup_grid_id"] = self.get_grid_id(float(row["Start_Lon"]), float(row["Start_Lat"]))
                    setbits.append(self.get_setbit_string("pickup_grid_id", field["pickup_grid_id"], reader.line_num))

                    field["drop_grid_id"] = self.get_grid_id(float(row["End_Lon"]), float(row["End_Lat"]))
                    setbits.append(self.get_setbit_string("drop_grid_id",  field["drop_grid_id"], reader.line_num))

                    field["duration_minutes"] = self.get_duration_minutes(pickup,drop)
                    setbits.append(self.get_setbit_string("duration_minutes", field["duration_minutes"], reader.line_num))

                    field["speed_mph"] = self.get_speed_mph(float(row["Trip_Distance"]), pickup,drop)
                    setbits.append(self.get_setbit_string("speed_mph", field["speed_mph"], reader.line_num))

                    field["cab_type"] = "Yellow"
                    setbits.append(self.get_setbit_string("cab_type", 1, reader.line_num))

                    str = ' '.join(setbits)
                    bits_string.append(str)

                    fields.append(field)

                    if lines and len(fields) >= int(lines):
                        break
                    if len(fields) % 1000000 == 0:
                        print (len(fields))
                print ("Total requests: %s" % len(fields))
        except Exception as ex:
            print (ex)
            pass
        stats1 = Stats()
        print ("Time multiple setbit")
        set_bit_results = {}
        self.reset_db("taxi1")
        for bit in bits_string:
            res = requests.post(url='http://localhost:10101/index/taxi1/query', data=bit).elapsed.total_seconds()
            s_max, s_min, total, num = stats1.add_duration(res * 1000)
            set_bit_results["max"] = s_max
            set_bit_results["min"] = s_min
            set_bit_results["avg"] = float(total / num)
        print (set_bit_results)

        stats = Stats()
        input_def_results = {}
        print ("Time input definition")
        self.reset_db("taxi1")
        for fld in fields:
            res = requests.post(url='http://localhost:10101/index/taxi1/input/def1', data=json.dumps([fld])).elapsed.total_seconds()
            s_max, s_min, total, num = stats.add_duration(res * 1000)
            input_def_results["max"] = s_max
            input_def_results["min"] = s_min
            input_def_results["avg"] = float(total/num)

        print(input_def_results)

        # print("Writing to json file")
        # with open(self.get_path("taxi_input.json"), "w") as json_file:
        #     json.dump(fields, json_file, indent=4, sort_keys=True)
        # print ("Done")

    def reset_db(self, name):
        delt = requests.delete(url='http://localhost:10101/index/%s' % name)
        if delt.status_code != 200:
            print (delt.text)
        created = requests.post(url='http://localhost:10101/index/%s' % name, data=json.dumps({"options": {"columnLabel": "id"}}))
        if delt.status_code != 200:
            print (created.text)
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        res = requests.post(url="http://localhost:10101/index/%s/input-definition/def1" % name, data=open('taxi_definition.json', 'rb'), headers=headers)
        if delt.status_code != 200:
            print (res.text)

    def get_path(self, filename):
        return os.path.join(os.getcwd(), filename)

    def get_time(self, x):
        time_in_sec = datetime.timedelta(hours=x.hour, minutes=x.minute, seconds=x.second).total_seconds()
        return int(time_in_sec * 30 / 86400)

    def get_duration_minutes(self, pickup, drop):
        min_diff = (drop - pickup).seconds/60
        return int(round(min_diff))

    def get_speed_mph(self, dist_miles, pickup, drop):
        # round(dist_miles / (drop_timestamp - pickup_timestamp).minutes)
        if (drop - pickup).seconds == 0:
            return None
        else:
            return int(round(dist_miles/(float((drop - pickup).seconds) / 3600)))

    def get_grid_id(self, x, y):
        """
        this needs to be identical to the GridMapper.ID function in PDK
        """

        if x < self.xmin or x > self.xmax or y < self.ymin or y > self.ymax:
            return None

        xi = math.floor(self.xres * (x - self.xmin) / (self.xmax - self.xmin))
        yi = math.floor(self.xres * (y - self.ymin) / (self.ymax - self.ymin))
        grid_id = int(self.yres * xi + yi)

        return grid_id

    def get_setbit_string(self, frame, rowID, id):
        if not rowID or not id:
            return ""
        return "SetBit(frame='%s', rowID=%s, id=%s)" % (frame, rowID, id)

class Stats:
    def __init__(self, s_min=sys.maxint, s_max=0, num=0, all=[], total=0 ):
        self.min = s_min
        self.max = s_max
        self.num = num
        self.all = all
        self.total = total

    def add_duration(self, duration):
        self.all.append(duration)
        self.num += 1
        self.total += duration
        if duration < self.min:
            self.min = duration

        if duration > self.max:
            self.max = duration
        return self.max, self.min, self.total, self.num

    def avg(self):
        return self.total/self.num



def main():
    if len(sys.argv) > 3:
        print("Usage: python build_taxi_data.py file number_of_lines")
        sys.exit(1)

    st = TaxiData()
    if len(sys.argv) == 3:
        st.build(sys.argv[1], sys.argv[2])
    else:
        st.build(sys.argv[1])
if __name__ == '__main__':
    main()
