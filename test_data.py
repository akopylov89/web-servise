import types

CORREL_DIF = 0.000000000001
TYPES_COMPARE = (types.ComplexType, types.LongType,
                 types.IntType, types.FloatType)

test_uuid = "PAXTRA27775"
test_product_id = "CPVIEWS"
test_method = "POST"
test_output = ''

test_template = """
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns="http://schemas.reuters.com/ns/2007/07/snapshot">
    <soap:Header>
        <userIdentity xmlns="http://schemas.reuters.com/ns/2005/08/infrastructure/tornado_soap">
            <UUID xmlns="http://schemas.reuters.com/ns/2007/10/cp/user_identity">%s</UUID>
        </userIdentity>
        <transactionInfo xmlns="http://schemas.reuters.com/ns/2005/08/infrastructure/tornado_soap">
            <id></id>
        </transactionInfo>
        <timings xmlns="http://schemas.reuters.com/ns/2009/08/infrastructure/timings" />
    </soap:Header>
    <soap:Body>
        <selectReq productID='%s'>
            <formula>
                %s
            </formula>
            <identifiers>
                %s
            </identifiers>
            <output>
                %s
            </output>
        </selectReq>
    </soap:Body>
</soap:Envelope>
"""

test_headers = {"Accept": "text/javascript, text/html, application/xml, text/xml, */*",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest",
                "Content-type": "text/xml;charset=UTF-8; charset=UTF-8",
                "SOAPAction": "",
                "X-Prototype-Version": "1.7.1",
                "Connection": "keep-alive"}

server_dict = {
    'server1': {
        "Referer": "http://10.65.9.221/adcportal/",
        "Host": "10.65.9.221",
        "url": "10.65.9.221",
        "address": "/snapshot/snapshot.asmx"
    },
    'server2': {
        "Referer": "http://amers1.datacloud.cp.icp2.mpp.ime.reuters.com:1080/adcportal/",
        "Host": "amers1.datacloud.cp.icp2.mpp.ime.reuters.com:1080",
        "url": "amers1.datacloud.cp.icp2.mpp.ime.reuters.com:1080",
        "address": "/snapshot/snapshot.asmx"
    }
}
