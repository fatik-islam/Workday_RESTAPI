#!/usr/bin/env python3
from zeep import Client, Settings
from zeep.exceptions import Fault
from zeep.wsse.username import UsernameToken
from zeep.helpers import serialize_object

class WorkdaySOAPClient:
    """
    A wrapper for the Workday SOAP API Get_Workers operation.
    
    This implementation expects the client to supply a dictionary that mirrors the full SOAP XML structure.
    """
    
    def __init__(self, wsdl_url, username, password, tenant):
        settings = Settings(strict=False, xml_huge_tree=True)
        self.client = Client(
            wsdl=wsdl_url,
            settings=settings,
            wsse=UsernameToken(username, password)
        )
    
    def get_workers(self, filters):
        try:
            header_factory = self.client.get_element('{urn:com.workday/bsvc}Workday_Common_Header')
            header_obj = header_factory(Include_Reference_Descriptors_In_Response=True)
            
            # Pass the entire filters dictionary as keyword arguments.
            response = self.client.service.Get_Workers(
                **filters,
                version="v43.2",
                _soapheaders=[header_obj]
            )
            
            serialized_response = serialize_object(response)
            print("Serialized SOAP Response (get_workers):")
            print(serialized_response)
            
            workers = serialized_response.get("Response_Data", {}).get("Worker", [])
            if not isinstance(workers, list):
                workers = [workers]
            return workers
        
        except Fault as fault:
            raise Exception(f"SOAP Fault: {fault}")
        except Exception as e:
            raise Exception(f"Failed to get workers: {str(e)}")
    
    def get_worker_by_reference(self, worker_id_value):
        try:
            header_factory = self.client.get_element('{urn:com.workday/bsvc}Workday_Common_Header')
            header_obj = header_factory(Include_Reference_Descriptors_In_Response=True)
            
            request_params = {
                "Request_References": {
                    "Worker_Reference": [
                        {"ID": [{"_value_1": worker_id_value, "type": "Employee_ID"}]}
                    ]
                }
            }
            
            response = self.client.service.Get_Workers(
                **request_params,
                version="v43.2",
                _soapheaders=[header_obj]
            )
            
            serialized_response = serialize_object(response)
            print("Serialized SOAP Response (get_worker_by_reference):")
            print(serialized_response)
            
            workers = serialized_response.get("Response_Data", {}).get("Worker", [])
            if not isinstance(workers, list):
                workers = [workers]
            return workers[0] if workers else {}
        
        except Fault as fault:
            raise Exception(f"SOAP Fault: {fault}")
        except Exception as e:
            raise Exception(f"Failed to get worker by reference: {str(e)}")

if __name__ == '__main__':
    from config import Config
    client = WorkdaySOAPClient(
        Config.WORKDAY_WSDL,
        "your_workday_username",
        "your_workday_password",
        Config.WORKDAY_TENANT
    )
    # Example test: pass the complete structure as filters.
    filters = {
      "Request_References": {
         "Skip_Non_Existing_Instances": False,
         "Ignore_Invalid_References": False,
         "Worker_Reference": [
           {
             "Descriptor": "Logan McNeil",
             "ID": [
               { "type": "WID", "_value_1": "3aa5550b7fe348b98d7b5741afc65534" },
               { "type": "Employee_ID", "_value_1": "21001" }
             ]
           }
         ]
      },
      "Request_Criteria": {
         "Exclude_Inactive_Workers": True,
         "Exclude_Employees": False,
         "Exclude_Contingent_Workers": False
      },
      "Response_Filter": {
         "Page": 1,
         "Count": 1,
         "As_Of_Effective_Date": "2022-01-01",
         "As_Of_Entry_DateTime": "2022-01-01T00:00:00"
      },
      "Response_Group": {
         "Include_Reference": True,
         "Include_Personal_Information": True,
         "Show_All_Personal_Information": True,
         "Include_Additional_Jobs": True,
         "Include_Employment_Information": True,
         "Include_Compensation": True,
         "Include_Organizations": True,
         "Exclude_Organization_Support_Role_Data": False,
         "Exclude_Location_Hierarchies": False,
         "Exclude_Cost_Centers": False,
         "Exclude_Cost_Center_Hierarchies": False,
         "Exclude_Companies": False,
         "Exclude_Company_Hierarchies": False,
         "Exclude_Matrix_Organizations": False,
         "Exclude_Pay_Groups": False,
         "Exclude_Regions": False,
         "Exclude_Region_Hierarchies": False,
         "Exclude_Supervisory_Organizations": False,
         "Exclude_Teams": False,
         "Exclude_Custom_Organizations": False,
         "Include_Roles": True,
         "Include_Management_Chain_Data": True,
         "Include_Multiple_Managers_in_Management_Chain_Data": True,
         "Include_Benefit_Enrollments": True,
         "Include_Benefit_Eligibility": True,
         "Include_Related_Persons": True,
         "Include_Qualifications": True,
         "Include_Employee_Review": True,
         "Include_Goals": True,
         "Include_Development_Items": True,
         "Include_Skills": True,
         "Include_Photo": True,
         "Include_Worker_Documents": True,
         "Include_Transaction_Log_Data": True,
         "Include_Subevents_for_Corrected_Transaction": True,
         "Include_Subevents_for_Rescinded_Transaction": True,
         "Include_Succession_Profile": True,
         "Include_Talent_Assessment": True,
         "Include_Employee_Contract_Data": True,
         "Include_Contracts_for_Terminated_Workers": True,
         "Include_Collective_Agreement_Data": True,
         "Include_Probation_Period_Data": True,
         "Include_Extended_Employee_Contract_Details": True,
         "Include_Feedback_Received": True,
         "Include_User_Account": True,
         "Include_Career": True,
         "Include_Account_Provisioning": True,
         "Include_Background_Check_Data": True,
         "Include_Contingent_Worker_Tax_Authority_Form_Information": True,
         "Exclude_Funds": False,
         "Exclude_Fund_Hierarchies": False,
         "Exclude_Grants": False,
         "Exclude_Grant_Hierarchies": False,
         "Exclude_Business_Units": False,
         "Exclude_Business_Unit_Hierarchies": False,
         "Exclude_Programs": False,
         "Exclude_Program_Hierarchies": False,
         "Exclude_Gifts": False,
         "Exclude_Gift_Hierarchies": False,
         "Exclude_Retiree_Organizations": False
      }
    }
    workers = client.get_workers(filters)
    print(workers)
