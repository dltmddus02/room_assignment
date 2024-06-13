import pandas as pd
# import os
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import font
import calculatePriority
import roomAssignBySex
import getTable
import roomList
import getRoommateInfo
import traceback

root = Tk()
root.title("곤자가 방배정 프로그램")

frame1 = Frame(root)
frame1.pack(side='left')
frame2 = Frame(root)
frame2.pack(side='left', padx=20)

file_frame = Frame(frame1)
file_frame.pack(fill="x", padx=5, pady=5)

table_frame = Frame(frame1)
table_frame.pack(fill='x', padx=5, pady=5)

root.geometry("1600x480")
root.resizable(False, False)

selected_file_path = None
selected_roommate_file_path = None
global combined_df, result_df
# 2024만 사용할 입주기간 불러오기 위한 df

class roommatesException(Exception):
    pass

def file_select():
    global selected_file_path, combined_df, female_df, male_df, result_df
    selected_file_path = filedialog.askopenfilename(initialdir="/", title="파일을 선택 해 주세요.")
    if selected_file_path == '':
        messagebox.showwarning("경고", "파일을 선택 하세요.")
    else:
        print("선택된 파일 :", selected_file_path)
        result_df = pd.read_excel(selected_file_path)

        # 사전작업
        result_df = calculatePriority.preprocessing(result_df)
        
        # # 여자 + 남자
        # combined_df = pd.concat([female_df, male_df], ignore_index=True)
        
        # 표 배치하기
        getTable.dataframe_to_table(result_df)
        
        # 방 상태 표 배치하기
        getTable.dataframe_to_room_state_table()

def roommate_file_select():
    global selected_file_path, selected_roommate_file_path, female_df, male_df, result_df, combined_df
    selected_roommate_file_path = filedialog.askopenfilename(initialdir="/", title="파일을 선택 해 주세요.")
    if selected_roommate_file_path == '':
        messagebox.showwarning("경고", "파일을 선택 하세요.")
    else:
        print("선택된 파일 :", selected_roommate_file_path)
        roommate_df = pd.read_excel(selected_roommate_file_path)

        # 룸메 계산
        modified_df = getRoommateInfo.write_roommate_ID(result_df, roommate_df)

        # 사전작업
        female_df, male_df = calculatePriority.roommate_preprocessing(modified_df)
        
        # 여자 + 남자
        combined_df = pd.concat([female_df, male_df], ignore_index=True)
        
        # 표 배치하기
        getTable.dataframe_to_table(combined_df)
        
        # 방 상태 표 배치하기
        getTable.dataframe_to_room_state_table()



def assign():
    global combined_df, female_df, male_df
    try:
        if combined_df is not None:
            # print("!!!!!!!!-------")
            
            # 1. 여자
            female_modified_df = roomAssignBySex.assign(female_df)
            
            # 2. 남자
            male_modified_df = roomAssignBySex.assign(male_df)

            # 여자 + 남자
            combined_df = pd.concat([female_df, male_df], ignore_index=True)
            
            # 표 배치하기
            getTable.dataframe_to_table(combined_df)
            
            # 방 상태 표 배치하기
            getTable.dataframe_to_room_state_table()
            
            
    except Exception as e:
        trace_back = traceback.format_exc()
        message = str(e)+ "\n" + str(trace_back)

        print('[FAIL] %s', message)
        messagebox.showwarning("경고", "먼저 파일을 선택하고 수정하세요.")
            

def save_file():
    global combined_df, male_modified_df
    try:
        if combined_df is not None:
            for room_number in list(roomList.room_numbers_A_map.keys()):
                if len(roomList.room_numbers_A_map[room_number]) > 2:
                    raise roommatesException(str(room_number))
            for room_number in list(roomList.room_numbers_B_map.keys()):
                if len(roomList.room_numbers_B_map[room_number]) > 2:
                    raise roommatesException(str(room_number))
            
            save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
            if save_path:
                combined_df.to_excel(save_path, index=False)
                messagebox.showinfo("알림", "파일이 저장되었습니다.")
    except roommatesException as e:
        messagebox.showwarning("경고", f"{e}의 배정인원이 2명 이상입니다.")
    except Exception as E:
        print(E)
        messagebox.showwarning("경고", "먼저 파일을 선택하고 수정하세요.")


