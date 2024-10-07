from database_operations import DatabaseOperations
from timetable_manager import TimetableManager
from excel_export import export_timetable
import tabulate

def main_menu():
    print("\n--- College Timetable Management System V1.4.0 [BETA] ---")
    print("1. Manage Departments")
    print("2. Manage Staff")
    print("3. Manage Courses")
    print("4. Manage Labs")
    print("5. Manage Extra Activities")
    print("6. Generate Timetable")
    print("7. Display/Export Timetable")
    print("8. Display Free Staff")
    print("9. Delete Timetable")
    print("10. Find Alternate Staff")
    print("11. Exit")
    return input("Enter your choice: ")


def manage_courses(db):
    while True:
        print("\n--- Manage Courses ---")
        print("1. Add Course")
        print("2. Edit Course")
        print("3. Delete Course")
        print("4. View Courses")
        print("5. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            add_course(db)
        elif choice == '2':
            edit_course(db)
        elif choice == '3':
            delete_course(db)
        elif choice == '4':
            courses = db.get_courses()
            list_items(courses, "course")
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

def delete_course(db):
    courses = db.get_courses()
    course_id = get_user_choice(courses, "course")
    db.delete_course(course_id)
    print("Course deleted successfully!")

def list_items(items, item_type):
    print(f"Available {item_type}s:")
    for item in items:
        print(f"{item[0]}. {item[1]}")

def get_user_choice(items, item_type):
    list_items(items, item_type)
    return int(input(f"Enter {item_type} ID: "))

def manage_labs(db):
    while True:
        print("\n--- Manage Labs ---")
        print("1. Add Lab")
        print("2. Edit Lab")
        print("3. Delete Lab")
        print("4. View Labs")
        print("5. Remove Staff from Lab")  # New option
        print("6. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            add_lab(db)
        elif choice == '2':
            edit_lab(db)
        elif choice == '3':
            delete_lab(db)
        elif choice == '4':
            view_labs(db)
        elif choice == '5':
            remove_staff_from_lab(db)  # New function call
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")

def remove_staff_from_lab(db):
    departments = db.get_departments()
    department_id = get_user_choice(departments, "department")
    labs = db.get_department_labs(department_id)
    
    if not labs:
        print("No labs found for this department.")
        return

    print("Available labs:")
    for lab in labs:
        print(f"ID: {lab[0]}, Name: {lab[1]}")
    
    lab_id = int(input("Enter the ID of the lab: "))
    if lab_id not in [lab[0] for lab in labs]:
        print("Invalid lab ID.")
        return

    lab_staff = db.get_lab_staff(lab_id)
    if not lab_staff:
        print("No staff assigned to this lab.")
        return

    print("\nCurrently assigned staff:")
    for staff in lab_staff:
        print(f"ID: {staff[0]}, Name: {staff[1]}")

    staff_id = input("Enter the ID of the staff member to remove (or 0 to cancel): ")

    if staff_id == '0':
        print("Staff removal cancelled.")
        return

    try:
        staff_id = int(staff_id)
        if staff_id not in [s[0] for s in lab_staff]:
            print("Invalid staff ID. Please try again.")
            return

        confirm = input(f"Are you sure you want to remove this staff member from the lab? (y/n): ")
        if confirm.lower() == 'y':
            db.cursor.execute('DELETE FROM lab_staff WHERE lab_id = ? AND staff_id = ?', (lab_id, staff_id))
            db.conn.commit()
            print("Staff member removed from the lab successfully!")
        else:
            print("Staff removal cancelled.")
    except ValueError:
        print("Invalid input. Please enter a number.")

def add_lab(db):
    name = input("Enter lab name: ")
    departments = db.get_departments()
    department_id = get_user_choice(departments, "department")
    periods_per_week = int(input("How many periods per week does this lab require? "))
    lab_id = db.add_lab(name, department_id, periods_per_week)
    
    # Assign staff to the lab
    while True:
        assign_staff = input("Do you want to assign staff to this lab? (y/n): ")
        if assign_staff.lower() == 'y':
            staff = db.get_staff(department_id)
            if staff:
                staff_id = get_user_choice(staff, "staff")
                db.assign_lab_to_staff(lab_id, staff_id)
                print("Staff assigned to lab successfully!")
            else:
                print("No staff available for this department.")
        elif assign_staff.lower() == 'n':
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

    print("Lab added successfully!")

def edit_lab(db):
    departments = db.get_departments()
    department_id = get_user_choice(departments, "department")
    labs = db.get_department_labs(department_id)
    
    if not labs:
        print("No labs found for this department.")
        return

    print("Available labs:")
    for lab in labs:
        print(f"ID: {lab[0]}, Name: {lab[1]} (Periods per week: {lab[2]})")
    
    lab_id = int(input("Enter the ID of the lab to edit: "))
    if lab_id not in [lab[0] for lab in labs]:
        print("Invalid lab ID.")
        return

    while True:
        print("\nEdit Lab Menu:")
        print("1. Edit Name")
        print("2. Edit Periods per Week")
        print("3. Assign Staff")
        print("4. View Assigned Staff")
        print("5. Finish Editing")
        choice = input("Enter your choice: ")

        if choice == '1':
            new_name = input("Enter new lab name: ")
            db.update_lab(lab_id, new_name, None)  # Update only the name
            print("Lab name updated successfully!")
        elif choice == '2':
            new_periods = int(input("Enter new periods per week: "))
            db.update_lab(lab_id, None, new_periods)  # Update only the periods
            print("Lab periods updated successfully!")
        elif choice == '3':
            assign_staff_to_lab(db, lab_id, department_id)
        elif choice == '4':
            view_lab_staff(db, lab_id)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

def assign_staff_to_lab(db, lab_id, department_id):
    staff = db.get_staff_by_department(department_id)
    if not staff:
        print("No staff available in this department.")
        return

    print("\nAvailable staff:")
    for s in staff:
        print(f"ID: {s[0]}, Name: {s[1]}")

    staff_id = int(input("Enter the ID of the staff to assign (or 0 to cancel): "))
    if staff_id == 0:
        return

    if staff_id not in [s[0] for s in staff]:
        print("Invalid staff ID.")
        return

    db.assign_lab_to_staff(lab_id, staff_id)
    print("Staff assigned to lab successfully!")

def view_lab_staff(db, lab_id):
    lab_staff = db.get_lab_staff(lab_id)
    if not lab_staff:
        print("No staff assigned to this lab.")
    else:
        print("\nAssigned staff:")
        for staff in lab_staff:
            print(f"ID: {staff[0]}, Name: {staff[1]}")

def edit_extra_activity(db):
    departments = db.get_departments()
    department_id = get_user_choice(departments, "department")
    activities = db.get_department_extra_activities(department_id)
    
    if not activities:
        print("No extra activities found for this department.")
        return

    print("Available extra activities:")
    for activity in activities:
        print(f"ID: {activity[0]}, Name: {activity[1]} (Periods per week: {activity[2]})")
    
    activity_id = int(input("Enter the ID of the extra activity to edit: "))
    if activity_id not in [activity[0] for activity in activities]:
        print("Invalid activity ID.")
        return

    while True:
        print("\nEdit Extra Activity Menu:")
        print("1. Edit Name")
        print("2. Edit Periods per Week")
        print("3. Finish Editing")
        choice = input("Enter your choice: ")

        if choice == '1':
            new_name = input("Enter new activity name: ")
            db.update_extra_activity(activity_id, new_name, None)  # Update only the name
            print("Extra activity name updated successfully!")
        elif choice == '2':
            new_periods = int(input("Enter new periods per week: "))
            db.update_extra_activity(activity_id, None, new_periods)  # Update only the periods
            print("Extra activity periods updated successfully!")
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

def view_labs(db):
    departments = db.get_departments()
    for dept in departments:
        print(f"\nDepartment: {dept[1]}")
        labs = db.get_department_labs(dept[0])
        if labs:
            for lab in labs:
                staff = db.get_lab_staff(lab[0])
                staff_names = ", ".join([s[1] for s in staff]) if staff else "No staff assigned"
                print(f"  ID: {lab[0]}, Name: {lab[1]} (Periods per week: {lab[2]}) - Staff: {staff_names}")
        else:
            print("  No labs for this department.")

def delete_lab(db):
    departments = db.get_departments()
    department_id = get_user_choice(departments, "department")
    labs = db.get_department_labs(department_id)
    
    if not labs:
        print("No labs found for this department.")
        return

    print("Available labs:")
    for lab in labs:
        print(f"ID: {lab[0]}, Name: {lab[1]} (Periods per week: {lab[2]})")
    
    lab_id = int(input("Enter the ID of the lab to delete: "))
    if lab_id in [lab[0] for lab in labs]:
        confirm = input(f"Are you sure you want to delete this lab? (y/n): ")
        if confirm.lower() == 'y':
            db.delete_lab(lab_id)
            print("Lab deleted successfully!")
        else:
            print("Deletion cancelled.")
    else:
        print("Invalid lab ID.")

def manage_departments(db):
    while True:
        print("\n--- Manage Departments ---")
        print("1. Add Department")
        print("2. Edit Department")
        print("3. Delete Department")
        print("4. View Departments")
        print("5. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            add_department(db)
        elif choice == '2':
            edit_department(db)
        elif choice == '3':
            delete_department(db)
        elif choice == '4':
            departments = db.get_departments()
            list_items(departments, "department")
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

def edit_department(db):
    departments = db.get_departments()
    dept_id = get_user_choice(departments, "department")
    name = input("Enter new department name (or press enter to keep current): ")
    if name:
        db.update_department(dept_id, name)
    print("Department updated successfully!")

def delete_department(db):
    departments = db.get_departments()
    dept_id = get_user_choice(departments, "department")
    confirm = input(f"Are you sure you want to delete this department? This will also delete all associated courses and staff assignments. (y/n): ")
    if confirm.lower() == 'y':
        db.delete_department(dept_id)
        print("Department deleted successfully!")
    else:
        print("Deletion cancelled.")

def add_department(db):
    name = input("Enter department name: ")
    dept_id = db.add_department(name)
    print("Department added successfully!")
    
    while True:
        course_name = input("Enter a course for this department (or press enter to finish): ")
        if not course_name:
            break
        periods_per_week = int(input("How many periods per week does this course require? "))
        db.add_course(course_name, dept_id, periods_per_week)
        print(f"Course '{course_name}' added to the department.")
    
    while True:
        lab_name = input("Enter a lab for this department (or press enter to finish): ")
        if not lab_name:
            break
        periods_per_week = int(input("How many periods per week does this lab require? "))
        db.add_lab(lab_name, dept_id, periods_per_week)
        print(f"Lab '{lab_name}' added to the department.")

def find_alternate_staff(tm):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    day = days[get_user_choice(list(enumerate(days, 1)), "day") - 1]
    period = int(input("Enter period: "))
    shift = int(input("Enter shift (1 or 2): "))
    staff = tm.db.get_staff()
    staff_id = get_user_choice(staff, "staff")
    
    timetable_entry, alternate_staff = tm.get_alternate_staff(day, period, shift, staff_id)
    
    if not timetable_entry:
        print(f"No timetable entry found for the selected staff on {day}, period {period}, shift {shift}.")
        return
    
    print(f"\nCurrent timetable entry:")
    print(f"Course: {timetable_entry[3]}, Staff: {timetable_entry[5]}")
    
    if not alternate_staff:
        print("No alternate staff available for this slot.")
    else:
        print("\nAvailable alternate staff:")
        for staff in alternate_staff:
            print(f"ID: {staff[0]}, Name: {staff[1]}")

def add_course(db):
    name = input("Enter course name: ")
    departments = db.get_departments()
    department_id = get_user_choice(departments, "department")
    periods_per_week = int(input("How many periods per week does this course require? "))
    db.add_course(name, department_id, periods_per_week)
    print("Course added successfully!")

def edit_course(db):
    courses = db.get_courses()
    course_id = get_user_choice(courses, "course")
    name = input("Enter new course name (or press enter to keep current): ")
    departments = db.get_departments()
    department_id = get_user_choice(departments, "department")
    periods_per_week = int(input("How many periods per week does this course require? "))
    
    if not name:
        name = courses[course_id-1][1]
    
    db.update_course(course_id, name, department_id, periods_per_week)
    print("Course updated successfully!")

def manage_extra_activities(db):
    while True:
        print("\n--- Manage Extra Activities ---")
        print("1. Add Extra Activity")
        print("2. Edit Extra Activity")
        print("3. Delete Extra Activity")
        print("4. View Extra Activities")
        print("5. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            add_extra_activity(db)
        elif choice == '2':
            edit_extra_activity(db)
        elif choice == '3':
            delete_extra_activity(db)
        elif choice == '4':
            view_extra_activities(db)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

def add_extra_activity(db):
    name = input("Enter extra activity name: ")
    departments = db.get_departments()
    department_id = get_user_choice(departments, "department")
    periods_per_week = int(input("How many periods per week does this activity require? "))
    db.add_extra_activity(name, department_id, periods_per_week)
    print("Extra activity added successfully!")

def view_extra_activities(db):
    departments = db.get_departments()
    for dept in departments:
        print(f"\nDepartment: {dept[1]}")
        activities = db.get_department_extra_activities(dept[0])
        if activities:
            for idx, activity in enumerate(activities, 1):
                print(f"  {idx}. {activity[1]} (Periods per week: {activity[2]})")
        else:
            print("  No extra activities for this department.")

def delete_extra_activity(db):
    departments = db.get_departments()
    department_id = get_user_choice(departments, "department")
    activities = db.get_department_extra_activities(department_id)
    
    if not activities:
        print("No extra activities found for this department.")
        return

    print("Available extra activities:")
    for idx, activity in enumerate(activities, 1):
        print(f"{idx}. {activity[1]} (Periods per week: {activity[2]})")
    
    choice = int(input("Enter the number of the extra activity to delete: "))
    if 1 <= choice <= len(activities):
        activity_id = activities[choice-1][0]
        confirm = input(f"Are you sure you want to delete this extra activity? (y/n): ")
        if confirm.lower() == 'y':
            db.delete_extra_activity(activity_id)
            print("Extra activity deleted successfully!")
        else:
            print("Deletion cancelled.")
    else:
        print("Invalid choice.")

def assign_courses(db, staff_id):
    while True:
        departments = db.get_staff_departments(staff_id)
        for dept in departments:
            print(f"\nCourses for department: {dept[1]}")
            courses = db.get_courses_by_department(dept[0])
            assigned_courses = db.get_staff_courses(staff_id)
            available_courses = [c for c in courses if c[0] not in [ac[0] for ac in assigned_courses]]
            
            print("\nAvailable courses:")
            for course in available_courses:
                print(f"{course[0]}. {course[1]}")
        
        course_id = int(input("Enter course ID (or 0 to finish): "))
        if course_id == 0:
            break
        if course_id not in [c[0] for c in available_courses]:
            print("Invalid course ID or course already assigned. Please try again.")
            continue
        db.assign_course_to_staff(staff_id, course_id)
        print("Course assigned to staff successfully!")

def assign_extra_activities(db, staff_id):
    while True:
        all_extra_activities = db.get_extra_activities()
        assigned_activities = db.get_staff_extra_activities(staff_id)
        assigned_activity_ids = [a[0] for a in assigned_activities]
        
        available_activities = [a for a in all_extra_activities if a[0] not in assigned_activity_ids]
        
        if not available_activities:
            print("No more extra activities available to assign.")
            break
        
        print("\nAvailable extra activities:")
        for activity in available_activities:
            print(f"{activity[0]}. {activity[1]}")
        
        activity_id = input("Enter extra activity ID (or 0 to finish): ")
        
        if activity_id == '0':
            break
        
        try:
            activity_id = int(activity_id)
            if activity_id not in [a[0] for a in available_activities]:
                print("Invalid activity ID. Please try again.")
                continue
            
            db.assign_extra_activity_to_staff(staff_id, activity_id)
            print("Extra activity assigned to staff successfully!")
        except ValueError:
            print("Invalid input. Please enter a number.")

    print("Extra activities assignment completed.")

def add_staff(db):
    name = input("Enter staff name: ")
    staff_id = db.add_staff(name)
    print("Staff added successfully!")
    
    while True:
        departments = db.get_departments()
        department_id = get_user_choice(departments, "department")
        db.assign_staff_to_department(staff_id, department_id)
        if input("Do you want to assign another department? (y/n): ").lower() != 'y':
            break
    
    assign_courses(db, staff_id)
    assign_extra_activities(db, staff_id)

def edit_staff(db):
    staff = db.get_staff()
    staff_id = get_user_choice(staff, "staff")
    
    while True:
        print("\n--- Edit Staff ---")
        print("1. Edit Name")
        print("2. Edit Assigned Departments")
        print("3. Edit Assigned Courses")
        print("4. Edit Assigned Extra Activities")
        print("5. Back to Staff Management")
        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter new staff name: ")
            current_departments = db.get_staff_departments(staff_id)
            if current_departments:
                department_id = current_departments[0][0]  # Use the first assigned department
                db.update_staff(staff_id, name, department_id)
                print("Staff name updated successfully!")
            else:
                print("Error: Staff must be assigned to at least one department.")
                print("Please assign a department first.")
        elif choice == '2':
            edit_staff_departments(db, staff_id)
        elif choice == '3':
            edit_staff_courses(db, staff_id)
        elif choice == '4':
            edit_staff_extra_activities(db, staff_id)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

def edit_staff_departments(db, staff_id):
    current_departments = db.get_staff_departments(staff_id)
    print("Current departments:")
    for dept in current_departments:
        print(f"- {dept[1]}")
    
    if input("Do you want to update assigned departments? (y/n): ").lower() == 'y':
        db.delete_staff_departments(staff_id)
        while True:
            departments = db.get_departments()
            department_id = get_user_choice(departments, "department")
            db.assign_staff_to_department(staff_id, department_id)
            if input("Do you want to assign another department? (y/n): ").lower() != 'y':
                break
        

        updated_departments = db.get_staff_departments(staff_id)
        if updated_departments:
            staff_info = db.get_staff(staff_id)[0]
            db.update_staff(staff_id, staff_info[1], updated_departments[0][0])
        
    print("Staff departments updated successfully!")

def edit_staff_courses(db, staff_id):
    current_courses = db.get_staff_courses(staff_id)
    print("Current courses:")
    for course in current_courses:
        print(f"- {course[1]}")
    
    if input("Do you want to update assigned courses? (y/n): ").lower() == 'y':
        db.delete_staff_courses(staff_id)
        assign_courses(db, staff_id)
    print("Staff courses updated successfully!")

def edit_staff_extra_activities(db, staff_id):
    while True:
        current_activities = db.get_staff_extra_activities(staff_id)
        print("Current extra activities:")
        for activity in current_activities:
            print(f"- {activity[1]}")
        
        print("\n1. Add extra activities")
        print("2. Remove extra activities")
        print("3. Finish editing")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            assign_extra_activities(db, staff_id)
        elif choice == '2':
            remove_extra_activities(db, staff_id)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")
    
    print("Staff extra activities updated successfully!")

def remove_extra_activities(db, staff_id):
    while True:
        current_activities = db.get_staff_extra_activities(staff_id)
        print("\nCurrent extra activities:")
        for activity in current_activities:
            print(f"{activity[0]}. {activity[1]}")
        
        activity_id = input("Enter extra activity ID to remove (or 0 to finish): ")
        
        if activity_id == '0':
            break
        
        try:
            activity_id = int(activity_id)
            if activity_id not in [a[0] for a in current_activities]:
                print("Invalid activity ID. Please try again.")
                continue
            
            db.remove_extra_activity_from_staff(staff_id, activity_id)
            print("Extra activity removed from staff successfully!")
        except ValueError:
            print("Invalid input. Please enter a number.")

    print("Extra activities removal completed.")

def manage_staff(db):
    while True:
        print("\n--- Manage Staff ---")
        print("1. Add Staff")
        print("2. Edit Staff")
        print("3. Delete Course from Staff")
        print("4. View Staff")
        print("5. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            add_staff(db)
        elif choice == '2':
            edit_staff(db)
        elif choice == '3':
            delete_course_from_staff(db)
        elif choice == '4':
            view_staff(db)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

def delete_course_from_staff(db):
    staff = db.get_staff()
    staff_id = get_user_choice(staff, "staff")
    courses = db.get_staff_courses(staff_id)
    if not courses:
        print("This staff member has no assigned courses.")
        return
    course_id = get_user_choice(courses, "course")
    db.delete_course_from_staff(staff_id, course_id)
    print("Course deleted from staff successfully!")

def view_staff(db):
    staff = db.get_staff()
    for s in staff:
        print(f"\nID: {s[0]}, Name: {s[1]}")
        departments = db.get_staff_departments(s[0])
        print("Departments:")
        for dept in departments:
            print(f"  - {dept[1]}")
        courses = db.get_staff_courses(s[0])
        print("Assigned Courses:")
        for c in courses:
            print(f"  - {c[1]}")
        extra_activities = db.get_staff_extra_activities(s[0])
        print("Assigned Extra Activities:")
        for ea in extra_activities:
            print(f"  - {ea[1]}")

def display_timetable(timetable_data):
    if isinstance(timetable_data, list) and 'department_name' in timetable_data[0]:
        for dept_data in timetable_data:
            print(f"\nDepartment: {dept_data['department_name']}")
            display_single_department_timetable(dept_data['timetable'])
    else:
        display_single_department_timetable(timetable_data)

def display_single_department_timetable(timetable_data):
    days = [day['Day'] for day in timetable_data]
    periods = timetable_data[0]['Periods']
    
    headers = ['Day'] + [f"P{p['Period']}\n{p['Time']}" for p in periods]
    table_data = []
    
    for day_data in timetable_data:
        row = [day_data['Day']]
        for period in day_data['Periods']:
            if period['Type'] == 'regular':
                cell = f"{period['Course']}\n{period['Staff']}" if period['Course'] else ''
            else:
                cell = period['Type'].capitalize()
            row.append(cell)
        table_data.append(row)
    
    print(tabulate.tabulate(table_data, headers=headers, tablefmt='grid'))

def main():
    db = DatabaseOperations()
    tm = TimetableManager()

    while True:
        choice = main_menu()
        
        if choice == '1':
            manage_departments(db)
        elif choice == '2':
            manage_staff(db)
        elif choice == '3':
            manage_courses(db)
        elif choice == '4':
            manage_labs(db)
        elif choice == '5':
            manage_extra_activities(db)
        elif choice == '6':
            shift = int(input("Enter shift to generate timetable for (1 or 2): "))
            working_days = int(input("Enter number of working days per week (5 or 6): "))
            periods_per_day = 7  # Fixed to 7 periods per day
            
            departments = db.get_departments()
            print("\nAvailable departments:")
            for dept in departments:
                print(f"{dept[0]}. {dept[1]}")
            
            department_input = input("Enter department ID (or press Enter for all departments): ")
            department_id = int(department_input) if department_input else None
            
            tm.create_timetable(shift, working_days, periods_per_day, department_id)
            print("Timetable generated successfully!")
        elif choice == '7':
            shift = int(input("Enter shift to display/export timetable for (1 or 2): "))
            departments = db.get_departments()
            print("\nAvailable departments:")
            for dept in departments:
                print(f"{dept[0]}. {dept[1]}")
            department_input = input("Enter department ID (or press Enter for all departments): ")
            department_id = int(department_input) if department_input else None
            display_choice = input("Do you want to (D)isplay, or (E)xport? ").lower()
            if display_choice == 'd':
                timetable_data = tm.get_timetable_data(shift, department_id)
                display_timetable(timetable_data)
            elif display_choice == 'e':
                filename = input("Enter the base filename to save the files (without extension): ")
                export_timetable(tm, shift, filename, department_id)
            else:
                print("Invalid choice. Please try again.")
        elif choice == '8':
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            day = days[get_user_choice(list(enumerate(days, 1)), "day") - 1]
            period = int(input("Enter period: "))
            shift = int(input("Enter shift (1 or 2): "))
            tm.display_free_staff(day, period, shift)
        elif choice == '9':
            shift = int(input("Enter shift to delete timetable for (1 or 2): "))
            
            departments = db.get_departments()
            print("\nAvailable departments:")
            for dept in departments:
                print(f"{dept[0]}. {dept[1]}")
            
            department_input = input("Enter department ID (or press Enter for all departments): ")
            department_id = int(department_input) if department_input else None
            
            try:
                tm.delete_timetable(shift, department_id)
                print("Timetable deleted successfully!")
            except Exception as e:
                print(f"An error occurred while deleting the timetable: {str(e)}")
        elif choice == '10':
            find_alternate_staff(tm)
        elif choice == '11':
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

    db.close()

if __name__ == "__main__":
    main()