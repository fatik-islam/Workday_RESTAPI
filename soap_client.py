#!/usr/bin/env python3
from zeep import Client, Settings, xsd
from zeep.exceptions import Fault
from zeep.wsse.username import UsernameToken
from zeep.helpers import serialize_object

class WorkdaySOAPClient:
    """
    A wrapper class for interacting with the Workday SOAP API using WS‑Security.
    This implementation calls the Get_Workers operation so that the outgoing SOAP envelope
    matches the SoapUI sample.

    The SOAP envelope sample from SoapUI:

    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
                      xmlns:bsvc="urn:com.workday/bsvc">
        <soapenv:Header>
            <bsvc:Workday_Common_Header>
                <!-- No mandatory sub-elements required here -->
            </bsvc:Workday_Common_Header>
        </soapenv:Header>
        <soapenv:Body>
            <bsvc:Get_Workers_Request bsvc:version="v43.2">
                <!-- No mandatory sub-elements required here -->
            </bsvc:Get_Workers_Request>
        </soapenv:Body>
    </soapenv:Envelope>

    Although the XML sample uses <bsvc:Get_Workers_Request>, the actual WSDL defines the operation as Get_Workers.
    """

    def __init__(self, wsdl_url, username, password, tenant):
        self.wsdl_url = wsdl_url
        self.username = username
        self.password = password
        self.tenant = tenant

        settings = Settings(strict=False, xml_huge_tree=True)
        self.client = Client(
            wsdl=self.wsdl_url,
            settings=settings,
            wsse=UsernameToken(self.username, self.password)
        )

    def get_workers(self):
        """
        Retrieves a list of workers by calling the SOAP operation Get_Workers.
        The response is serialized, and Worker_ID, First_Name, Last_Name, and Email are extracted.
        """
        try:
            # Create the SOAP header using the WSDL-defined element and wrap it in a list.
            header_factory = self.client.get_element('{urn:com.workday/bsvc}Workday_Common_Header')
            header_obj = header_factory()  # no subelements required

            # Include a Response_Group to request personal information.
            response = self.client.service.Get_Workers(
                _soapheaders=[header_obj],
                version="v43.2",
                Response_Group={
                    "Include_Personal_Information": True,
                    "Include_Reference": True,
                    "Show_All_Personal_Information": False
                }
            )

            serialized_response = serialize_object(response)
            print("Serialized SOAP Response (get_workers):")
            print(serialized_response)

            workers_list = []
            workers = serialized_response.get("Response_Data", {}).get("Worker", [])
            if not isinstance(workers, list):
                workers = [workers]

            for worker in workers:
                worker_data = worker.get("Worker_Data", {})
                worker_id = worker_data.get("Worker_ID")

                # Process the personal data to extract name details.
                personal_data = worker_data.get("Personal_Data", {})
                name_data = personal_data.get("Name_Data", {})

                legal_name = name_data.get("Legal_Name_Data", {})
                # Check if Legal_Name_Data has a nested Name_Detail_Data
                if "Name_Detail_Data" in legal_name:
                    name_detail = legal_name.get("Name_Detail_Data", {})
                    first_name = name_detail.get("First_Name")
                    last_name = name_detail.get("Last_Name")
                else:
                    first_name = legal_name.get("First_Name")
                    last_name = legal_name.get("Last_Name")

                # Process the contact data (if available)
                contact_data = worker_data.get("Contact_Data", {})
                email_list = contact_data.get("Email_Address_Data", [])
                email = None
                if isinstance(email_list, list) and email_list:
                    email = email_list[0].get("Email_Address")
                elif isinstance(email_list, dict):
                    email = email_list.get("Email_Address")

                workers_list.append({
                    "Worker_ID": worker_id,
                    "First_Name": first_name,
                    "Last_Name": last_name,
                    "Email": email
                })
            return workers_list

        except Fault as fault:
            raise Exception(f"SOAP Fault: {fault}")
        except Exception as e:
            raise Exception(f"Failed to get workers: {str(e)}")

if __name__ == '__main__':
    # For testing purposes only – replace with your actual Workday credentials.
    wsdl_url = "https://wd2-impl-services1.workday.com/ccx/service/ibmsrv_pt1/Human_Resources/v43.2?wsdl"
    username = "your_username"
    password = "your_password"
    tenant = "your_tenant"
    
    client = WorkdaySOAPClient(wsdl_url, username, password, tenant)
    workers = client.get_workers()
    for w in workers:
        print(w)

