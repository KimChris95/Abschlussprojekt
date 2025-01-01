# -*- coding: utf-8 -*-

import os
import copy

DEFAULT_SENSOR_BLOCK = {
    "active" : True,
    "evals"  : None,
    "rate"   : "1 s",
    "used_channels" : None,
    "model" : None,
    "label" : None,
    "height" : None,
    "type" : None
}

DEFAULT_EVAL_BLOCK = {
    "statistics_bis": None,
    "active": True,
    "formula": None,
    "statistics": None,
    "sensors": None,
    "statistics_ter": None,
    "label": None,
    "formula_params": None,
    "type": None,
    "unit" : None
}

DEFAULT_SETTINGS = {
    "WINDSPEED": {
        "unit": "m/s",
        "slope_unit": "m/s/I",
        "offset_unit": "m/s",

    },
    "WIND_DIRECTION": {
        "unit": "°",
        "slope_unit": "°",
        "offset_unit": "°",

    },
    "TEMP": {
        "unit": "°C",
        "slope_unit": "°C/V",
        "offset_unit": "°C",

    },
    "HUMIDITY": {
        "unit": "%",
        "slope_unit": "%/V",
        "offset_unit": "%",

    },
    "PRESSURE": {
        "unit": "hPa",
        "slope_unit": "hPa/V",
        "offset_unit": "hPa",
    }
}


class SensorBase:

    def __init__(self, sensor_index, eval_index, available_channels, SENSOR_DB, **kwargs):
        print(f"{type(self).__name__}::init")
        self.sensor_index = sensor_index
        self.eval_index = eval_index
        self.available_channels = available_channels
        self.cfg = kwargs
        self.name = self.cfg.get('name',"unnamed")
        self.height = self.cfg.get('height',0.0)
        self.type_no = self.cfg.get('type_no',None)
        self.serial = self.cfg.get('serial',"SNxxxyyyy")
        self.type_no = self.cfg.get('type_no',"")
        self.mess_typ = self.cfg.get("mess_typ",[])
        self.channel = None
        self.eval_dicts = []
        self.create_eval_section()
        self.create_sensor_section()
        self.update_eval()


    def _set_if_exists(self,key, name=None):
        if name is None:
            name = key
        if self.cfg[key]:
            self._sensor[name] = self.cfg[key]

    def create_sensor_section(self):
        self._sensor = copy.deepcopy(DEFAULT_SENSOR_BLOCK)
        self._sensor["model"] = self.cfg["model"]
        self._sensor["label"] = self.name
        self._sensor["height"] = self.height
        self._sensor["type"] = self.cfg["type"]
        self._sensor["used_channels"] = self.channel
        self._sensor["evals"] = self.eval_index
        self._sensor["serial_number"] = self.serial
        self._set_if_exists("url", name="url_path")
        self._set_if_exists("protocol")
        self._set_if_exists("adc_range_u")
        self._set_if_exists("sensor_type")
        self._sensor["model_id"] = int(self.cfg["model_id"]) 
        self._sensor["evals"] = ",".join(str(self.eval_index + i) for i in range(self.get_number_of_evals()))
        self.process_sensor_section()  
        result = {f"Sensor_{self.sensor_index}" : self._sensor}
        return result

    def create_eval_section(self):
        formula_splited, statistics = self.convert_values_from_db()
        for x in range(self.get_number_of_evals()):
            self.cfg = copy.deepcopy(DEFAULT_SETTINGS.get(self.cfg["mess_typ"].split(", ")[x], {})) | copy.deepcopy(self.cfg) # self.cfg erweitern um die jeweils passenden DEFAULT werte. 
            self.select_channel(self.available_channels)
            eval_dict = copy.deepcopy(DEFAULT_EVAL_BLOCK)
            eval_dict["statistics"] = statistics[x]
            self.activision_values_stat = statistics[x]
            eval_dict["label"] = self.name
            eval_dict["formula"] = formula_splited[x]
            eval_dict["formula_params"] = f"{self.channel.split(',')[x]}" + (f",{self.cfg.get('formula_params').split('/ ')[x]}" if self.cfg.get("formula_params") is not None else "")
            eval_dict["type"] = self.cfg["eval_type"].split(", ")[x]
            eval_dict["unit"] = self.cfg["unit"]
            self.create_activision_values(x)
            self.process_eval_section(eval_dict, x)
            self.eval_dicts.append(eval_dict)

    def convert_values_from_db(self): 
        if "," in self.cfg["formula"]:
            formula_splited = self.cfg["formula"].split(", ")
        elif "," not in self.cfg["formula"] and self.get_number_of_evals() > 1 :
            formula_splited = [self.cfg["formula"]] * self.get_number_of_evals()
        else: 
            formula_splited = [self.cfg["formula"]]
            
        if "/" in self.cfg["statistics"] : 
            statistics = self.cfg["statistics"].split("/")
        if not "/"  in self.cfg["statistics"] :
            statistics = []
            statistics.extend([self.cfg["statistics"]] * self.get_number_of_evals())
        return formula_splited, statistics

    def update_eval(self):
        for x in range(self.get_number_of_evals()):
            self.eval_dicts[x]["sensors"] = self.sensor_index

    def create_activision_values(self, x):
        self.activision_values = {"active": True}
        if "A" in self.channel: 
            self.process_activision_values(x)
        else: 
            self.process_activision_values(x)

    def process_activision_values(self, x):
        pass

    def get_number_of_evals(self):
        return int(self.cfg["counter_evals"])


    def select_channel(self, channels):
        channel_type = self.cfg["channel_type"]
        channel_for_sensor = channels[channel_type].pop(0)
        if not self.channel:
            self.channel = f"{channel_type}{channel_for_sensor}"
        else:
            self.channel += "," +  f"{channel_type}{channel_for_sensor}"
        print(f"{type(self).__name__}::select_channel {self.channel}")
        return self.channel
                
    def process_sensor_section(self):
        pass

    def process_eval_section(self):
        pass

    def get_sections(self):
        s = {f"Sensor_{self.sensor_index}": self._sensor}
        evals = {f"Eval_{self.eval_index + index}": eval_dict for index, eval_dict in enumerate(self.eval_dicts)}
        sections = [{k: v} for k, v in s.items()]
        sections.extend([{k: v} for k, v in evals.items()])
        return sections

