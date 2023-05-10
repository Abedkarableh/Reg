# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# ---- type your code here ---


auth.add_group('admin', 'Administrators')
auth.add_membership('admin', 2)


# define the 'student' group
auth.add_group('student', 'Students')

# get the user object using the user_id
user = db.auth_user(3)

# add the user to the 'student' group
auth.add_membership(auth.id_group('student'), 3)





def index():
   return locals()

@auth.requires_login()
def main():
    import time
    response.flash = T("Hello World")
    # set the session timeout to 15 minutes
    session_timeout = 900  # in seconds

    # check if the last activity time is set in the session
    if 'last_activity_time' not in session:
        # if not, set it to the current time
        session.last_activity_time = time.time()

    # check if the user has been inactive for more than the session timeout
    if (time.time() - session.last_activity_time) > session_timeout:
        # if so, log them out and redirect to the login page
        auth.logout()
        redirect(URL('default', 'index'))

    # update the last activity time in the session
    session.last_activity_time = time.time()
    return dict()


def register():
    form = auth.register()
    if form.accepted:
        # User data is valid, add user to database
        auth.add_user(
            username=form.vars.email,
            password=auth.hash_password(form.vars.password),
            first_name=form.vars.first_name,
            last_name=form.vars.last_name,
            email=form.vars.email,
        )
        sql = "INSERT INTO students (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)"
        # Redirect to success page
        redirect(URL('default', 'register_success'))
    return dict(form=form)


def login():
    form = auth.login()
    if form.accepted:
        # Form was submitted and validated successfully
        # You can access form.vars to get the submitted form data
        # For example, form.vars.email and form.vars.password
        # You can then store this information in your database
        db.mytable.insert(email=form.vars.email, password=form.vars.password)
        redirect(URL('default', 'main'))
    return dict(form=form)



@auth.requires_login()
@auth.requires_membership('admin')
def add_schedules():
    form = SQLFORM(db.courseSchedules ,submit_button='Add Schedule')
    
    if form.process().accepted:
        response.flash = 'Schedule added successfully!'
    
    return dict(form=form)

@auth.requires_login()
@auth.requires_membership('admin')
def add_courses():
    form = SQLFORM(db.courses, submit_button='Add Course')
    if form.process().accepted:
        response.flash = 'Course added successfully!'
    return dict(form=form)

@auth.requires_login()
@auth.requires_membership('admin')
def add_rooms():
    form = SQLFORM(db.rooms ,submit_button='Add Rooms')
    if form.process().accepted:
        response.flash = 'Room added successfully!'
    elif form.errors:
        response.flash = 'Please correct the errors.'
    return dict(form=form)


@auth.requires_login()
def search_courses():
    courses = None
    form = FORM(
        DIV(
            LABEL('Enter course code :'),
            INPUT(_name='code',  _class='form-control'),
            _class='form-group'
        ),
        DIV(
            LABEL('Enter course name :'),
            INPUT(_name='name',  _class='form-control'),
            _class='form-group'
        ),
        DIV(
            LABEL('Enter instructor name :'),
            INPUT(_name='instructor', _class='form-control'),
            _class='form-group'
        ),
        DIV(
            INPUT(_type='submit', _value='Search', _class='btn btn-primary'),
            _class='form-group'
        ),
        _class='form'
    )

    if form.process().accepted:
        query = None
        parameter = None
        
        if form.vars.code:
            query = (db.courses.code == form.vars.code)
            parameter = form.vars.code
        elif form.vars.name:
            query = (db.courses.name == form.vars.name)
            parameter = form.vars.name
        elif form.vars.instructor:
            query = (db.courses.instructor == form.vars.instructor)
            parameter = form.vars.instructor
        
        if query:
            courses = db(query).select()
    
    return dict(courses=courses, form=form)




@auth.requires_login()
@auth.requires_membership('Student')
def course_registration():
    query = (db.courseSchedules.id == db.courses.schedule_id)
    join=db.courses.on(db.courseSchedules.id == db.courses.schedule_id)
    fields=[
            db.courses.code,
            db.courses.name,
            db.courses.prerequisites,
            db.courses.num_of_student,
            db.courses.capacity,
            db.courseSchedules.days,
            db.courseSchedules.startTime,
            db.courseSchedules.endTime
        ]
    grid = SQLFORM.grid(
        query=query,
        left=join,
        fields=fields,
        csv=False,
        create=False,
        editable=False,
        deletable=False,
        searchable=False , 
        selectable=registration, 
        formargs=dict(onsubmit=registration),
        selectable_submit_button='Save')
    return dict(grid=grid)



