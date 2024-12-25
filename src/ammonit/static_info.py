static_config = {
    "ModemGSM": {
        "permanent": True,
        "number": "*99#",
        "apn": "",
        "username": "",
        "allowed_modes": "",
        "preferred_mode": "",
        "bsd-comp": False,
        "deflate-comp": False,
        "vj-comp": False,
        "switch_id": "S1",
        "sms_active": False,
        "sms_receiver": "",
        "smsc": ""
    },
    "Ethernet": {
        "permanent": True,
        "method": "dhcp",
        "ip_address": "192.168.40.40",
        "subnet_mask": "255.255.255.0",
        "gateway": "192.168.40.1",
        "dns_server": "192.168.40.1",
        "switch_id": "none",
        "never_default": False,
        "addsubnet": ""
    },
    "Heating": {
        "switch_id": "none",
        "switch_invert": False,
        "label": "",
        "temperature_eval": "",
        "humidity_eval": "",
        "temperature_min": -10.0,
        "temperature_max": 2.0,
        "humidity_min": 70.0,
        "voltage_eval": "",
        "voltage_min": 0.0,
        "windspeed_eval": "",
        "windspeed_min": 20.0,
        "timer": False,
        "timer_on_1": "09:00",
        "timer_dur_1": "01:00",
        "timer_on_2": "21:00",
        "timer_dur_2": "01:00"
    },
    "WLAN": {
        "active": False,
        "ip_address": "192.168.42.1",
        "network": "192.168.42.0",
        "netmask": "255.255.255.0",
        "firstaddr": "192.168.42.2",
        "lastaddr": "192.168.42.254"
    },
    "ServerCopy": {
        "method": "scp",
        "server": "",
        "port": 0,
        "username": "",
        "ssl_verify": True,
        "directory": "",
        "startdate": "",
        "csv_data": True,
        "csv_bis_data": False,
        "csv_ter_data": False,
        "logbook": True,
        "config": True,
        "use_camera": False,
        "snapshot": False,
        "gustdata": False
    },
    "EMail": {
        "method": "tls",
        "server": "",
        "port": 0,
        "ssl_verify": False,
        "username": "",
        "from": "",
        "to": "",
        "cc": "",
        "popserver": "",
        "startdate": "",
        "csv_data": True,
        "csv_bis_data": False,
        "csv_ter_data": False,
        "logbook": True,
        "config": True,
        "use_camera": False,
        "snapshot": False,
        "gustdata": False,
        "max_attach": 10
    },
    "AmmonitConnect": {
        "active": True,
        "active_only_online_action": False,
        "active_only_for_signalling": False,
        "login": "_ac-login@D240096.connect.ammonit.com",
        "port": 4040,
        "accesscode": "",
        "xmpp_jids": ""
    },
    "AmmonitOR": {
        "project_key": "",
        "server": "upload.ammonit.com",
        "username": "upload",
        "port": 4041,
        "startdate": "",
        "csv_data": True,
        "csv_bis_data": False,
        "csv_ter_data": False,
        "logbook": True,
        "config": True,
        "use_camera": False,
        "snapshot": False,
        "gustdata": False
    },
    "LiveData": {
        "publish_livedata": False,
        "publish_avgdata": False,
        "open_nodes": False,
        "port": 443,
        "server": "",
        "allow_jids": "aligator@livedata.ammonit.com"
    },
    "SCADA": {
        "active": False,
        "serial_speed": 38400,
        "serial_format": "8N1",
        "id": 1,
        "protocol_type": "Modbus TCP",
        "port": 502,
        "allowed": "",
        "byte_endianness": "high_first",
        "word_endianness": "high_first",
        "global_access": False,
        "measurements_to_holding": False
    },
    "Evaluation": {
        "stat_interval": "10 min",
        "stat_bis_active": True,
        "stat_interval_bis": "10 min",
        "stat_ter_active": False,
        "stat_interval_ter": "10 min",
        "file_interval": "daily",
        "signal_stat_interval": "10 min",
        "signal_sum_interval": "daily",
        "order": "",
        "partial": False,
        "capacity_action": "stop"
    },
    "Gusts": {
        "active": False,
        "trigger_eval": "",
        "threshold": 20.0,
        "repetitions_min": 3,
        "repetitions_max": 15,
        "t_overhang": 15,
        "csv_evals": ""
    },
    "ActionAmmonitOR": {
        "weekdays": "mon,tue,wed,thu,fri,sat,sun",
        "time_start": "12:00",
        "time_interval": "06:00",
        "quantity": 1
    },
    "ActionEMail": {
        "weekdays": "mon,tue,wed,thu,fri,sat,sun",
        "time_start": "12:00",
        "time_interval": "06:00",
        "quantity": 1
    },
    "ActionCopy": {
        "weekdays": "",
        "time_start": "12:00",
        "time_interval": "06:00",
        "quantity": 1
    },
    "ActionOnline": {
        "weekdays": "mon,tue,wed,thu,fri,sat,sun",
        "time_start": "12:00",
        "time_interval": "06:00",
        "quantity": 1,
        "minimal_runtime": "00:20"
    },
    "CSVFilesGenerate": {
        "weekdays": "",
        "time_start": "12:00",
        "time_interval": "06:00",
        "quantity": 1
    }
}


static_config_over_sensors = {
    "I": {
        "active": True,
        "statistics": "avg,max,min",
        "statistics_bis": "",
        "statistics_ter": ""
    },
    "V": {
        "active": True,
        "statistics": "avg,max,min",
        "statistics_bis": "",
        "statistics_ter": ""
    },
    "T": {
        "active": True,
        "statistics": "avg",
        "statistics_bis": "",
        "statistics_ter": ""
    },
    "switches_state": {
        "active": True,
        "statistics": "first",
        "statistics_bis": "",
        "statistics_ter": ""
    },
    "User_1": {
        "name": "Admin",
        "permissions": "Admin",
        "active": True
    },
    "User_2": {
        "name": "User",
        "permissions": "User",
        "active": True
    },
    "User_3": {
        "name": "Viewer",
        "permissions": "Viewer",
        "active": True
    },
    "User_4": {
        "name": "Guest",
        "permissions": "Guest",
        "active": True
    },
    "Adjustment": {
        "CS1": "199.86 μA"
    }

    
}


#,
#'Adjustment': {
#    'CS1': '200.05 μA',
#    'CS2': '199.73 μA'
#}
