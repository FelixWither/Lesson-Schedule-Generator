# -*-coding:utf-8-*-
import re
import datetime
import sys
import os


conf_sequences = [{}]
weekOne: datetime.datetime


def str_to_weekday(str):
    class Weekday:
        monday = weekOne - datetime.timedelta(days=weekOne.weekday())
        tuesday = weekOne - datetime.timedelta(days=weekOne.weekday() - 1)
        wednesday = weekOne - datetime.timedelta(days=weekOne.weekday() - 2)
        thursday = weekOne - datetime.timedelta(days=weekOne.weekday() - 3)
        friday = weekOne - datetime.timedelta(days=weekOne.weekday() - 4)
        saturday = weekOne - datetime.timedelta(days=weekOne.weekday() - 5)
        sunday = weekOne - datetime.timedelta(days=weekOne.weekday() - 6)
    if str == '周一':
        return Weekday.monday
    elif str == '周二':
        return Weekday.tuesday
    elif str == '周三':
        return Weekday.wednesday
    elif str == '周四':
        return Weekday.thursday
    elif str == '周五':
        return Weekday.friday
    elif str == '周六':
        return Weekday.saturday
    elif str == '周日':
        return Weekday.sunday


def string_to_relative_date(str):
    date = str.split(" ")
    date[1] = date[1].split(":")
    hrs = datetime.timedelta(hours=int(date[1][0])) + datetime.timedelta(minutes=int(date[1][1]))
    date = str_to_weekday(date[0]) + hrs
    return date


def string_to_abs_date(str):
    date = str.split(" ")
    date[0] = date[0].split("-")
    date[1] = date[1].split(":")

    hrs = datetime.timedelta(hours=int(date[1][0])) + datetime.timedelta(minutes=int(date[1][1]))
    date = datetime.datetime(int(date[0][0]), int(date[0][1]), int(date[0][2])) + hrs
    return date


def formatString(str):
    return str.replace(" ", "").replace("\n", "").replace(";", " ")


def formatData(str):
    space_end_index = re.match(r'( *)', str).end()
    return str[space_end_index:]

repeat_count = 0
last_course_name = ''


def add_extra_schedule(add_at, dic_tag, with_data):
    for count in range(0, repeat_count, 1):
        conf_sequences[add_at + count + 1][dic_tag] = with_data


def switch(on_data, add_at, with_data):
    global weekOne
    global conf_sequences
    global repeat_count
    global last_course_name
    if on_data == "课程名称":
        with_data = formatData(with_data)
        conf_sequences[add_at]["subject"] = with_data
        last_course_name = with_data
    elif on_data == "开始时间":
        with_data = formatString(with_data)
        time_slots = with_data.split(",")
        conf_sequences[add_at]["day_to_start"] = string_to_relative_date(time_slots[0])
        if len(time_slots) > 1:
            repeat_count = len(time_slots) - 1
            for count in range(0, repeat_count, 1):
                conf_sequences.append(
                    {"subject": "%s" % last_course_name, "day_to_start": string_to_relative_date(time_slots[count + 1])})
    elif on_data == "结束时间":
        with_data = formatString(with_data)
        time_slots = with_data.split(",")
        conf_sequences[add_at]["day_to_end"] = string_to_relative_date(time_slots[0])
        if len(time_slots) > 1:
            for count in range(0, repeat_count, 1):
                conf_sequences[add_at + count + 1]["day_to_end"] = string_to_relative_date(time_slots[count + 1])
    elif on_data == "课程描述":
        with_data = formatData(with_data)
        conf_sequences[add_at]["description"] = with_data
        if repeat_count > 0:
            add_extra_schedule(add_at, "description", with_data)
    elif on_data == "教室":
        with_data = formatData(with_data)
        conf_sequences[add_at]["class_room"] = with_data
        if repeat_count > 0:
            add_extra_schedule(add_at, "class_room", with_data)
    elif on_data == "授课教师":
        with_data = formatData(with_data)
        conf_sequences[add_at]["teacher"] = with_data
        if repeat_count > 0:
            add_extra_schedule(add_at, "teacher", with_data)
    elif on_data == "教师邮箱":
        with_data = formatData(with_data)
        conf_sequences[add_at]["email_addr"] = with_data
        if repeat_count > 0:
            add_extra_schedule(add_at, "email_addr", with_data)
    elif on_data == "课程周数":
        with_data = formatString(with_data)
        conf_sequences[add_at]["class_length"] = int(with_data)
        if repeat_count > 0:
            add_extra_schedule(add_at, "class_length", int(with_data))
    elif on_data == "不重复周数":
        with_data = formatString(with_data)
        counter = 0
        splitArray = with_data.split(",")
        for num_in_string in splitArray:
            try:
                splitArray[counter] = int(num_in_string)
            except:
                splitArray = []
                break
            counter += 1
        conf_sequences[add_at]["except_week"] = splitArray
        if repeat_count > 0:
            add_extra_schedule(add_at, "except_week", with_data=splitArray)
    elif on_data == "提前多少分钟提醒":
        with_data = formatString(with_data)
        conf_sequences[add_at]["remind_before"] = int(with_data)
        if repeat_count > 0:
            add_extra_schedule(add_at, "remind_before", int(with_data))
    elif on_data == "lesson_end":
        return "end"
    elif on_data == "lesson_start":
        conf_sequences.append({})
    elif on_data == "日历名称":
        with_data = formatData(with_data)
        conf_sequences[0]["cal_name"] = "%s" % with_data
    elif on_data == "学期开始时间":
        with_data = formatString(with_data)
        conf_sequences[0]["sem_start_date"] = string_to_abs_date(with_data)
        weekOne = string_to_abs_date(with_data)
    else:
        return


def strip_comment(str):
    comment_start = str.find("//")
    if comment_start is not None:
        return str[0:comment_start]
    else:
        return str


counter = 1


def parse():
    global counter
    global repeat_count
    if getattr(sys, 'frozen', False):
        absPath = os.path.dirname(os.path.abspath(sys.executable))
    elif __file__:
        absPath = os.path.dirname(os.path.abspath(__file__))
    file = open(absPath + '/课表配置.txt', 'r')
    line = file.readline()
    while line:
        line = strip_comment(line)
        matched = re.match(r'(.*)[\u4e00-\u9fa5]:', line)
        if matched is None:
            line = line.replace(":", "")
            if re.match(r'(.*)[a-z]', line) is not None:
                if switch(re.match(r'(.*)[a-z]', line).group(), counter, "") == "end":
                    counter += 1 + repeat_count
                    repeat_count = 0
            line = file.readline()
        else:
            data = line.strip(matched.group())
            line = file.readline()
            matched = matched.group().strip(':')
            switch(matched, counter, data)
    file.close()
    return conf_sequences


if __name__ == "__main__":
    parse()
