import pandas as pd

def write_roommate_ID(df, roommate_df):
    if '룸메이트' not in df.columns:
        df['룸메이트'] = ''     # df['룸메이트'] = df['룸메이트'].astype(str)  # '룸메이트' 열을 문자열로 변환

    for idx, row in roommate_df.iterrows():

        student_id = str(row['학번'])
        roommate_id = str(row['희망 룸메이트 학번'])
        if (roommate_id in df['학번'].values) & (student_id in df['학번'].values):
            student_row = df.loc[df['학번'] == student_id]
            roommate_row = df.loc[df['학번'] == roommate_id]
            
            df.loc[student_row.index, '룸메이트'] = (roommate_id)
            df.loc[roommate_row.index, '룸메이트'] = (student_id)
    # df['룸메이트'] = df['룸메이트'].astype(str)

    return df