import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    WORKDAY_WSDL = os.getenv("WORKDAY_WSDL", "https://wd2-impl-services1.workday.com/ccx/service/ibmsrv_pt1/Human_Resources/v43.2?wsdl")
    WORKDAY_TENANT = os.getenv("WORKDAY_TENANT", "your_workday_tenant")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key")