# 버튼 배치
button_label = Label(file_frame)
button_label.pack(fill='x', padx=20, pady=10)

btn_select_file = Button(button_label, text="파일 선택", width=12, padx=5, pady=5, command=file_select)
btn_select_file.pack(padx=5, pady=5, side='left')

btn_save_file = Button(button_label, text="파일 저장", width=12, padx=5, pady=5, command=save_file)
btn_save_file.pack(padx=5, pady=5, side='left')

btn_assign = Button(button_label, text="배정하기", width=12, padx=5, pady=5, command=assign)
btn_assign.pack(padx=5, pady=5, side='left')

btn_assign = Button(button_label, text="룸메 파일 선택", width=12, padx=5, pady=5, command=roommate_file_select)
btn_assign.pack(padx=5, pady=5, side='left')


spacer = Label(button_label, text="")
spacer.pack(side='left', padx=20)

# 수정 기능 배치
spacer = Label(button_label, text="")
spacer.pack(side='left', padx=10)

# 수정 기능 학번 entry 배치
edit_student_id_entry = Entry(button_label, width=24, font=font.Font(family="맑은 고딕", size=12))
edit_student_id_entry.pack(side='left', ipady=5)

def focus_in_student_id(*args):
    if edit_student_id_entry.get() == "수정할 학번을 입력하세요":
        edit_student_id_entry.delete(0, "end")
        edit_student_id_entry.configure(fg="black")

def focus_out_student_id(*args):
    if not edit_student_id_entry.get():
        edit_student_id_entry.configure(fg="gray")
        edit_student_id_entry.insert(0, "수정할 학번을 입력하세요")

focus_out_student_id()
edit_student_id_entry.bind("<FocusIn>", focus_in_student_id)
edit_student_id_entry.bind("<FocusOut>", focus_out_student_id)

# 수정 기능 방번호 entry 배치
edit_room_number_entry = Entry(button_label, width=24, font=font.Font(family="맑은 고딕", size=12))
edit_room_number_entry.pack(side='left', ipady=5, padx=5)

def focus_in_room_number(*args):
    if edit_room_number_entry.get() == "변경할 방번호를 입력하세요":
        edit_room_number_entry.delete(0, "end")
        edit_room_number_entry.configure(fg="black")

def focus_out_room_number(*args):
    if not edit_room_number_entry.get():
        edit_room_number_entry.configure(fg="gray")
        edit_room_number_entry.insert(0, "변경할 방번호를 입력하세요")

focus_out_room_number()
edit_room_number_entry.bind("<FocusIn>", focus_in_room_number)
edit_room_number_entry.bind("<FocusOut>", focus_out_room_number)

def handle_edit():
    global combined_df
    try:
        getTable.edit(edit_student_id_entry.get(), edit_room_number_entry.get(), combined_df)
    except:
        messagebox.showwarning("경고", "먼저 파일을 선택하고 수정하세요.")

btn_edit = Button(button_label, text="수정하기", width=12, padx=5, pady=5, command = handle_edit)
btn_edit.pack(padx=5, pady=5, side='left',)


# 검색바 배치
search_label = Label(file_frame)
search_label.pack(fill='x', padx=20, pady=10)

def handle_search():
    global combined_df
    try:
        getTable.search(search_entry.get(), combined_df)
    except:
        messagebox.showwarning("경고", "먼저 파일을 선택하고 수정하세요.")

search_entry = Entry(search_label, width=100, font=font.Font(family="맑은 고딕", size=14))
search_button = Button(
    search_label,
    text='검색하기',
    width=20,
    padx=5,
    pady=5,
    command= handle_search
)

search_entry.pack(side='left', ipady=3)
search_button.pack(side='right')


# 표들 배치
getTable.make_table(table_frame)
getTable.make_room_state_table(frame2)

root.mainloop()