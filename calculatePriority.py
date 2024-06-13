import pandas as pd
import roomAssignment
import calculatePriority
import roomList

def preprocessing(df):
    # '방배정'열 추가하기
    df = roomAssignment.add_room_assignment_column(df)
    # '나이'열 추가하기 (생일 이상한 사람들은 20이라고 초기화함)
    df = roomAssignment.add_age_column(df)
    # '국적' 상관없음, Korea 작성하기
    df = roomAssignment.add_nationality_column(df)
    # '활동형' 아침형 작성하기
    df = roomAssignment.add_activity_column(df)
    # '흡연여부' 비흡연 작성하기
    df = roomAssignment.add_smoke_column(df)
    return df


def roommate_preprocessing(df):
    # 룸메이트 우선 배정하기
    df = calculatePriority.predesigned_roommates(df)
    # 성별로 엑셀 나누기
    female_df, male_df = calculatePriority.group_by_sex(df)
    return female_df, male_df



def predesigned_roommates(df):
    roommate_rows = df.dropna(subset=['룸메이트'])
    myset = set()
    group = None
    for _, row1 in roommate_rows.iterrows():
        student_number1 = row1['학번']
        roommate_number1 = row1['룸메이트']
        for _, row2 in roommate_rows.iterrows():
            student_number2 = row2['학번']
            roommate_number2 = row2['룸메이트']
            if (student_number1) == (roommate_number2) and (roommate_number1) == (student_number2) and (student_number1) not in myset:
                myset.add((student_number2))
                myset.add((roommate_number2))
                group = df[(df['학번'] == student_number2) | (df['학번'] == student_number1)]
                df = roomAssignment.room_assign_in_roommate(df, group)
    return df

def group_by_sex(df):
    grouped = df.groupby('성별')

    female_df = None
    male_df = None

    for group_name, group_data in grouped:
        if group_name == 'Female':
            female_df = group_data.copy()
        else:
            male_df = group_data.copy()

    return female_df, male_df

def group_by_nationality(df):
    grouped = df.groupby('국적')

    want_same_nationality_groups = []
    regardless_of_nationality_groups = []
    for nationality, group in grouped:
        group = group[['학번', '성명', '성별', '국적', ' 선호국적', '활동형', '흡연여부', '방배정', '생년월일', '나이', '입주기간']]
        if len(group) >= 5 or len(group) == 3:
            # 인원 수가 3명 이상일 경우 '같은국적', '상관없음' 나누기
            same_nationality_group = group[group[' 선호국적'] == '같은국적']
            # regardless_of_nationality_group = group[(group['선호국적'] == '상관없음') | (group['선호국적'] == '다른국적')]
            regardless_of_nationality_group = group[group[' 선호국적'] != '같은국적']

            want_same_nationality_groups.append(same_nationality_group)
            regardless_of_nationality_groups.append(regardless_of_nationality_group)
        elif len(group) == 4:
            for i in range(0, len(group), 2):
                subgroup = group.iloc[i:i+2]
                modified_df = roomAssignment.room_assign(df, subgroup)
        elif len(group) == 2:
            # 딱 두 명일 경우, 그 두 명 배정하기
            modified_df = roomAssignment.room_assign(df, group)
        else:
            # 같은 국적인 사람 없는 경우
            regardless_of_nationality_groups.append(group)

    want_same_nationality_df = pd.concat(want_same_nationality_groups)
    regardless_of_nationality_df = pd.concat(regardless_of_nationality_groups)
    return want_same_nationality_df, regardless_of_nationality_df, modified_df

def group_by_activity_type(df):
    grouped = df.groupby('활동형')
    morning_df = grouped.get_group('아침형')
    night_df = grouped.get_group('저녁형')

    # print(len(morning_df))
    # print(len(night_df))
    return morning_df, night_df

def group_by_smoke_type(morning_df, night_df):
    try:
        morning_grouped = morning_df.groupby('흡연여부')
        morning_smoking_df = morning_grouped.get_group('흡연')
        morning_not_smoking_df = morning_grouped.get_group('비흡연')
    except KeyError:
        # '흡연' 열이 없는 경우에 대한 예외 처리
        morning_smoking_df = pd.DataFrame()
        morning_not_smoking_df = morning_df
    
    try:
        night_grouped = night_df.groupby('흡연여부')
        night_smoking_df = night_grouped.get_group('흡연')
        night_not_smoking_df = night_grouped.get_group('비흡연')
    except KeyError:
        # '흡연' 열이 없는 경우에 대한 예외 처리
        night_smoking_df = pd.DataFrame()
        night_not_smoking_df = night_df
    return morning_smoking_df, morning_not_smoking_df, night_smoking_df, night_not_smoking_df

def group_by_age(df):
    if df.empty:
        return df
    # 한 명씩 남으면 따로 singles 배열로 빼자.
    df = df.sort_values(by='나이')
    return df