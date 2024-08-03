import json

class MapLoader:
    @staticmethod
    def load_map(maps_to_load):
        mappings = {}
        for map_file_name in maps_to_load:
            with open('mappings/' + map_file_name + '.json') as json_file:
                for key, value in json.load(
                    json_file, 
                    object_pairs_hook=MapLoader.on_duplicate_pairs # Give destinct error for duplicate keys within the same JSON file
                ).items():
                    # Ignore empty key strings, allows for easier map file building
                    if key == '': 
                        return
                    # Prevent duplicate keys across multiple files
                    if key in mappings and mappings[key] != value: 
                        raise ValueError(
                            'Duplicate keys with differnt values were found when creating the mapping.\n' +
                            'key: ' + str(key) + ', val1: ' + str(mappings[key]) + ', val2: ' + str(value)
                        )
                    # Add key/value
                    mappings[key] = value
        return mappings
    
    @staticmethod
    def on_duplicate_pairs(ordered_pairs):
        data = {}
        for key, value in ordered_pairs:
            # Ignore empty keys
            if key == '':
                continue
            # Throw error for duplicate keys
            if key in data:
                 raise ValueError(
                    'Duplicate keys were found within the same JSON file while mapping.\n' +
                    'key: ' + str(key)
                )
            # Collect the non-duplicate entries to return them if no error is thrown
            else:
                data[key] = value
        return data
    
