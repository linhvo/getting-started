import json
import os
import sys
import csv
import datetime

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

        frames = [i["name"] for i in self.definition["frames"]]

        fields = []
        try:
            with open(path) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    field = {}
                    pickup = datetime.datetime.strptime(row["Trip_Pickup_DateTime"], '%Y-%m-%d %H:%M:%S')
                    field["id"] = reader.line_num
                    field["pickup_year"] = pickup.year
                    field["pickup_month"] = pickup.month
                    field["pickup_day"] = pickup.day
                    field["pickup_time"] = self.get_time(pickup)

                    drop = datetime.datetime.strptime(row["Trip_Dropoff_DateTime"], '%Y-%m-%d %H:%M:%S')
                    field["drop_year"] = drop.year
                    field["drop_month"] = drop.month
                    field["drop_day"] = drop.day
                    field["drop_time"] = self.get_time(drop)

                    field["dist_miles"] = int(round(float(row["Trip_Distance"])))
                    field["total_amount_dollars"] = int(round(float(row["Total_Amt"])))
                    field["passenger_count"] = int(row["Passenger_Count"])
                    field["pickup_grid_id"] = self.get_grid_id(float(row["Start_Lon"]), float(row["Start_Lat"]))
                    field["drop_grid_id"] = self.get_grid_id(float(row["End_Lon"]), float(row["End_Lat"]))
                    field["duration_minutes"] = self.get_duration_minutes(pickup,drop)
                    field["speed_mph"] = self.get_speed_mph(float(row["Trip_Distance"]), pickup,drop)
                    field["cab_type"] = "Yellow"

                    fields.append(field)
                    if lines and len(fields) >= int(lines):
                        break
                    if len(fields) % 1000000 == 0:
                        print (len(fields))
                print (len(fields))
        except Exception as ex:
            print (ex)
            pass

        print("Writing to json file")
        with open(self.get_path("taxi_input.json"), "w") as json_file:
            json.dump(fields, json_file, indent=4, sort_keys=True)
        print ("Done")

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


curl -vX POST http://localhost:10101/index/taxi1/input/def1 -d /Users/lvo/dev/pilosa/getting-started/taxi_input.json \
--header "Content-Type: application/json"