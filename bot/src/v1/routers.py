# Local
from src.v1.handlers import doctor, master, patient


ROUTERS = [master.router, doctor.router, patient.router]
