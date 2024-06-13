import pandas as pd
import roomList
import random
from datetime import datetime

singles_df = pd.DataFrame()

def add_room_assignment_column(df):
    df['방배정'] = None
    return df

def calculate_age(birthdate):
    birthdate = str(birthdate)
    try:
        if len(birthdate) != 6:
            birthdate = '0' * (6 - len(birthdate)) + birthdate  # 앞에 0을 채워 6자리로 만듦
            # print(birthdate)

        today = datetime.today()
        birthdate = datetime.strptime(birthdate, "%y%m%d")
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        # print(type(age))
        return age
    except ValueError:
        return None

def add_age_column(df):
    df['나이'] = df['생년월일'].apply(calculate_age)
    df['나이'].fillna(20, inplace=True)
    return df

def add_nationality_column(df):
    df[' 선호국적'].fillna('상관없음', inplace=True)
    df['국적'].fillna('Foreign', inplace=True)
    return df

def add_activity_column(df):
    df['활동형'].fillna('아침형', inplace=True)
    return df

def add_smoke_column(df):
    df['흡연여부'].fillna('비흡연', inplace=True)
    return df


assigned_room_female = []
assigned_room_male = []

# 장애인 전용 방인지 확인
def is_room_for_disabled(room_number):
    room_number_int = int(room_number[1:])
    if(room_number in roomList.room_numbers_A):
        # 여자 장애인 전용 방
        if(room_number_int // 100 <= 4):
            if((room_number_int % 100 == 19 or room_number_int % 100 == 21)):
                return True
        else:
            if(room_number_int % 100 == 21):
                return True
        return False
    else:
        # 남자 장애인 전용 방
        if(room_number_int % 100 == 60):
            return True
        return False
    
    
# 중국인 전용 층인지 확인
def is_room_for_chinese(room_number):
    room_number_int = int(room_number[1:])
    if(room_number_int%100 == 10 or room_number_int%100 == 11):
        return True
    return False

# 둘다 중국인일 경우 제일 위층부터 배정
index_female_chinese = len(roomList.room_numbers_A_map.keys()) -1
index_male_chinese = len(roomList.room_numbers_B_map.keys()) -1
def room_assign_chinese(df, group):
    global assigned_room_female, assigned_room_male, index_female_chinese, index_male_chinese
    if(group['성별'] == 'Female').all():
        room_number_female = list(roomList.room_numbers_A_map.keys())[index_female_chinese]
        while(room_number_female in assigned_room_female or is_room_for_disabled(room_number_female)):
            if index_female_chinese == index_female_high:
                return room_assign_semester(df, group)
            index_female_chinese = index_female_chinese - 1
            room_number_female = list(roomList.room_numbers_A_map.keys())[index_female_chinese]
        assigned_room_female.append(room_number_female)
        df.loc[group.index, '방배정'] = room_number_female
        roomList.room_numbers_A_map[room_number_female] = list(group['학번'])
    else:
        room_number_male = list(roomList.room_numbers_B_map.keys())[index_male_chinese]
        while(room_number_male in assigned_room_male or is_room_for_disabled(room_number_male)):
            if index_male_chinese ==index_male_high:
                return room_assign_semester(df, group)
            index_male_chinese = index_male_chinese - 1
            room_number_male = list(roomList.room_numbers_B_map.keys())[index_male_chinese]
        assigned_room_male.append(room_number_male)
        df.loc[group.index, '방배정'] = room_number_male
        roomList.room_numbers_B_map[room_number_male] = list(group['학번'])
        
    return df
    
    

# 1학기 거주자들 제외 7층부터 배정
index_female_high = 166
index_male_high = 75
def room_assign(df, group):
    global assigned_room_female, assigned_room_male, index_female_high, index_male_high
    if(group['성별'] == 'Female').all():
        room_number_female = list(roomList.room_numbers_A_map.keys())[index_female_high]
        while(room_number_female in assigned_room_female or is_room_for_disabled(room_number_female)):
            if index_female_high == 281:
                return room_assign_semester(df, group)
            index_female_high = index_female_high + 1
            room_number_female = list(roomList.room_numbers_A_map.keys())[index_female_high]
        assigned_room_female.append(room_number_female)
        df.loc[group.index, '방배정'] = room_number_female
        roomList.room_numbers_A_map[room_number_female] = list(group['학번'])
    else:
        room_number_male = list(roomList.room_numbers_B_map.keys())[index_male_high]
        while(room_number_male in assigned_room_male or is_room_for_disabled(room_number_male)):
            if index_male_high == 164:
                return room_assign_semester(df, group)
            index_male_high = index_male_high + 1
            room_number_male = list(roomList.room_numbers_B_map.keys())[index_male_high]
        assigned_room_male.append(room_number_male)
        df.loc[group.index, '방배정'] = room_number_male
        roomList.room_numbers_B_map[room_number_male] = list(group['학번'])

    return df


# 1학기 거주자들 저층 배정
index_female_low = 0
index_male_low = 0
def room_assign_semester(df, group):
    global assigned_room_female, assigned_room_male, index_female_low, index_male_low, index_female_high, index_male_high, index_female_chinese, index_male_chinese
    if(group['성별'] == 'Female').all():
        room_number_female = list(roomList.room_numbers_A_map.keys())[index_female_low]
        while(room_number_female in assigned_room_female or is_room_for_disabled(room_number_female)):
            if index_female_low >= index_female_high and index_female_low >= index_female_chinese:
                return df
                raise Exception("여자 방이 가득 찼습니다!")
            index_female_low = index_female_low + 1
            room_number_female = list(roomList.room_numbers_A_map.keys())[index_female_low]
        assigned_room_female.append(room_number_female)
        df.loc[group.index, '방배정'] = room_number_female
        roomList.room_numbers_A_map[room_number_female] = list(group['학번'])
    else:
        room_number_male = list(roomList.room_numbers_B_map.keys())[index_male_low]
        while(room_number_male in assigned_room_male or is_room_for_disabled(room_number_male)):
            if index_male_low >= index_male_high and index_male_low >= index_male_chinese:
                return df
                raise Exception("남자 방이 가득 찼습니다!")
            index_male_low = index_male_low + 1
            room_number_male = list(roomList.room_numbers_B_map.keys())[index_male_low]
        assigned_room_male.append(room_number_male)
        df.loc[group.index, '방배정'] = room_number_male
        roomList.room_numbers_B_map[room_number_male] = list(group['학번'])

    return df

def room_assign_in_roommate(df, group):
    if group['국적'].str.contains('China').all():
        return room_assign_chinese(df, group)
    elif group['입주기간'].str.contains('1학기').any():
        return room_assign_semester(df, group)
    else:
        return room_assign(df, group)


def room_assign_in_pairs(modified_df, df):
    global singles_df
    if df.empty:
        return modified_df
    unassigned_df = df[df['방배정'].isnull()]
    if len(unassigned_df) % 2 == 1:
        singles_df = pd.concat([singles_df, unassigned_df.iloc[-1:]])
        unassigned_df = unassigned_df.iloc[:-1]

    for i in range(0, len(unassigned_df), 2):
        group = unassigned_df.iloc[i:i+2]
        if group['국적'].str.contains('China').all():
            # print("중국인 배정")
            modified_df = room_assign_chinese(modified_df, group)
        elif group['입주기간'].str.contains('1학기').any():
            # print("저층 배정")
            modified_df = room_assign_semester(modified_df, group)
        else:
            # print("걍 배정")
            modified_df = room_assign(modified_df, group)
    return modified_df

def room_assign_in_singles(modified_df, df):
    
    if df.empty:
        return modified_df
    for i in range(0, len(df), 2):
        group = df.iloc[i:i+2]
        modified_df = room_assign(modified_df, group)    
    return modified_df
    