def registration(ids):
    student_id=auth.user.id
    if not ids:
        session.flash = 'Error: Please select a course.'
        redirect(URL('course_registration'))
        
    # convert ids to list
    if not isinstance(ids, (list, tuple)):
        ids = [ids]
        
    # get the selected courses
    courses = db(db.courses.code.belongs(ids)).select()
    

    # check if student exists
    student = db.auth_user(student_id)
    if not student:
        session.flash = 'Error: Student not found'
    
    for course in courses:
        # check if course exists
        if not course:
            session.flash = 'Error: Course not found'

        # check if course is already registered
        if db.studentsregs(student_id=student_id, code=course.code):
            session.flash = 'Error: Course already registered'

        # check if course is full
        if db(db.studentsregs.code==course.code).count() >= course.capacity:
            session.flash =  'Error: Course is full'

        # check if course schedule clashes with existing courses
        new_schedule = db.courseSchedules[course.schedule_id]
        existing_courses = db((db.studentsregs.student_id==student_id) &
                              (db.studentsregs.code!=course.code)).select(db.courses.code, db.courses.schedule_id)
        for existing_course in existing_courses:
            existing_schedule = db.courseSchedules[existing_course.schedule_id]
            if new_schedule.days == existing_schedule.days and \
                new_schedule.starttime < existing_schedule.endtime and \
                new_schedule.endtime > existing_schedule.starttime:
                session.flash =  'Error: Course schedule clashes with existing course'

        # check if student meets prerequisites
        if course.prerequisites:
            prerequisites = course.prerequisites.split(',')
            completed_courses = [row.code for row in db(db.studentsregs.student_id==student_id)(db.studentsregs.code==db.courses.code).select()]
            if not all(preq in completed_courses for preq in prerequisites):
                session.flash =  'Error: Student does not meet prerequisites'

        # register student for course
        db.studentsregs.insert(student_id=student_id, code=course.code)
        course.update_record(num_of_student=course.num_of_student + 1)
        session.flash =  'Success: Course registered'

    return dict()




@auth.requires_login()
@auth.requires_membership('Student')
def my_schedule():


    if auth.user.id:
       query = (db.studentsregs.code == db.courses.code) & (db.studentsregs.student_id == auth.user.id)
 

    join = db.courses.on(db.courseSchedules.id == db.courses.schedule_id)

    fields=[
            db.courses.code,
            db.courses.name,
            db.courseSchedules.days,
            db.courseSchedules.startTime,
            db.courseSchedules.endTime
        ]
    grid = SQLFORM.grid(
        query=query,
        left=join,
        fields=fields,
        csv=False,
        create=False,
        editable=False,
        deletable=False,
        searchable=False)
    return dict(grid=grid)




@auth.requires_login()
def schedules():
   grid = SQLFORM.grid(db.courseSchedules , csv=False , create=False , editable=auth.has_membership('admin'),deletable=auth.has_membership('admin') )
   return dict(grid = grid )



@auth.requires_login()
def courses():
    grid = SQLFORM.grid(db.courses, csv=False  , create=False , editable=auth.has_membership('admin'),deletable=auth.has_membership('admin') )
    return dict(grid = grid)



@auth.requires_login()
def rooms(): 
    grid  = SQLFORM.grid(db.rooms, csv=False, create=False , editable=auth.has_membership('admin'),deletable=auth.has_membership('admin') )
    return dict(grid = grid) 




@auth.requires_login()
@auth.requires_membership('Student')
def notifications():
    registration_deadline = datetime.datetime(2023, 6, 10)
    add_drop_deadline = datetime.datetime(2023, 7, 10)

    now = datetime.datetime.now()

    days_left_registration = (registration_deadline - now).days
    days_left_add_drop = (add_drop_deadline - now).days

    message1 = f"- The registration deadline is in {days_left_registration} days !" 
    message2 = f"- The add/drop deadline is in {days_left_add_drop} days !"

    if days_left_registration <= 0:
        response.flash = "Registration deadline has passed."
    elif days_left_add_drop <= 0:
        response.flash = "Add/Drop deadline has passed."

    return dict(message1=message1,message2=message2)




@auth.requires_login()
@auth.requires_membership('admin')
def reports():
    # Course  Data
    course = db(db.courses).select(db.courses.code).as_list()
    
    # Room  Data
    room = db(db.courseSchedules).select(db.courseSchedules.room_no).as_list()
    
    # Course Schedule Data
    courseschedule = db(db.courseSchedules).select(db.courseSchedules.id, db.courseSchedules.startTime, db.courseSchedules.endTime)
    
    return dict(course=course, room=room, courseschedule=courseschedule)



@auth.requires_login()
@auth.requires_membership('student')
def completed_courses():
    # get the ID of the current logged-in student
    student_id = auth.user.id 
    
    # get a list of courses that the student has completed
    completed_courses = db(db.studentsregs.student_id == student_id).select(db.studentsregs.code)
    completed_courses = [row.code for row in completed_courses]
    
    # get a list of courses that the student has completed the prerequisites for
    courses = db(db.courses.prerequisites.belongs(completed_courses)).select()
    
    return dict(courses=courses)







# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
