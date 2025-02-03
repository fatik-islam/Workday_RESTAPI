import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Config:
    # Workday credentials and tenant information
    WORKDAY_USERNAME = os.getenv("WORKDAY_USERNAME", "your_username")
    WORKDAY_PASSWORD = os.getenv("WORKDAY_PASSWORD", "your_password")
    WORKDAY_TENANT   = os.getenv("WORKDAY_TENANT", "your_tenant")

    # WSDL URL for the Workday SOAP API
    WORKDAY_WSDL = os.getenv(
        "WORKDAY_WSDL", 
        "https://wd2-impl-services1.workday.com/ccx/service/ibmsrv_pt1/Human_Resources/v43.2?wsdl"
    )

