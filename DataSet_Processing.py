import numpy as np
import pandas as pd

def assignCat(ranges, avg_stats):
  if avg_stats > ranges[5]:
    return 1
  elif avg_stats < ranges[5] and avg_stats > ranges[4]:
    return 2
  elif avg_stats < ranges[4] and avg_stats > ranges[3]:
    return 3
  elif avg_stats < ranges[3] and avg_stats > ranges[2]:
    return 4
  elif avg_stats < ranges[2] and avg_stats > ranges[1]:
    return 5
  elif avg_stats < ranges[1]:
    return 6

def processDataSet():
    data = pd.read_csv("data.csv")

    data['avg_stats'] = data.select_dtypes(include=[np.number]).apply(lambda row: (row['avg_score'] + row['avg_game_pieces_score'] + row['avg_links_points'] + row['avg_charge_station'])/4, axis=1)

    summary = data.describe()

    max_value = summary["avg_stats"].loc['max']
    min_value = summary["avg_stats"].loc['min']

    ranges = np.linspace(min_value, max_value, 7).tolist()

    data['rbt_category'] = data.select_dtypes(include=[np.number]).apply(lambda row: assignCat(ranges,row['avg_stats']) , axis=1)

    mask = data['avg_score'] == 0

    # Apply the mask to filter out rows with 0 values
    df = data[~mask]

  
    data.to_csv('p_data.csv', index=False)
    #df.to_csv('p2_data.csv', index=False)
