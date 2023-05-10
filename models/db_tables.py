import datetime

db.define_table('rooms',
    Field('code', 'string', required=True, notnull=True),
    primarykey=['code']
)

db.define_table('courseSchedules',
    Field('id', 'integer', required=True, notnull=True),
    Field('days', 'string'),
    Field('startTime', 'time', default=datetime.time(0,0)),
    Field('endTime', 'time', default=datetime.time(0,0)),
    Field('room_no', 'reference rooms', requires=IS_IN_DB(db, 'rooms.code', '%(code)s')),
    primarykey=['id']
)

db.define_table('courses',
    Field('code', 'string', required=True, notnull=True),
    Field('name', 'string'),
    Field('description', 'string'),
    Field('prerequisites', 'reference courses', requires=IS_EMPTY_OR(IS_IN_DB(db, 'courses.code', '%(name)s'))),
    Field('instructor', 'string'),
    Field('num_of_student', 'integer'), 
    Field('capacity', 'integer'),
    Field('schedule_id', 'reference courseSchedules', requires=IS_IN_DB(db, 'courseSchedules.id', '%(days)s: %(startTime)s - %(endTime)s')),
    primarykey=['code']
)

db.define_table('studentsregs', 
    Field('id','integer'),
    Field('student_id','integer'),
    Field('code','string'),
    primarykey =['id']
)

db.define_table('students',
    Field('student_id', 'integer', required=True, notnull=True),
    Field('first_name', 'string'),
    Field('last_name', 'string'),
    Field('email', 'string'),
    Field('password', 'string'),
    Field('registration_key', 'string'),
    Field('reset_password_key', 'string'),
    Field('registration_id', 'string'),
    primarykey =['student_id']
)
