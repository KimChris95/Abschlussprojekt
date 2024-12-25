# -*- coding: utf-8 -*-


import os
import pandas as pd
from ammonit import ASSETS_DIR


def read_man_plan(filename):
    columns_to_check = ["Unnamed: 5"]
    dtypes = {"Serial Number":str,}
    df = pd.read_excel(filename, sheet_name="Manufacturing_Plan")
    df.reset_index(inplace=True,drop=True)
    col = df.iloc[:, 1]
    header_index = None
    stop_index = None 
    project_number = None 
    logger_type = None 
    serial_logger = None
    x = 0 
    for i, val in col.items(): 
        if val == "Sensor Type": 
            header_index = i + 1
        if header_index != None and pd.isna(val) and x != 1: 
            stop_index = i + 1
            x = 1 
        if val == "Project N°:": 
            project_number = df.iloc[i, 1 + 1] 
        if val == "Datalogger" : 
            logger_type = df.iloc[i, 1 + 1] 
            serial_logger = str(df.iloc[i, 1 + 2]) 
            break
            
    project_informations = [project_number, logger_type, serial_logger]
    del df 
    df = pd.read_excel(filename, sheet_name="Manufacturing_Plan",header = header_index, dtype=dtypes, nrows=stop_index)
    df.reset_index(inplace=True,drop=True)
    for col in columns_to_check: 
        if col in df.columns: 
            df["type_index"] = df["Unnamed: 5"].astype(int)
            df["label"] = df["Sensor Nom."].astype(str) + df["Unnamed: 5"].astype(str)
            df.drop(columns=["Sensor Nom.", "Unnamed: 5", "type_index"], inplace=True)
        else: 
            df = df.rename(columns={"Sensor Nom.":"label"})
            
    df.drop(labels=["Ordered Device", "No.", "Tested", "Comment Production", "Slope (m/s)/(Hz)", "Offset (m/s)", "Cable"],axis=1,inplace=True)
    
    df = df.rename(columns={"Sensor Type": "sensor_type", "Type/Model Nr.": "type_no", 
                            "Length [m]": "height", "Calibration Certificate No.": "cert_no",
                            "Serial Number": "serial_number", "Installation Height [m]": "height2"})
    if "height2" in df.columns: 
        if not df['height2'].isna().any():
            df.drop(columns="height", inplace=True)
            df = df.rename(columns={"height2":"height"})
        else: 
            df.drop(columns="height2", inplace=True)
    
    return df, project_informations
    


if __name__ == "__main__":
    test = r"C:\Users\chris\Desktop\Programmieren\ammonit_config_generator\assets\project_template\01_Connection Planung\2900-1_AUS_ConnectionScheme_V1_VZ.xlsm"
    filename  = os.path.join(ASSETS_DIR, 'excel_project_data', "2380_AUS_ConnectionScheme_V2_VZ.xlsm")
    df, project_informations = read_man_plan(test)



