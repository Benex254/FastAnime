from datetime import datetime

# TODO: Add formating options for the final date
def format_anilist_date_object(anilist_date_object:dict|None):
    if anilist_date_object:
        return f"{anilist_date_object['day']}/{anilist_date_object['month']}/{anilist_date_object['year']}" 
    else:
        return "Unknown" 
    
def format_anilist_timestamp(anilist_timestamp:int|None):
    if anilist_timestamp:
        return datetime.fromtimestamp(anilist_timestamp).strftime("%d/%m/%Y %H:%M:%S") 
    else:
        return "Unknown"

def format_list_data_with_comma(data:list|None):
    if data:
        return ", ".join(data)
    else:
        return "None"