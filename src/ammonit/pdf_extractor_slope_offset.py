import os
import pdfplumber
import re


def get_filenames(directory, suffix=".pdf"): 
    pdf_paths = []
    for filename in os.listdir(directory):
        if filename.endswith(suffix):
            pdf_path = os.path.join(directory, filename)
            pdf_paths.append(pdf_path)
    return pdf_paths


def search_pdf_for_values(pdf_path, search_values):  
    """
        re.compile(r'\b' + re.escape(value) + r'\b|\b' + re.escape(value.replace(' ', '')) + r'\b', re.IGNORECASE) 
        re.complie erstellt ein reguläres Ausdrucksmuster für eine Suchoperation gibt ein Regex Objekt zurück 
        r steht für Rawstring er ermöglicht es escapezeichen zu vermeiden 
        \b ist ein Wortgrenzen Anker Entspricht einer Postion einer Grenze zwischen Wort und nicht Wort zeichen 
        value.replace beduetet das alle leerzeichen aus dem value entfernt werden z.b. Serial Number wird SerialNumber 
        | ist ein logisches Oder wird in re verwendet um verschiedene fälle zu erschaffen z.b. SerialNumber oder Serial Number 
        ignorecase wird verwendet um Groß oder Kleinschreibung zu ignorieren 
    """
    found_values = {value: [] for value in search_values}
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                for value in search_values:
                    pattern = re.compile(r'\b' + re.escape(value) + r'\b|\b' + re.escape(value.replace(' ', '')) + r'\b', re.IGNORECASE)
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        start_index = match.end()
                        end_index = start_index
                        while end_index < len(text) and not text[end_index].isalpha():
                            end_index += 1
                        found_value = text[start_index:end_index].strip()
                        found_values[value].append(found_value)
    return found_values

        
def search_pdfs(Serial_number, search_values, pdf_folder_path):
    filenames = get_filenames(pdf_folder_path)
    for pdf_path in filenames: 
        filename = os.path.basename(pdf_path)
        if Serial_number in filename:
            return(search_pdf_for_values(pdf_path, search_values))
    return False  


def extract_slope_offset(serial_number, pdf_folder_path, search_values): # search_values = List 
    serial_slope_offset = search_pdfs(serial_number, search_values, pdf_folder_path)
    if serial_slope_offset:
        print(serial_slope_offset)
        slope_values = serial_slope_offset.get('Slope', [])
        offset_values = serial_slope_offset.get('Offset', [])
        print(len(slope_values))
        if len(slope_values) > 1 : 
            for x, (value) in enumerate(slope_values) : 
                slope_values[x] = re.sub(r"[^\d.\-+]", "", value)
            for x, (value) in enumerate(offset_values) : 
                offset_values[x] = re.sub(r"[^\d.\-+]", "", value)
        else: 
            slope_values[0] = re.sub(r"[^\d.\-+]", "", slope_values[0])
            offset_values[0] = re.sub(r"[^\d.\-+]", "", offset_values[0])
        return slope_values, offset_values
    else : 
        return None, None 
        
if __name__ == "__main__":
    search_values = ["Serial Number", "Slope", "Offset"]
    pdf_folder_path = r"C:\Users\chris\Meine Ablage\Abschlussprojekt\assets\project_template\06_Certificates"
    found_values = extract_slope_offset("01246750", pdf_folder_path, search_values)
   