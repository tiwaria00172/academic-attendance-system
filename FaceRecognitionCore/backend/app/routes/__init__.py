from app.routes.auth import auth_bp
from app.routes.attendance import attendance_bp
from app.routes.students import students_bp
from app.routes.classes import classes_bp
from app.routes.reports import reports_bp

__all__ = ['auth_bp', 'attendance_bp', 'students_bp', 'classes_bp', 'reports_bp']
