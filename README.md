# Timetable Management System

This project provides a **timetable management system** for managing **departments**, **courses**, **labs**, and **staff** assignments. The system allows users to create, manage, display, and export timetables while handling department and staff-related operations.

## Features

### **Department Management**
- **Add Department**:
  - Add a new department by entering a department name.
  - Add **courses** and **labs** associated with the department, specifying the number of periods per week for each.
  
- **Update Department**:
  - Modify the name of an existing department.
  
- **Delete Department**:
  - Delete a department along with all its associated **courses**, **labs**, and **staff assignments**.

### **Course Management**
- **Add Course**:
  - Add a new course to a department by specifying its name and the number of periods per week.

- **Update Course**:
  - Modify an existing course's details such as name and number of periods.

- **Delete Course**:
  - Remove a course from a department.

### **Lab Management**
- **Add Lab**:
  - Add a lab for a department, including the number of periods per week required for the lab.

- **Update Lab**:
  - Modify an existing lab’s details, such as the name and number of periods.

- **Delete Lab**:
  - Remove a lab from the department.

### **Timetable Management**
- **Display Timetable**:
  - Display the timetable for a selected **department** and **shift** (morning/afternoon).
  
- **Export Timetable**:
  - Export the timetable for a department and shift as files for external use.
  
- **Delete Timetable**:
  - Delete an existing timetable for a specific department and shift.

### **Staff Assignment Management**
- **View Free Staff**:
  - View available staff for a specific day, period, and shift.

- **Find Alternate Staff**:
  - Find alternate staff for a specific day, period, and shift if the assigned staff is unavailable.

## How to Use

1. **Add Department**: 
   - Enter the department name and assign courses/labs with the required periods per week.
  
2. **Update Department**: 
   - Modify department details such as name and associated courses/labs.

3. **Delete Department**: 
   - Remove a department and all associated data (courses, labs, staff).

4. **Add/Update/Delete Courses and Labs**: 
   - Manage courses and labs for departments, including the periods they require.

5. **View/Export Timetable**: 
   - Choose to display or export timetables for a specific shift and department.

6. **Find Alternate Staff**:
   - Identify alternate staff for periods when the original staff is unavailable.

7. **View Free Staff**: 
   - Display available staff members for a particular day, shift, and period.

## Getting Started

1. Clone this repository:
    ```
    git clone https://github.com/log0207/TimeTable.git
    ```

2. Install dependencies:
    ```
    pip install -U -r requirements.txt
    ```

3. Run the main program:
    ```
    python main.py
    ```

## Dependencies

- Python 3.x
- Additional packages listed in `requirements.txt`
