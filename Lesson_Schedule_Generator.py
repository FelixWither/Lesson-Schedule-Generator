# -*-coding:utf-8-*-

import CalDataFormatter
import ConfigureParser

if __name__ == '__main__':
    parsed_result = ConfigureParser.parse()
    cal_name = parsed_result[0]['cal_name']
    calendar = CalDataFormatter.Calendar(calendar_name=cal_name)
    CalDataFormatter.add_curriculum_from_conf(calendar, parsed_result)

    calendar.save_as_ics_file()
