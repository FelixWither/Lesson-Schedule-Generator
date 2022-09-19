# -*-coding:utf-8-*-
import datetime
import sys
from os import path
from os import system
from os import name as os_name
from uuid import uuid4

weekOne: datetime.datetime


def day(day, time):
    splitTime = time.split(":")
    hour = int(splitTime[0])
    minute = int(splitTime[1])
    return day.value + datetime.timedelta(hours=hour) + datetime.timedelta(minutes=minute)


class Event:
    """
    事件对象
    """

    def __init__(self, kwargs, remind_before):
        self.event_data = kwargs
        self.remind_before = remind_before

    def __turn_to_string__(self):
        self.event_text = "BEGIN:VEVENT\n"
        for item, data in self.event_data.items():
            item = str(item).replace("_", "-")
            if item not in ["ORGANIZER", "DTSTART", "DTEND"]:
                self.event_text += "%s:%s\n" % (item, data)
            else:
                self.event_text += "%s;%s\n" % (item, data)
        if self.remind_before > 0:
            self.event_text += "BEGIN:VALARM\n"
            self.alarm_uuid = uuid4()
            self.event_text += "X-WR-ALARMUID:%s\n" % self.alarm_uuid
            self.event_text += "UID:%s\n" % self.alarm_uuid
            self.event_text += "TRIGGER:-PT%sM\n" % self.remind_before
            self.event_text += "ATTACH;VALUE=URI:Chord\n"
            self.event_text += "ACTION:AUDIO\n"
            self.event_text += "END:VALARM\n"
        self.event_text += "END:VEVENT\n"
        return self.event_text


class Calendar:
    """
    日历对象
    """

    def __init__(self, calendar_name="My Calendar"):
        self.__calendar_text__ = None
        self.__events__ = {}
        self.__event_id__ = 0
        self.calendar_name = calendar_name

    def add_event(self, remind_before, **kwargs):
        event = Event(kwargs, remind_before)
        event_id = self.__event_id__
        self.__events__[self.__event_id__] = event
        self.__event_id__ += 1
        return event_id

    def modify_event(self, event_id, **kwargs):
        for item, data in kwargs.items():
            self.__events__[event_id].event_data[item] = data

    def remove_event(self, event_id):
        self.__events__.pop(event_id)

    def get_ics_text(self):
        self.__calendar_text__ = """BEGIN:VCALENDAR\nMETHOD:PUBLISH\nVERSION:2.0\nX-WR-CALNAME:%s\nPRODID:-//Apple 
        Inc.//macOS 12.1//EN\nCALSCALE:GREGORIAN\nX-WR-TIMEZONE:Asia/Shanghai\n""" % self.calendar_name
        for key, value in self.__events__.items():
            self.__calendar_text__ += value.__turn_to_string__()
        self.__calendar_text__ += "END:VCALENDAR"
        return self.__calendar_text__

    @staticmethod
    def get_abs_path():
        if getattr(sys, 'frozen', False):
            return path.dirname(path.abspath(sys.executable))
        elif __file__:
            return path.dirname(path.abspath(__file__))

    def save_as_ics_file(self):
        ics_text = self.get_ics_text()
        absPath = self.get_abs_path()
        open(absPath + "/%s.ics" % self.calendar_name, "w", encoding="utf8").write(ics_text)  # 使用utf8编码生成ics
        # 文件，否则日历软件打开是乱码

    def open_ics_file(self):
        os_type = os_name
        absPath = self.get_abs_path()
        if os_type == 'nt':
            system(absPath + "/%s.ics" % self.calendar_name)
        elif os_type == 'posix':
            system("open %s/%s.ics" % (absPath, self.calendar_name))


# Added code


def numeric_zero_filling_plus_to_string(number):
    if number < 10:
        return "0%s" % number
    else:
        return "%s" % number


def form_RRULE(until_date):
    yearStr = "%s" % until_date.year
    monthStr = numeric_zero_filling_plus_to_string(until_date.month)
    dayStr = numeric_zero_filling_plus_to_string(until_date.day)

    until = yearStr + monthStr + dayStr + 'T' + '000000Z'
    return "FREQ=WEEKLY;UNTIL=%s" % until


def date_offset_by_week(start, week):
    weekRange = range(0, week, 1)
    for _ in weekRange:
        start += datetime.timedelta(days=7)
    return start


