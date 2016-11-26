# Reactivity Series Scrape

filename_prefix = 'reactivity_series'

import sys, requests, openpyxl
from bs4 import BeautifulSoup

def download_raw_reactivity_series_data():
    result = []
    url = 'https://en.wikipedia.org/wiki/Reactivity_series'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    trs = soup.find_all('table')[0].find_all('tr')
    for tr in trs:
        result.append([td.text for td in tr.find_all('td')])
    return result

def download_reactivity_series():
    raw_reactivity_series = download_raw_reactivity_series_data()
    reactivity_series = [a[:2] for a in raw_reactivity_series if len(a) > 1]
    for row in reactivity_series:
        row.extend(row[0].split('\xa0'))
        row.pop(0)
        for c in range(len(row[0])):
            if row[0][c].isdigit() or row[0][c] == '+':
                row[0] = row[0][c:]
                break
        row[0] = row[0][:row[0].index('+')+1]
    return [['symbol', 'name', 'ion']] + [list(reversed(row)) for row in reactivity_series]

def write_excel_file(filename, data):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = filename_prefix
    for row in data:
        ws.append(row)    
    wb.save(filename)

def excel_workbook_to_list(filepath):
    retval = []
    wb = openpyxl.load_workbook(filepath)
    ws = wb.worksheets[0]
    for row in ws.iter_rows():
        retval.append([cell.value for cell in row])
    return retval

def get_json_from_excel_workbook(filepath):
    excel_data = excel_workbook_to_list(filepath)
    keys, j = excel_data[0], []
    for row in range(1, len(excel_data)):
        j.append({})
        for k in range(len(keys)):
            if excel_data[row][k] == None:
                excel_data[row][k] = 'n/a'
            j[-1].update( { keys[k] : excel_data[row][k] } )
    return j

def write_json_list_to_file(filepath, j):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        for row in j:
            outfile.write(str(row) + '\n')

def write_series_to_json_file(excel_filepath, json_filepath):
    j = get_json_from_excel_workbook(excel_filepath)
    write_json_list_to_file(json_filepath, j)

if __name__ == '__main__':
    reactivity_series = download_reactivity_series()
    write_excel_file(filename_prefix + '.xlsx', reactivity_series)
    write_series_to_json_file(filename_prefix + '.xlsx', filename_prefix + '.json')
