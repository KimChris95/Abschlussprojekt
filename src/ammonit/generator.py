# -*- coding: utf-8 -*-
import os
import copy 
import pandas as pd 
import configparser
import re 
from io import StringIO
from datetime import datetime, timezone
from ammonit import excel_reader_manufactureplan
from ammonit import pdf_extractor_slope_offset
from sensor import WindVane, Anemometer, Barometer, Temperature_and_Humidity
from ammonit import static_info
from ammonit import ASSETS_DIR



class Generator(): 
    
    sensor_classes = {
        "anemometer": Anemometer,
        "wind_vane":  WindVane,
        "barometer":  Barometer,
        "hygro_thermo":  Temperature_and_Humidity,
    }
    sensor_list    = []
    sensor_index   = 1
    eval_index     = 1


    def __init__(self, manufacture_plan_path):
        self.search_values  = ["Serial Number", "Slope", "Offset"]
        self.load_db()
        self.create_config_from_manufacturing_plan(manufacture_plan_path) 
        self.load_db 
        
        
    def load_db(self) :
        db = pd.read_excel(os.path.join(ASSETS_DIR,"sensor_db.xlsx"),index_col=0)
        db["model_id"] = db["model_id"].astype("int")
        
        for col in db.columns:
            db.loc[db[col].isna(),col] = None
            
        
        self.db = db.to_dict(orient="index")


    def create_config_from_manufacturing_plan(self, manufacture_plan_path) :
        self.validate_path(manufacture_plan_path)
        output_folder_path, certificates_folder = self.create_paths(manufacture_plan_path)
        self.validate_path(certificates_folder)

        sensors_data_frame, project_informations = excel_reader_manufactureplan.read_man_plan(manufacture_plan_path)
        
        self.projekt_number = project_informations[0]
        self.name = project_informations[1]
        self.serial_number = project_informations[2] 
        ##############
        self.initialize_channels()
        self.create_system_info()
        self.create_channels()
        self.create_system_dict()
        ##############

        typ_no = ""
        label = ""
        serial_number = ""
        height = ""
        cert_no = ""
        cert = False
        slope = None 
        offset = None 
        columns = sensors_data_frame.columns.tolist()
        for index, row in sensors_data_frame.iterrows():
            for x, col in enumerate(columns):
                if col == "serial_number":
                    serial_number = row.iloc[x]  
                elif col == "type_no":
                    typ_no = row.iloc[x]
                elif col == "label":
                    label = row.iloc[x]
                elif col == "height":
                    height = row.iloc[x]
                elif col == "cert_no":
                    if row.iloc[x] != "-": # im Herstellungsplan sind nicht kalibrierte Sensoren mit einem - statt der Kalibiriernummer gekennzeichnet. 
                        cert_no = row.iloc[x]
                        print(f"Please wait, extracting Slope and Offset from PDF for {serial_number}")
                        slope, offset = pdf_extractor_slope_offset.extract_slope_offset(serial_number, certificates_folder, self.search_values) ######################## 5. 
                        cert = True
                        if not slope and not offset: 
                            print(f"Can´t find Slope and Offset for {serial_number} Please add it manually")
            if cert :
                self.add_sensor(typ_no, label, serial_number, height, cert_no, slope, offset)
                cert = False
                slope = None 
                offset = None 
            else:
                self.add_sensor(typ_no, label, serial_number, height)
        config = self.create_ini_config(output_folder_path)
        print(output_folder_path)
        return config
        

    def validate_path(self, path): 
        if not os.path.exists(path):
            raise FileNotFoundError(f"The file '{path}' dosen´t exists")
            return None
        else: pass 

    def create_paths(self, manufacture_plan_path):
        folder_name = "config"
        manufacture_plan_folder = os.path.dirname(manufacture_plan_path)
        project_folder = os.path.dirname(manufacture_plan_folder)
        certificates_folder = os.path.join(project_folder, "06_Certificates")
        new_folder_path = os.path.join(project_folder, folder_name)
        os.makedirs(new_folder_path, exist_ok=True) 
        output_folder_path = os.path.join(project_folder, folder_name)
        return output_folder_path, certificates_folder 

    def add_sensor(self, type_no, name, serial, height, cert_no=None, slope=None, offset=None):
        type_no_x = self.convert_type_no(type_no) 

        if type_no_x not in self.db:
            print(f"ERROR: Sensor type {type_no_x} not found in self.db")
            return None
        cfg = copy.deepcopy(self.db[type_no_x])
        cfg.update({
            "type_no": type_no_x,
            "name": name,
            "serial": serial,
            "height": height,
            "cert_no": cert_no,
        })
        
        if slope is not None: 
            cfg["slope"] = slope
        if offset is not None: 
            cfg["offset"] = offset
            
        sensor_class = self.sensor_classes.get(cfg["type"].strip())
        if not sensor_class:
            print(f"ERROR: unknown type <{cfg['type']}>")
            return None
        sensor_obj = sensor_class(self.sensor_index, self.eval_index, self.channels, self.db, **cfg)
        self.sensor_index += 1
        self.eval_index += sensor_obj.get_number_of_evals()
        self.sensor_list.append(sensor_obj)
        self.activate_channel(sensor_obj)
        if static_info.static_config["Evaluation"]["order"] is None:
            static_info.static_config["Evaluation"]["order"] = ""
        static_info.static_config["Evaluation"]["order"] = f"{static_info.static_config['Evaluation']['order']}{sensor_obj._sensor['evals']},"

        return sensor_obj

    def convert_type_no(self, type_no):
        parts = type_no.split(".")
        if len(parts) == 4 and parts[0] == "4":
                parts[2] = "x0"
        return ".".join(parts)


    def activate_channel(self, sensor_obj):
        sensor_channels = sensor_obj._sensor["used_channels"].split(",")
        for index_one, (channels, keys) in enumerate(self.channel_mapping.items()) :
            for key, value in keys.items():
                for index_two, (channels_) in enumerate(sensor_channels):
                    if key == sensor_channels[index_two] and len(sensor_channels) == 1 :
                        values = sensor_obj.activision_values
                        value.update(values)
                    elif  key == sensor_channels[index_two]:
                        values = sensor_obj.activision_values
                        value.update(values)
                        if "range" in sensor_obj.activision_values:
                            value_list = sensor_obj.activision_values["range"].split(";")
                            value_extracted = {"range": value_list[index_two]}
                            value.update(value_extracted)

    def format_value(self, value):
        string_value = str(value)
        if value is None:
            return ''
        elif value is True:
            return "true"
        elif value == "None": 
            return "none"
        elif value is False:
            return "false"
        elif "´" in string_value:
            new_string = string_value[1:]
            return new_string
        else:
            return str(value).strip()
        
    def write_config(self, ini, path_output_folder) :
        """
            Schreibt eine Konfiguration in eine Datei und ergänzt sie mit Systeminformationen und Kommentaren.
        
            Diese Methode verwendet die `StringIO`-Klasse, um die Konfigurationsdaten im Speicher zwischenzuspeichern, bevor sie in eine Datei geschrieben werden.
            Dadurch entfällt der direkte Zugriff auf physische Dateien während der Verarbeitung. Die Konfiguration wird zusätzlich mit
            systembezogenen Kommentaren ergänzt.
        
            Args:
                ini (ConfigParser): Das ConfigParser-Objekt, das die Konfigurationsdaten enthält.
                path_output_folder (str): Der Pfad zum Ausgabeverzeichnis, in dem die Konfigurationsdatei gespeichert wird.
        
            Ablauf:
                1. Die Methode schreibt die Konfigurationsdaten mithilfe von `ConfigParser.write` in ein `StringIO`-Objekt.
                2. Mit `.getvalue()` wird der gesamte Inhalt aus dem `StringIO`-Objekt als String extrahiert.
                3. Systeminformationen und zusätzliche Kommentare werden dem Konfigurationsstring vorangestellt.
                4. Der vollständige Text wird in eine Datei im angegebenen Ausgabeverzeichnis geschrieben.
        
            Returns:
                str: Die endgültige Konfigurationsdatei als String, einschließlich Systeminformationen und Kommentaren.
        """
        temp = StringIO()
        ini.write(temp, space_around_delimiters=False)
        ini_data = temp.getvalue()
        system_info_str = "\n#".join(self.system_info)
        ini_with_comments = f"#{system_info_str}\n#Created Sensors                 {self.sensor_index}\n\n{ini_data}"

        new_filename = os.path.join(path_output_folder, f"{self.serial_number}_configuartion.txt")
        
        print(new_filename)

        with open(new_filename, "w", encoding="utf-8") as configfile:
            configfile.write(ini_with_comments)
        return ini_with_comments


    def initialize_channels(self):
        """
            Mit der Dict Comprehension wird für den Channel R1C 8 listen erstellt mit jeweils 8 einträgen
            i steht für die Keys in diesem fall 1 - 8 und für jeden eintrag wird ein liste
            erstellt mit einer Range zwischen 1 und 9 die endziffer ist nicht enthalten
            also bekomme ich 8 listen mit 8 einträgen.
            R1C = {}
            for i in range(1,9) :
                valuelist = []
                for y in range(1,9):
                    valuelist.append(y)
                R1C[i] = value_list
        """
        R1C = {i: list(range(1, 9)) for i in range(1, 9)} # gruselig

        """
            list(range(1,9))
            range(1,9) erzeugt eine sequenz von einschlieslich 1 und ausschließlich 9 das heist 1 - 8
            durch list(range(1,9)) wandle ich diese sequenz in eine Liste um
            einfach Methode um listen schnell und effizient zu erstellen.
            value_list = []
            for i in range(1,9):
                value_list.append(i)
        """
        channels = {
            "M": {
                "C": list(range(1, 9)),
                "D": list(range(1, 5)),
                "A": list(range(1, 9)),
                "AC": [1],
                "P": [1, 2],
                "R": [1],
                "R1C": R1C,
                "Switch": list(range(1, 5)),
                "Period": [1, 2]
            },
            "S": {
                "C": list(range(1, 5)),
                "D": list(range(1, 3)),
                "A": list(range(1, 5)),
                "AC": [1],
                "P": [1],
                "R": [1],
                "R1C": R1C,
                "Switch": list(range(1, 3))
            },
            "L": {
                "C": list(range(1, 13)),
                "D": list(range(1, 9)),
                "A": list(range(1, 13)),
                "AC": [1, 2],
                "P": list(range(1, 5)),
                "R": [1],
                "R1C": R1C,
                "Switch": list(range(1, 9)),
                "Period": list(range(1, 5))
            }
        }
        
        """sucht nach dem ersten Treffer im Text 
        /D ein nicht Zahlen Zeichen,
        \d+ eine oder mehrere Ziffern als erste Gruppe,
        LMS ein einzelnes Zeichen welches LM oder S sein muss 
        .group(2) erste Gruppe sind die Zeichen - Zeite gruppe sind LM oder S 
        der gefundene Buchstabe wird der Variabele datalogger_typ zugewiesen 
        """ 
        datalogger_typ = re.search(r"\D(\d+)([LMS])", self.name).group(2)
        if datalogger_typ in channels:
            self.channels = channels[datalogger_typ]
            self.name = f"Meteo-40{datalogger_typ}"
        else:
            raise ValueError(f"Unknown datalogger type: {self.name}")
            
            
    def create_system_info(self):

        now_utc = datetime.now(timezone.utc)
        timestamp = now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')
        period_measurement_count = len(self.channels.get('Period', []))
        channel_summary = (
            "Number of Channels              "
            f"{len(self.channels.get('A', []))} Analog Voltage, "
            f"{len(self.channels.get('C', []))} Counters, "
            f"{len(self.channels.get('AC', []))} Analog Current, "
            f"{len(self.channels.get('P', []))} Current Sources, "
            f"{len(self.channels.get('D', []))} Digital, "
            f"{len(self.channels.get('Switch', []))} Switches, "
            "8 RS485"
        )
        
        
        if period_measurement_count > 0:
            channel_summary += f", {period_measurement_count} Period Measurement"

        self.system_info = [
                   "Ammonit Data Logger - System Information",
                   "----------------------------------------",
                   "",
                   f"Data Logger Type                {self.name}",
                   f"Serial Number                   {self.serial_number}",
                   channel_summary,
                   "Data Logger Location            unknown",
                   "RAM                             Total: 119 MiB, Used: 54 MiB, Available: 63 MiB",
                   "Source Data Memory              1960.51MiB (0.02% used, page-id: 944)",
                   "System Memory                   Total: 447 MiB, Used: 163 MiB, Free: 284 MiB",
                   "Number of Statistics Files      0",
                   "Software Version                2.1.8 (2023-01-19)",
                   "Bootloader Version              10395",
                   "Current Connections             Admin (192.168.1.0)",
                   f"Date/time                       {timestamp}"
               ]


    def create_system_dict(self):

        self.system = {
            "System" : {
                "name": self.projekt_number, 
                "config_id": "1.1.1711442282", 
                "camera_url": None,
                "camera_copy_to_usb": False,
                "set_dt_method": "use_ntp",
                "set_dt_threshold": 0.4,
                "ntpserver": "0.pool.ntp.org 1.pool.ntp.org 2.pool.ntp.org 3.pool.ntp.org",
                "timezone": "UTC+01:00",
                "display_permissions": "network,rec_on,switches,wlan,action",
                "display_backlight": True,
                "cecs_power_permanent": True,
                "cecs_power_on_status": "none",
                "cecs_auto_reboot": "weekly",
                "longitude": None,
                "latitude": None,
                "altitude": None,
                "power_supply": None,
                "min_supply_voltage": 11.5,
                "sign_enc": "sign",
                "force_enc": False
            }
        }

    def create_channels(self):

        self.analog_channels = {}
        self.counter_channels = {}
        self.digital_channels = {}
        self.ac_channels = {}
        self.p_channels = {}
        self.r_channels = {}
        self.r1_channels = {}

        self.channel_mapping = {
            "A": self.analog_channels,
            "C": self.counter_channels,
            "D": self.digital_channels,
            "AC": self.ac_channels,
            "P": self.p_channels,
            "R": self.r_channels,
            "R1C": self.r1_channels,
        }

        channel_dict = {
            "A": {
                "active": False,
                "rate": "1 s",
                "range": "10 V",
                "switch_active": False,
                "switch_id": "S1",
                "switch_pretime": "1 min",
                "statistics": "avg,max,min,stddev,count",
                "statistics_bis": None,
                "statistics_ter": None
            },
            "C": {
                "rate": "1 s",
                "active": False,
                "switch_active": False,
                "switch_id": "S1",
                "switch_pretime": "1 min",
                "statistics": "avg,max,min,stddev,count",
                "statistics_bis": None,
                "statistics_ter": None
            },
            "D": {
                "rate": "1 s",
                "protocol": "none",
                "active": False,
                "switch_active": False,
                "switch_id": "S1",
                "switch_pretime": "1 min",
                "statistics": "avg,max,min,stddev,count",
                "statistics_bis": None,
                "statistics_ter": None
            },
            "AC": {
                "active": False,
                "rate": "1 s",
                "range": "100 mA",
                "switch_active": False,
                "switch_id": "S1",
                "switch_pretime": "1 min",
                "statistics": "avg,max,min,stddev,count",
                "statistics_bis": None,
                "statistics_ter": None
            },
            "P": {
                "rate": "1 s",
                "type": "None",
                "active": False,
                "statistics": "avg,max,min,stddev,count",
                "statistics_bis": None,
                "statistics_ter": None
            },
            "R": {
                "rate": "1 s",
                "serial_speed": 38400,
                "serial_format": "8N1",
                "sensors_check": False,
                "biasing_enable": False
            },
            "R1C": {
                "active": False,
                "protocol_type": "None",
                "sensor_type": "MODBUS_OTHER",
                "address": 0,
                "modbus_start_register": 0,
                "modbus_function_code": 4,
                "modbus_register_quantity": 1,
                "modbus_data_type": "IEEE754",
                "modbus_word_endianness": "high_first",
                "statistics": "count",
                "statistics_bis": None,
                "statistics_ter": None
            }
        }

        for index, (channel_type, numbers) in enumerate(self.channels.items()):
            if index > 6 : # Damit begrenze ich welche Channels er nehmen soll, ist ziemlich rudimentär aber nach dem 7ten durchlauf soll er aufhören da ich nur 7 Channels bauen muss.
                break
            for number in numbers:
                if channel_type != "R1C" :
                    key = f"{channel_type}{number}"
                    self.channel_mapping[channel_type][key] = copy.deepcopy(channel_dict[channel_type])
                else:
                    for sub_number, sub_channels in numbers.items():
                        for sub_channel in sub_channels:
                            key = f"{channel_type}{sub_number}"

                            self.channel_mapping[channel_type][key] = copy.deepcopy(channel_dict[channel_type])
  
    def create_ini_config(self, path_output_folder):
        config = configparser.RawConfigParser()
        """
            Aufteilung in static_config_dicts und static_config_dicts_over_sensor da zwischen diese Parts die Channels müssen
            Durch ** werden die Dicts ausgepackt und an ein neues Dict in diesem Fall ini angehängt.
        """
        static_info.static_config["Evaluation"]["order"] = static_info.static_config["Evaluation"]["order"][:-1]
        #Entfernt ein "," am Ende

        ini = {**self.system, **static_info.static_config,
               **self.analog_channels,**self.ac_channels, **self.counter_channels, **self.p_channels , **self.digital_channels,
               **self.r_channels, **self.r1_channels ,** static_info.static_config_over_sensors}

        for section, values in ini.items():
            if section not in config:
                config.add_section(section)
            for key, value in values.items():
                config.set(section, key, self.format_value(value))

        for sensor in self.sensor_list:
            for each_block in sensor.get_sections():
                for section, values in each_block.items():
                    if section not in ini:
                        ini[section] = {}
                    for key, value in values.items():
                        ini[section][key] = self.format_value(value)
                    if not config.has_section(section):
                        config.add_section(section)
                    for key, value in ini[section].items():
                        config.set(section, key, str(value))

        self.write_config(config, path_output_folder)
        return("Succesfully create")
    
if __name__ == "__main__":
    print("*** CONFIG GENERATOR ***")
    manufacture_plan_path =r"C:\Users\chris\Desktop\Abschlussprojekt\assets\project_template\01_Connection Planung\3034_KOR_ConnectionScheme_V2_VZ.xlsm"
    c = Generator(manufacture_plan_path)
