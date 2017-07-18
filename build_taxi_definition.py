import json
import sys


class TaxiDefinition:
    def build(self, filepath=None):
        cab_types = ["Yellow", "Green", "Uber"]
        store = self.build_map(cab_types)
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

        definition["fields"] = [
            {
                "name": "id",
                "primaryKey": True
            }]
        for i in definition["frames"]:
            field = {}
            action = {}
            field["name"] = i["name"]
            action["frame"] = i["name"]
            if action["frame"] == "cab_type":
                action["valueDestination"] = "mapping"
                action["valueMap"] = store
            else:
                action["valueDestination"] = "value-to-row"
            field["actions"] = [action]
            definition["fields"].append(field)

        input_def = json.dumps(definition, indent=4, sort_keys=True)
        if filepath:
            inputDef_file = open(filepath, "w")
            inputDef_file.write(input_def)
        else:
            print(input_def)

    def build_map(cls, cab_types):
        store = {}
        for i, x in enumerate(cab_types):
            store[x.strip()] = i + 1
        return store


def main():
    st = TaxiDefinition()
    if len(sys.argv) == 2:
        st.build(sys.argv[1])
    else:
        st.build()


if __name__ == '__main__':
    main()
