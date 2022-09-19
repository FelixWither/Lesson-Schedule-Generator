# -*-coding:utf-8-*-

import CalDataFormatter
import ConfigureParser

if __name__ == '__main__':
    parsed_result = ConfigureParser.parse()
    cal_name = parsed_result[0]['cal_name']
    calendar = CalDataFormatter.Calendar(calendar_name=cal_name)
    CalDataFormatter.add_curriculum_from_conf(calendar, parsed_result)

    calendar.save_as_ics_file()
    print('================================================================================')
    print('                             日历日程表生成完成！')
    print('                              请到程序目录查看')
    print('                           文件名是你设置的日历名称')
    print('================================================================================')
    calendar.open_ics_file()
    if CalDataFormatter.os_name == 'nt':
        input('请按回车键结束程序')
