# Automatic Students Attendance System

This project is an automatic students attendance system that utilizes facial recognition technology to mark student attendance efficiently. The system is designed to be deployed on a Raspberry Pi and includes several features to enhance usability and functionality.

## Features

- **Facial Recognition**: Automatically marks student attendance using facial recognition.
- **LCD Display**: Displays attendance information in real-time.
- **Camera Integration**: Captures student faces for accurate attendance tracking.
- **Data Storage**: Stores attendance data in a SQLite database.
- **Data Management**: Allows viewing and managing attendance records.

## Technology Stack

- **Programming Language**: Python
- **Facial Recognition Library**: OpenCV
- **Database**: SQLite
- **Hardware**: Raspberry Pi

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Kavita211/automatic_students_attendance.git
   ```

2. Navigate to the project directory:
   ```bash
   cd automatic_students_attendance
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Follow the setup instructions specific to Raspberry Pi.

## Usage

1. Connect the camera and LCD display to the Raspberry Pi.
2. Run the main application:
   ```bash
   python main.py
   ```

3. Follow the on-screen instructions to register students and mark attendance.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

