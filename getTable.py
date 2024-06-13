import pandas as pd
import os
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import roomList
import roomAssignment

columns = ['생년월일', '학번', '성명', '성별', '학과(부)', '활동형', '흡연여부', ' 청소', ' 선호국적', '국적', '방배정']

def make_table(frame):
    global treeview
    scrollbar_x = Scrollbar(frame, orient='h')
    scrollbar_y = Scrollbar(frame, orient='v')
    scrollbar_x.pack(side="bottom", fill='x')
    scrollbar_y.pack(side="right", fill='y')
    
    headings = list(columns)
    treeview=ttk.Treeview(
        frame,
        height=200,
        columns=headings,
        displaycolumns=headings,
        xscrollcommand=scrollbar_x.set,
        yscrollcommand=scrollbar_y.set
    )
    treeview.pack(side='bottom')
    
    treeview.column('#0', width=50)
    treeview.heading('#0', text="num")
    for i in range(len(headings)):
        treeview.column(f'#{i+1}', width=100)
        treeview.heading(f'#{i+1}', text=headings[i])
        
    scrollbar_x["command"] = treeview.xview
    scrollbar_y["command"] = treeview.yview
    

def dataframe_to_table(df):
    global treeview
    modified_df = df.loc[:, columns]
    
    for row in treeview.get_children():
        treeview.delete(row)
    
    for idx, row in modified_df.iterrows():
        _row = tuple(row)
        treeview.insert('', 'end', text=idx, values=_row, iid=str(idx)+"번")



def search(search_text, df):
    selected_df = pd.DataFrame(columns = columns)
    try:
        if df is not None:
            if search_text == "흡연":
                selected_df = df.loc[df["흡연여부"] == '흡연', :]
            else:
                for c in columns:
                    df[c] = df[c].apply(str)
                    temp_df = df.loc[df[c].str.contains(search_text), :]
                    selected_df = pd.concat([selected_df, temp_df], ignore_index=True)
            selected_df = selected_df.drop_duplicates(subset = ['학번'])
            dataframe_to_table(selected_df)
        
    except:
        messagebox.showwarning("경고", "먼저 파일을 선택하고 수정하세요.")


def edit(student_id, room_number, df):
    student = df.loc[df["학번"] == student_id, :].squeeze()
    try:
        if student.empty:
            raise Exception("존재하지 않는 학번입니다.")
        
        if student['방배정'] in list(roomList.room_numbers_A_map.keys()):
            if room_number not in list(roomList.room_numbers_A_map.keys()):
                raise Exception("성별과 방번호를 확인해 주십시오.")
            if student["방배정"] is not None and student["학번"] in roomList.room_numbers_A_map[student["방배정"]]:
                roomList.room_numbers_A_map[student["방배정"]].remove(student["학번"])
            roomList.room_numbers_A_map[room_number].append(student["학번"])
        elif student['방배정'] in list(roomList.room_numbers_B_map.keys()):
            if room_number not in list(roomList.room_numbers_B_map.keys()):
                raise Exception("성별과 방번호를 확인해 주십시오.")
            if student["방배정"] is not None and student["학번"] in roomList.room_numbers_B_map[student["방배정"]]:
                roomList.room_numbers_B_map[student["방배정"]].remove(student["학번"])
            roomList.room_numbers_B_map[room_number].append(student["학번"])
        else:
            raise Exception("존재하지 않는 방번호입니다.")
        
        
        df.loc[df["학번"] == student_id, "방배정"] = room_number
        
        dataframe_to_table(df.loc[df["방배정"] == room_number])
        dataframe_to_room_state_table()
        
    except Exception as e:
        messagebox.showwarning("경고", e)
    
    
def make_room_state_table(frame):
    global treeview2
    scrollbar_y = Scrollbar(frame, orient='v')
    scrollbar_y.pack(side="right", fill='y')
    
    headings = list(['방배정', '학번'])
    treeview2=ttk.Treeview(
        frame,
        height=200,
        columns=headings,
        displaycolumns=headings,
        yscrollcommand=scrollbar_y.set,
        show='headings',
        
    )
    treeview2.pack(pady=10)
    
    treeview2.column('#1', width=150)
    treeview2.heading('#1', text='방배정')
    treeview2.column('#2', width=150)
    treeview2.heading('#2', text='학번')
    
    scrollbar_y["command"] = treeview2.yview
    
    dataframe_to_room_state_table()
    
    
def dataframe_to_room_state_table():
    global treeview2
    
    for row in treeview2.get_children():
        treeview2.delete(row)
        
    for idx, room_number in enumerate(roomList.room_numbers_A_map.keys()):
        roommates = roomList.room_numbers_A_map[room_number]
        
        if not roommates:
            treeview2.insert('', 'end', values=tuple([room_number, None]), tags=room_number)
            
        else:
            for roommate in roommates:
                treeview2.insert('', 'end', values=tuple([room_number, roommate]), tags=room_number)
        
        if roomAssignment.is_room_for_disabled(room_number):    # 장애인 전용 방일 경우 노란색으로 표시
            treeview2.tag_configure(room_number, background= '#FEC345')
        elif len(roommates)==1:   # 여자 1명만 배정된 경우 붉은색으로 표시
            treeview2.tag_configure(room_number, background= '#B60005')
        elif(idx%2==0):
            treeview2.tag_configure(room_number, background= '#FFFFFF')
        else:
            treeview2.tag_configure(room_number, background= '#F7F8F9')
        
    room_numbers_A_len = len(roomList.room_numbers_A_map.keys())
    
    for idx2, room_number in enumerate(roomList.room_numbers_B_map.keys()):
        roommates = roomList.room_numbers_B_map[room_number]
        # print(room_number, roommates)
        
        if not roommates:
            treeview2.insert('', 'end', values=tuple([room_number, None]), tags=room_number)
            
        else:
            for roommate in roommates:
                treeview2.insert('', 'end', values=tuple([room_number, roommate]), tags=room_number)
        
        if roomAssignment.is_room_for_disabled(room_number):    # 장애인 전용 방일 경우 노란색으로 표시
            treeview2.tag_configure(room_number, background= '#FEC345')
        elif len(roommates)==1:   # 남자 1명만 배정된 경우 붉은색으로 표시
            treeview2.tag_configure(room_number, background= '#B60005')
        elif((room_numbers_A_len + idx2)%2==0):
            treeview2.tag_configure(room_number, background= '#FFFFFF')
        else:
            treeview2.tag_configure(room_number, background= '#F7F8F9')
        