def calculate_RRULE(hint):
    # Minus extraDate,in order to end semester in weeks' Sunday, otherwise it will end any one day in week+1
    extraDate = hint[0].weekday()
    untilDate = date_offset_by_week(hint[0], hint[1]) - datetime.timedelta(days=extraDate + 1)
    RRULE = form_RRULE(untilDate)
    return RRULE


# Added code


def add_event(cal, subject, day_to_start, day_to_end, description, class_room, teacher, email_addr,
              repeat_rule_hint=None, remind_before=0):
    """
    向Calendar日历对象添加事件的方法
    :param teacher: 发起人（老师）
    :param email_addr: 发起人（老师）邮件地址
    :param remind_before: 在开始前几分钟提醒
    :param repeat_rule_hint: 学期开始时间与持续周数
    :param cal: calender日历实例
    :param subject: 事件名
    :param day_to_start: 事件开始时间
    :param day_to_end: 时间结束时间
    :param description: 备注
    :param class_room: 时间地点
    :return:
    """

    if repeat_rule_hint is None:
        repeat_rule_hint = [datetime.datetime.now(), 14]
    time_format = "TZID=Asia/Shanghai:{date.year}{date.month:0>2d}{date.day:0>2d}T{date.hour:0>2d}{date.minute:0>2d}00"
    dt_start = time_format.format(date=day_to_start)
    dt_end = time_format.format(date=day_to_end)
    create_time = datetime.datetime.today().strftime("%Y%m%dT%H%M%SZ")

    cal.add_event(remind_before,
                  SUMMARY=subject,
                  ORGANIZER="CN=%s:mailto:%s" % (teacher, email_addr),
                  DTSTART=dt_start,
                  DTEND=dt_end,
                  DTSTAMP=create_time,
                  UID=uuid4(),
                  SEQUENCE="0",
                  CREATED=create_time,
                  DESCRIPTION=description,
                  LAST_MODIFIED=create_time,
                  LOCATION=class_room,
                  STATUS="CONFIRMED",
                  TRANSP="OPAQUE",
                  RRULE=calculate_RRULE(repeat_rule_hint)
                  )


# Added code


def add_curriculum_from_conf(cal, curriculum_conf):
    global weekOne
    weekOne = curriculum_conf[0]['sem_start_date']
    index = 0
    for item in curriculum_conf:
        if index == 0:
            index += 1
            continue
        add_curriculum(cal, item)
        index += 1


def add_curriculum(cal, curriculum):
    subject = ''
    description = ''
    class_room = ''
    class_length = 0
    teacher = ''
    email_addr = ''
    except_week = []
    remind_before = 0

    for detail in curriculum:
        if detail == 'subject':
            subject = curriculum[detail]
        elif detail == 'day_to_start':
            day_to_start = curriculum[detail]
        elif detail == 'day_to_end':
            day_to_end = curriculum[detail]
        elif detail == 'description':
            description = curriculum[detail]
        elif detail == 'class_room':
            class_room = curriculum[detail]
        elif detail == 'teacher':
            teacher = curriculum[detail]
        elif detail == 'email_addr':
            email_addr = curriculum[detail]
        elif detail == 'class_length':
            class_length = curriculum[detail]
        elif detail == 'except_week':
            except_week = curriculum[detail]
        elif detail == 'remind_before':
            remind_before = curriculum[detail]

    canStartWeek = 1
    time_Intervals = []
    except_week.append(class_length + 1)

    for exceptWeekCount in except_week:
        time_Intervals.append(exceptWeekCount - canStartWeek)
        canStartWeek = exceptWeekCount + 1

    shiftedRepeatStartDate = weekOne
    shiftedStartDate = day_to_start
    shiftedEndDate = day_to_end

    for interval in time_Intervals:
        if interval > 0:
            add_event(cal,
                      subject=subject,
                      day_to_start=shiftedStartDate,
                      day_to_end=shiftedEndDate,
                      description=description,
                      class_room=class_room,
                      teacher=teacher,
                      email_addr=email_addr,
                      repeat_rule_hint=[shiftedRepeatStartDate, interval],
                      remind_before=remind_before)
        shiftedRepeatStartDate += datetime.timedelta(weeks=interval + 1)
        shiftedStartDate += datetime.timedelta(weeks=interval + 1)
        shiftedEndDate += datetime.timedelta(weeks=interval + 1)

# Added code
