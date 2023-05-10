# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

response.menu = [
    (T('Home'), False, URL('default', 'main'), [])
]

# ----------------------------------------------------------------------------------------------------------------------
# provide shortcuts for development. you can remove everything below in production
# ----------------------------------------------------------------------------------------------------------------------

if not configuration.get('app.production'):
    _app = request.application
    response.menu += [
        (T('Add'), False, None, [
            (T('Add Schedules'), False, URL('default', 'add_schedules')),
            (T('Add Rooms'), False, URL('default', 'add_rooms')),
            (T('Add Courses'), False, URL('default', 'add_courses')),
        ]),
        (T('Course Registration'), False, URL('default', 'course_registration')),
        (T('My Schedule'), False, URL('default', 'my_schedule')),
        (T('Schedules'), False, URL('default', 'schedules')),
        (T('Courses'), False, URL('default', 'courses')),
        (T('Rooms'), False, URL('default', 'rooms')),
        (T('Notifications'), False, URL('default', 'notifications')),
        (T('Reports'), False, URL('default', 'reports')),  
    ]