##############################################################

class Anemometer(SensorBase):

    def __init__(self,sensor_index, eval_index, available_channels, SENSOR_DB, **kwargs):
        super().__init__(sensor_index, eval_index, available_channels,SENSOR_DB, **kwargs)


    def process_activision_values(self, x):
        self.activision_values["statistics"] = self.cfg["statistics"]

    def process_sensor_section(self):
        pass


    def process_eval_section(self, eval_dict, x):
        eval_dict["offset_unit"] = self.cfg["offset_unit"]
        eval_dict["var_offset"] = self.cfg["offset"]
        eval_dict["var_minimal_value"] = 0
        eval_dict["slope_unit"] = self.cfg["slope_unit"]
        eval_dict["var_slope"] = self.cfg["slope"]
        eval_dict["minimal_value_unit"] = self.cfg["unit"]
        eval_dict["var_period"] = 1
                  


##############################################################

class WindVane(SensorBase):
    def __init__(self,sensor_index, eval_index, available_channels, SENSOR_DB, **kwargs):
        super().__init__(sensor_index, eval_index, available_channels,SENSOR_DB, **kwargs)
        del self.cfg["sensor_type"]

    def process_activision_values(self, x):
        self.activision_values["protocol"] = self.cfg["protocol"]

    def process_sensor_section(self):
        if "sensor_type" in self._sensor:
            del self._sensor["sensor_type"]
        if "protocol" in self._sensor:
            del self._sensor["protocol"]
            self._sensor["digital_protocol"] = self.cfg["protocol"]
    

    def process_eval_section(self, eval_dict, x ):
        eval_dict["offset_unit"] = self.cfg["offset_unit"]
        eval_dict["var_offset"] = self.cfg["offset"]
        eval_dict["var_slope"] = self.cfg["slope"]
        eval_dict["var_offset_installation"] = 0.0
        eval_dict["formula_params"] = f"{self.channel},var_offset,var_slope,var_offset_installation"
        
        if self.cfg["sensor_type"] == "A,A": # Windfahnen die analoge Channels Nutzen. 
            self.select_channel(self.available_channels)
            selected_channel = self.channel
            base_channel = selected_channel[0]  
            channel_number = int(selected_channel[1:2])  
            self.channel = f"{base_channel}{channel_number}"  
            next_channel = f"{base_channel}{channel_number + 1}"  
            eval_dict["formula_params"] = f"{self.channel},{next_channel},var_offset,var_slope,var_offset_installation"
            self.channel = f"{self.channel},{next_channel}"

        
        

##############################################################

class Barometer(SensorBase):

    def __init__(self,sensor_index, eval_index, available_channels, SENSOR_DB, **kwargs):
        super().__init__(sensor_index, eval_index, available_channels,SENSOR_DB, **kwargs)

    def process_activision_values(self, x):
        self.activision_values["range"] =  self.cfg.get("adc_range_u")

    def process_sensor_section(self):
        pass
        

    def process_eval_section(self, eval_dict, x):

        eval_dict["offset_unit"] = self.cfg["offset_unit"]
        eval_dict["var_offset"] = self.cfg["offset"]
        eval_dict["var_slope"] = self.cfg["slope"]
        eval_dict["formula_params"] = f"{self.channel},var_offset,var_slope"
        eval_dict["slope_unit"] = self.cfg["slope_unit"]

##############################################################

class Temperature_and_Humidity(SensorBase):
    types = ["humidity", "temperature"]
    def __init__(self,sensor_index, eval_index, available_channels, SENSOR_DB, **kwargs):
        super().__init__(sensor_index, eval_index, available_channels,SENSOR_DB, **kwargs)

    def process_activision_values(self, x):
        self.activision_values["range"] =  self.cfg.get("adc_range_u")

    def process_sensor_section(self):
        self._sensor["used_channels"] = self.channel
        del self._sensor["sensor_type"]


    def process_eval_section(self, eval_dict, x):
        if self.get_number_of_evals() > 1 : 
            slope_split = self.cfg["slope"].split(",")
            offset_split = self.cfg["offset"].split(",")
        else: 
            slope_split = [self.cfg["slope"]]
            offset_split = [self.cfg["offset"]]
        eval_dict["offset_unit"] = self.cfg["offset_unit"]
        eval_dict["var_offset"] = offset_split[x]
        eval_dict["var_slope"] = slope_split[x]
        eval_dict["slope_unit"] = self.cfg["slope_unit"]
        print( self.cfg["eval_type"].split(",")[x])
        if self.cfg["eval_type"].split(",")[x].strip() == "humidity": 
            eval_dict["var_clip"] = 100
       

