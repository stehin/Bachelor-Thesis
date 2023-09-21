from ncclient import manager
import xml.etree.ElementTree as ET
#fUNZIONI UTILIZZATE

"""INSTAURA LA SESSIONE NETCONF UTILIZZANDO MANAGER DI NCCLIENT, PRENDENDO IN INGRESSO I PARAMETRI HOST, PORT, USERNAME,
E PASSWORD, RESTITUENDO LA SESSIONE NETCONF INSTAURATA, CHE UTILIZZEREMO PER TUTTO IL PROGETTO"""
def start_session(HOST, PORT, USERNAME, PASSWORD):
    m = manager.connect_ssh(
        host=HOST,
        port=PORT,
        username=USERNAME,
        password=PASSWORD)
    return m

"""RESTITUISCE IL VALORE DEI CONTATORI (BYTES FLOW-COUNTERS), E PRENDE IN INGRESSO LA SESSIONE NETCONF.
UTILE PER INIZIALIZZARE I VALORI DEI CONTATORI ALLA PRIMA CHIAMATA DI get_Bps_and_counters"""
def get_counters(m):
    bytesCounter=[0, 0]
    # traffico in upstream
    QUERY_Bytes = '''
              <filter>
             <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
      		  <interface>
        		 <ont-ethernet xmlns="http://www.calix.com/ns/exa/gpon-interface-std">
          		  <flow-counters>
            	   <per-flow-counter-index>
              		<bytes/>
              		<if-name></if-name>
              		<direction>ingress</direction>
            	   </per-flow-counter-index>
         		 </flow-counters>
        		</ont-ethernet>
      	      </interface>
     	     </interfaces-state>
     	     </filter>
              '''

    #NB, STO USANDO IL TRAFFICO IN DOWNSTREAM PER TESTARE CON LA RISPOSTA AL PING. PER LA TESI CAMBIA IL FILTRO IN PROVE
    netconf_reply = m.get(filter=QUERY_Bytes)

    root1 = ET.fromstring(netconf_reply.xml)

    i = 0
    for bytes in root1.findall('.//{*}bytes'):
        bytesCounter[i] = int(bytes.text)
        #print(i, bytesCounter[i])
        i+=1
    return bytesCounter

"""RESTITUISCE LA DIFFERENZA TRA I VALORI DEI CONTATORI (CALCOLATTI CON UNA GET, CAMPIONATI ALL'ISTANTE DELLA CHIAMATA)
 E I PARAMETRI (I VALORI DEI CONTATORI CALCOLATI ALL ITSTANTE PRECEDENTE) PASSATI ALLA FUNZIONE, ED I VALORI DEI CONTATORI 
  AGGIORNATI AL MOMENTO DELLA CHIAMATA. RICHIEDE COME PARAMETRI APPUNTO I VALORI INIZIALI DEI CONTATORI, ALL'INTERNO DI UNA LISTA,
E LA SESSIONE NETCONF"""
def get_Gbps_and_Counters(startValues, m):

    gigaBitsNumber=[0,0]
    endValues=[0, 0]
    QUERY_Bytes = '''
             <filter>
             <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
      		  <interface>
        		 <ont-ethernet xmlns="http://www.calix.com/ns/exa/gpon-interface-std">
          		  <flow-counters>
            	   <per-flow-counter-index>
              		<bytes/>
              		<if-name></if-name>
              		<direction>ingress</direction>
            	   </per-flow-counter-index>
         		 </flow-counters>
        		</ont-ethernet>
      	      </interface>
     	     </interfaces-state>
     	     </filter>
              '''

    netconf_reply = m.get(filter=QUERY_Bytes)

    root1 = ET.fromstring(netconf_reply.xml)
    i = 0
    for bytes in root1.findall('.//{*}bytes'):
        endValues[i] = int(bytes.text)
        i+=1

    for j in range(len(gigaBitsNumber)):
        gigaBitsNumber[j] = round(((endValues[j]-startValues[j])*8)/1000000000,2)


    return gigaBitsNumber, endValues

def _check_response(rpc_obj, snippet_name):
    check = False
    print("RPCReply for %s is %s" % (snippet_name, rpc_obj.xml))
    xml_str = rpc_obj.xml
    if "<ok/>" in xml_str:
        print("%s successful" % snippet_name)
        check = True
    else:
        print("Cannot successfully execute: %s" % snippet_name)

def set_cir(m, policyMapName, classMapEthernetName, cir):
    cirSTR= str(cir)
    CONFIGURE_cir1 = """
              <config>
        	  <config xmlns="http://www.calix.com/ns/exa/base">
        	   <profile>
        	    <policy-map>
        	    <name>"""

    CONFIGURE_cir2="""</name>
        	     <class-map-ethernet>
        	     <name>"""
    CONFIGURE_cir3="""</name>
        	     <ingress>
        	      <meter-type>meter-mef</meter-type>
        	      <cir>"""
    CONFIGURE_cir4 = """</cir>
        	     </ingress> 
        	     </class-map-ethernet>
        	    </policy-map>
        	   </profile>
        	  </config>  
        	  </config>  
        	  """
    # traffico in upstream, guarda flow id

    CONFIGURE_cir = CONFIGURE_cir1 + policyMapName + CONFIGURE_cir2 + classMapEthernetName + CONFIGURE_cir3 + cirSTR + CONFIGURE_cir4
    rpc_response = m.edit_config(target="running", config=CONFIGURE_cir)
    cirInGbits = round(cir/1000000000,2)
    if _check_response(rpc_response, "CHANGING cir") == True:
        print("cir settato a %s Gbits/sec" %cirInGbits)

def set_eir(m, policyMapName, classMapEthernetName, eir):
    eirSTR= str(eir)
    CONFIGURE_eir1 = """
              <config>
        	  <config xmlns="http://www.calix.com/ns/exa/base">
        	   <profile>
        	    <policy-map>
        	    <name>"""

    CONFIGURE_eir2="""</name>
        	     <class-map-ethernet>
        	     <name>"""
    CONFIGURE_eir3="""</name>
        	     <ingress>
        	      <meter-type>meter-mef</meter-type>
        	      <eir>"""
    CONFIGURE_eir4 = """</eir>
        	     </ingress> 
        	     </class-map-ethernet>
        	    </policy-map>
        	   </profile>
        	  </config>  
        	  </config>  
        	  """
    CONFIGURE_eir = CONFIGURE_eir1 + policyMapName + CONFIGURE_eir2 + classMapEthernetName + CONFIGURE_eir3 + eirSTR + CONFIGURE_eir4
    rpc_response = m.edit_config(target="running", config=CONFIGURE_eir)
    eirInGbits = round(eir / 1000000000, 2)
    if _check_response(rpc_response, "CHANGING cir") == True:
        print("eir settato a %s Gbits/sec" % eirInGbits)
