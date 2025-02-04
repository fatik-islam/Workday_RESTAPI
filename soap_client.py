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

    The sample SOAP request in SOAP UI looks like this:

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

    Although the request XML uses <bsvc:Get_Workers_Request>, the WSDL defines the operation as Get_Workers.
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
        Instead of extracting only a few fields, this version returns the entire
        serialized worker object, which includes all available parameters such as
        email addresses, phone numbers, addresses, personal and employment details, etc.
        """
        try:
            # Create the SOAP header using the WSDL-defined element.
            header_factory = self.client.get_element('{urn:com.workday/bsvc}Workday_Common_Header')
            header_obj = header_factory()  # no subelements required

            # Call the Get_Workers operation with a Response_Group that requests personal information.
            response = self.client.service.Get_Workers(
                _soapheaders=[header_obj],
                version="v43.2",
                Response_Group={
                    "Include_Personal_Information": True,
                    "Include_Reference": True,
                    "Show_All_Personal_Information": False
                }
            )

            # Serialize the SOAP response into a Python dictionary.
            serialized_response = serialize_object(response)
            print("Serialized SOAP Response (get_workers):")
            print(serialized_response)

            # Get the list of workers from the Response_Data.
            workers = serialized_response.get("Response_Data", {}).get("Worker", [])
            if not isinstance(workers, list):
                workers = [workers]

            # Return the complete worker objects as received.
            return workers

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
