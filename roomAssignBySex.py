import pandas as pd
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import calculatePriority
import roomAssignment

def assign(df):
        roomAssignment.singles_df = pd.DataFrame()

        # 1-1. 국적 우선순위
        want_same_nationality_df, regardless_of_nationality_df, modified_df = calculatePriority.group_by_nationality(df)

        # 1-2. 활동형 우선순위
        # 국적 선호하는 사람들 묶어서 활동형으로 분류
        morning_A_df, night_A_df = calculatePriority.group_by_activity_type(want_same_nationality_df)
        # 국적 상관 없는 사람들 묶어서 활동형으로 분류
        morning_B_df, night_B_df = calculatePriority.group_by_activity_type(regardless_of_nationality_df)

        # 1-3 흡연 우선순위
        # 국적 선호하는 사람들 중, 아침 저녁 나누고 또 각각을 흡연 비흡연 나눔
        morning_smoking_A_df, morning_not_smoking_A_df, night_smoking_A_df, night_not_smoking_A_df = calculatePriority.group_by_smoke_type(morning_A_df, night_A_df)
        # 국적 상관없는 사람들 중, 아침 저녁 나누고 또 각각을 흡연 비흡연 나눔
        morning_smoking_B_df, morning_not_smoking_B_df, night_smoking_B_df, night_not_smoking_B_df = calculatePriority.group_by_smoke_type(morning_B_df, night_B_df)
        
        # 1-4 나이순으로 방배정
        modified_df = roomAssignment.room_assign_in_pairs(modified_df, calculatePriority.group_by_age(morning_smoking_A_df))
        modified_df = roomAssignment.room_assign_in_pairs(modified_df, calculatePriority.group_by_age(morning_not_smoking_A_df))
        modified_df = roomAssignment.room_assign_in_pairs(modified_df, calculatePriority.group_by_age(night_smoking_A_df))
        modified_df = roomAssignment.room_assign_in_pairs(modified_df, calculatePriority.group_by_age(night_not_smoking_A_df))

        modified_df = roomAssignment.room_assign_in_pairs(modified_df, calculatePriority.group_by_age(morning_smoking_B_df))
        modified_df = roomAssignment.room_assign_in_pairs(modified_df, calculatePriority.group_by_age(morning_not_smoking_B_df))
        modified_df = roomAssignment.room_assign_in_pairs(modified_df, calculatePriority.group_by_age(night_smoking_B_df))
        modified_df = roomAssignment.room_assign_in_pairs(modified_df, calculatePriority.group_by_age(night_not_smoking_B_df))

        singles = roomAssignment.singles_df
        # print(singles)

        modified_df = roomAssignment.room_assign_in_singles(modified_df, singles)

        return modified_df