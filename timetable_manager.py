import random
from database_operations import DatabaseOperations

class TimetableManager:
    def __init__(self):
        self.db = DatabaseOperations()
        self.shifts = {
            1: {
                "name": "Morning Shift",
                "time": "8:30 AM to 1:30 PM",
                "periods": [
                    {"start": "08:30", "end": "09:15", "type": "regular"},
                    {"start": "09:15", "end": "10:00", "type": "regular"},
                    {"start": "10:00", "end": "10:20", "type": "break"},
                    {"start": "10:20", "end": "11:00", "type": "regular"},
                    {"start": "11:00", "end": "11:40", "type": "regular"},
                    {"start": "11:40", "end": "11:50", "type": "break"},
                    {"start": "11:50", "end": "12:25", "type": "regular"},
                    {"start": "12:25", "end": "01:00", "type": "regular"},
                    {"start": "01:00", "end": "01:30", "type": "regular"}
                ]
            },
            2: {
                "name": "Afternoon Shift",
                "time": "1:30 PM to 6:30 PM",
                "periods": [
                    {"start": "12:00", "end": "12:40", "type": "regular"},
                    {"start": "12:40", "end": "01:20", "type": "regular"},
                    {"start": "01:20", "end": "02:00", "type": "regular"},
                    {"start": "02:00", "end": "02:20", "type": "lunch"},
                    {"start": "02:20", "end": "03:00", "type": "regular"},
                    {"start": "03:00", "end": "03:40", "type": "regular"},
                    {"start": "03:40", "end": "03:50", "type": "break"},
                    {"start": "03:50", "end": "04:25", "type": "regular"},
                    {"start": "04:25", "end": "05:00", "type": "regular"}
                ]
            }
        }

    def create_timetable(self, shift, working_days, periods_per_day, department_id=None):
        self.db.delete_timetable(shift, department_id)
        departments = [self.db.get_department(department_id)] if department_id else self.db.get_departments()
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][:working_days]

        courses = self.db.get_courses(department_id)
        course_periods = {course[0]: {'total': 0, 'per_day': {day: 0 for day in days}} for course in courses}
        
        # Initialize staff_periods with all staff members
        all_staff = self.db.get_staff(department_id)
        staff_periods = {staff[0]: {'total': 0, 'per_day': {day: 0 for day in days}} for staff in all_staff}

        print("Starting timetable generation...")
        for day in days:
            print(f"Generating timetable for {day}...")
            self._create_day_timetable(departments, day, shift, course_periods, staff_periods, periods_per_day)
            print(f"Timetable for {day} generated.")

        print("Adding labs...")
        self._add_labs(days, shift, departments, periods_per_day)
        print("Labs added.")

        print("Adding extra activities...")
        self._add_extra_activities(days, shift, departments, periods_per_day)
        print("Extra activities added.")

        print("Filling empty slots...")
        self._fill_empty_slots(days, shift, department_id, course_periods, staff_periods, periods_per_day)
        print("Empty slots filled.")

        print("Timetable generation completed.")

    def _add_labs(self, days, shift, departments, periods_per_day):
        for department in departments:
            labs = self.db.get_department_labs(department[0])
            regular_periods = [i for i, p in enumerate(self.shifts[shift]["periods"], start=1) if p["type"] == "regular"][:periods_per_day]
    
            for lab in labs:
                periods_scheduled = 0
                attempts = 0
                while periods_scheduled < lab[2] and attempts < 100:  # periods_per_week, limit attempts
                    attempts += 1
                    day = random.choice(days)
                    available_periods = [p for p in regular_periods if not self.db.get_timetable_entry(day, p, shift, department[0])]
                    if len(available_periods) >= 2:
                        consecutive_periods = [p for p in available_periods if p+1 in available_periods]
                        if consecutive_periods:
                            period = random.choice(consecutive_periods)
                            self.db.add_timetable_entry(day, period, shift, lab[0], None)
                            self.db.add_timetable_entry(day, period+1, shift, lab[0], None)
                            periods_scheduled += 2
                            print(f"Scheduled lab {lab[1]} on {day}, periods {period} and {period+1}")
                        else:
                            print(f"No consecutive periods available for lab {lab[1]} on {day}")
                    else:
                        print(f"Not enough available periods for lab {lab[1]} on {day}")
                
                if periods_scheduled < lab[2]:
                    print(f"Warning: Could only schedule {periods_scheduled}/{lab[2]} periods for lab {lab[1]}")

    def _create_day_timetable(self, departments, day, shift, course_periods, staff_periods, periods_per_day):
        regular_periods = [i for i, p in enumerate(self.shifts[shift]["periods"], start=1) if p["type"] == "regular"][:periods_per_day]
        random.shuffle(regular_periods)  # Randomize the order of periods
    
        for period_num in regular_periods:
            if self.db.get_timetable_entry(day, period_num, shift):
                continue
        
            department_order = list(departments)
            random.shuffle(department_order)
        
            for department in department_order:
                courses = self.db.get_department_courses(department[0])
                available_courses = [
                    c for c in courses 
                    if course_periods[c[0]]['total'] < c[3] and  # periods_per_week
                    course_periods[c[0]]['per_day'][day] < 2  # Limit to 2 periods per day for each course
                ]
            
                if not available_courses:
                    continue
            
                course_weights = [self._calculate_course_weight(c, course_periods) for c in available_courses]
                selected_course = random.choices(available_courses, weights=course_weights, k=1)[0]
            
                staff_ids = self._get_available_staff(selected_course[0], day, period_num, shift, staff_periods)
            
                if staff_ids:
                    staff_weights = [self._calculate_staff_weight(s, staff_periods, day) for s in staff_ids]
                    staff_id = random.choices(staff_ids, weights=staff_weights, k=1)[0]
            
                    if self._check_continuous_periods(staff_id, day, period_num, shift, periods_per_day) <= 2:
                        self.db.add_timetable_entry(day, period_num, shift, selected_course[0], staff_id)
                        course_periods[selected_course[0]]['total'] += 1
                        course_periods[selected_course[0]]['per_day'][day] += 1
                        self._update_staff_periods(staff_periods, staff_id, day)
                        break

    def _update_staff_periods(self, staff_periods, staff_id, day):
        """Safely update staff periods"""
        if staff_id not in staff_periods:
            staff_periods[staff_id] = {'total': 0, 'per_day': {day: 0 for day in staff_periods[next(iter(staff_periods))]['per_day']}}
        staff_periods[staff_id]['total'] += 1
        staff_periods[staff_id]['per_day'][day] += 1

    def _fill_empty_slots(self, days, shift, department_id, course_periods, staff_periods, periods_per_day):
        regular_periods = [i for i, p in enumerate(self.shifts[shift]["periods"], start=1) if p["type"] == "regular"][:periods_per_day]
        for day in days:
            for period_num in regular_periods:
                if not self.db.get_timetable_entry(day, period_num, shift):
                    self._fill_slot_with_extra_activity(day, period_num, shift, department_id)

    def _fill_slot_with_extra_activity(self, day, period_num, shift, department_id):
        extra_activities = self.db.get_department_extra_activities(department_id)
        if extra_activities:
            activity = random.choice(extra_activities)
            self.db.add_timetable_entry(day, period_num, shift, activity[0], None)
            print(f"Filled empty slot with extra activity {activity[1]} on {day}, period {period_num}")
        else:
            print(f"No extra activities available to fill empty slot on {day}, period {period_num}")

    def _add_extra_activities(self, days, shift, departments, periods_per_day):
        for department in departments:
            extra_activities = self.db.get_department_extra_activities(department[0])
            regular_periods = [i for i, p in enumerate(self.shifts[shift]["periods"], start=1) if p["type"] == "regular"][:periods_per_day]
    
            for activity in extra_activities:
                periods_scheduled = 0
                attempts = 0
                while periods_scheduled < activity[2] and attempts < 100:  # periods_per_week, limit attempts
                    attempts += 1
                    day = random.choice(days)
                    available_periods = [p for p in regular_periods if not self.db.get_timetable_entry(day, p, shift, department[0])]
                    if available_periods:
                        # Prioritize last period for extra activities
                        period = max(available_periods)
                        self.db.add_timetable_entry(day, period, shift, activity[0], None)
                        periods_scheduled += 1
                        print(f"Scheduled extra activity {activity[1]} on {day}, period {period}")
                    else:
                        print(f"No available periods for extra activity {activity[1]} on {day}")
                
                if periods_scheduled < activity[2]:
                    print(f"Warning: Could only schedule {periods_scheduled}/{activity[2]} periods for activity {activity[1]}")


    def _calculate_course_weight(self, course, course_periods):
        remaining_periods = course[3] - course_periods[course[0]]['total']
        return remaining_periods + 1

    def _calculate_staff_weight(self, staff_id, staff_periods, day):
        if staff_id in staff_periods and day in staff_periods[staff_id]['per_day']:
            daily_periods = staff_periods[staff_id]['per_day'][day]
        else:
            daily_periods = 0  
        total_periods = staff_periods.get(staff_id, {}).get('total', 0)
    
        return (5 - daily_periods) * (20 - total_periods)


    def _get_available_staff(self, course_id, day, period, shift, staff_periods):
        free_staff = self.db.get_free_staff(day, period, shift)
        course_staff = self.db.get_course_staff(course_id)
        available_staff = [
            staff for staff in free_staff 
            if staff[0] in [cs[0] for cs in course_staff] and
            self._check_staff_availability(staff[0], day, staff_periods) and
            not self._is_staff_teaching_in_other_department(staff[0], day, period, shift)
        ]
        return [staff[0] for staff in available_staff]

    def _check_staff_availability(self, staff_id, day, staff_periods):
        # Check if staff_id exists in staff_periods and has less than 5 periods for the day
        if staff_id in staff_periods:
            return staff_periods[staff_id].get('per_day', {}).get(day, 0) < 5
        return True

    def _is_staff_teaching_in_other_department(self, staff_id, day, period, shift):
        # Check if the staff is teaching in any department for the given day, period, and shift
        timetable_entry = self.db.get_timetable_entry_by_staff(day, period, shift, staff_id)
        return timetable_entry is not None

    def _check_continuous_periods(self, staff_id, day, current_period, shift, periods_per_day):
        continuous_periods = 1
        
        # Check previous periods
        for period in range(current_period - 1, 0, -1):
            entry = self.db.get_timetable_entry_by_staff(day, period, shift, staff_id)
            if entry:
                continuous_periods += 1
            else:
                break
        
        # Check next periods
        for period in range(current_period + 1, periods_per_day + 1):
            entry = self.db.get_timetable_entry_by_staff(day, period, shift, staff_id)
            if entry:
                continuous_periods += 1
            else:
                break
        
        return continuous_periods

    def _get_available_periods_for_extra_activities(self, day, shift, department_id):
        regular_periods = [p for p in self.shifts[shift]["periods"] if p["type"] == "regular"]
        available_periods = []
        for i, period in enumerate(regular_periods[-2:], start=len(regular_periods)-1):
            if not self.db.get_timetable_entry(day, i, shift, department_id):
                available_periods.append(i)
        return available_periods

    def get_timetable_data(self, shift, department_id=None):
        if department_id:
            return self._get_single_department_timetable(shift, department_id)
        else:
            return self._get_all_departments_timetable(shift)

    def _get_single_department_timetable(self, shift, department_id):
        timetable = self.db.get_timetable(shift, department_id)
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        periods = self.shifts[shift]["periods"]
        
        timetable_data = []
        for day in days:
            day_data = {"Day": day, "Periods": []}
            for i, period in enumerate(periods, start=1):
                entry = next((e for e in timetable if e[0] == day and e[1] == i), None)
                if entry:
                    course = entry[3]
                    staff = ', '.join(entry[4]) if isinstance(entry[4], list) else entry[4]
                else:
                    course = ""
                    staff = ""
                day_data["Periods"].append({
                    "Period": i,
                    "Time": f"{period['start']}-{period['end']}",
                    "Course": course,
                    "Staff": staff,
                    "Type": period["type"]
                })
            timetable_data.append(day_data)
        
        return timetable_data

    def _get_all_departments_timetable(self, shift):
        departments = self.db.get_departments()
        all_timetable_data = []
        
        for department in departments:
            department_timetable = self._get_single_department_timetable(shift, department[0])
            all_timetable_data.append({
                "department_name": department[1],
                "timetable": department_timetable
            })
        
        return all_timetable_data

    def display_timetable(self, shift, department_id=None):
        timetable_data = self.get_timetable_data(shift, department_id)
        department_name = self.db.get_department(department_id)[1] if department_id else "All Departments"
        print(f"\nTimetable for {self.shifts[shift]['name']} ({self.shifts[shift]['time']}) - {department_name}:")
    
        print("Day", end="\t")
        regular_period_count = 0
        for period in timetable_data[0]["Periods"]:
            if period["Type"] == "regular":
                regular_period_count += 1
                print(f"Period {regular_period_count} ({period['Time']})", end="\t")
            else:
                print(f"{period['Type'].capitalize()} ({period['Time']})", end="\t")
        print()
        
        for day_data in timetable_data:
            print(day_data["Day"], end="\t")
            for period in day_data["Periods"]:
                if period["Type"] == "regular":
                    if period["Course"] and period["Staff"]:
                        print(f"{period['Course']} ({period['Staff']})", end="\t")
                    else:
                        print(" ", end="\t")  # For empty slots
                else:
                    print(f"{period['Type'].capitalize()}", end="\t")
            print()

    def delete_timetable(self, shift, department_id=None):
        self.db.delete_timetable(shift, department_id)
        if department_id:
            department = self.db.get_department(department_id)
            print(f"Timetable for {self.shifts[shift]['name']} and {department[1]} department has been deleted.")
        else:
            print(f"Timetable for {self.shifts[shift]['name']} has been deleted.")

    def display_free_staff(self, day, period, shift):
        free_staff = self.db.get_free_staff(day, period, shift)
        print(f"Free staff for Day: {day}, Period: {period}, Shift: {shift}")
        for staff in free_staff:
            print(f"ID: {staff[0]}, Name: {staff[1]}")

    def get_alternate_staff(self, day, period, shift, staff_id):
        timetable_entry = self.db.get_timetable_entry_by_staff(day, period, shift, staff_id)
        if not timetable_entry:
            return None, None

        course_id = timetable_entry[4]  # Assuming course_id is at index 4
        alternate_staff = self._get_available_staff(course_id, day, period, shift, {})  # Empty dict as we don't have staff_periods here

        return timetable_entry, alternate_staff