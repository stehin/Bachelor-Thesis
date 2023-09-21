#IMPORT
import time
from functions import *
import csv

#Settings
HOST = "10.10.10.30"
PORT = 22
USERNAME = "username"
PASSWORD = "password"
policyMapName1 = "Eth-match-any-1"
classMapEthernetName1 = "ELINE_PM_1"
policyMapName2 = "Eth-match-any-2"
classMapEthernetName2 = "ELINE_PM_2"
EIR = 10000000
counters = [0, 0]
gigaBitsPerSecond = [0, 0]
i = 0
soglia = 1.5
picco = False
file = open("report.csv", "w", newline='')
writer = csv.writer(file)

m = start_session(HOST, PORT, USERNAME, PASSWORD) #instauro la sessione NETCONF
set_eir(m, policyMapName1, classMapEthernetName1, EIR) #setto l'eir al massimo per Eth-match-any-1
set_eir(m, policyMapName2, classMapEthernetName2, EIR) #setto l'eir al massimo per Eth-match-any-2

start_time = time.time()
localtime = time.localtime()
result = time.strftime("%I:%M:%S %p", localtime)
print("Orario inizio simulazione: %s" %result)
counters = get_counters(m) #prendo i valori iniziali
total_time = time.time() - start_time
time_sleep = 1 - total_time
time.sleep(time_sleep)

while True:
    start_time = time.time()
    localtime = time.localtime()
    result = time.strftime("%I:%M:%S %p", localtime)
    gigaBitsPerSecond, counters = get_Gbps_and_Counters(counters, m)
    writer.writerow([gigaBitsPerSecond[0], gigaBitsPerSecond[1]])
    if gigaBitsPerSecond[1] > soglia:
        picco = True
        print("Orario: %s, picco di traffico di G1" % result)
        print("precision:" + str(gigaBitsPerSecond[0]) + " Gbits/sec" + " --- G1:" + str(gigaBitsPerSecond[1]) + " Gbits/sec")
        set_cir(m, classMapEthernetName1, policyMapName1, 5000000)
        print("cir settato a 5 Gbits/sec")
        while picco == True and i <= 11: #qui decido il tempo da aspettare prima di ripristinare le politiche iniziali
            total_time = time.time() - start_time
            print("Tempo impiegato: %s secondi" % total_time)
            time_sleep = 1 - total_time
            time.sleep(time_sleep)
            start_time = time.time()
            localtime = time.localtime()
            result = time.strftime("%I:%M:%S %p", localtime)
            gigaBitsPerSecond, counters = get_Gbps_and_Counters(counters, m)
            writer.writerow([gigaBitsPerSecond[0], gigaBitsPerSecond[1]])
            if gigaBitsPerSecond[1] <= soglia:
                if i == 10:
                    picco = False
                    print("Orario: %s --- Il traffico di G1 è rientrato nei parametri" %result)
                    set_cir(m, classMapEthernetName1, policyMapName1, 0)
                    i = -1
                    total_time = time.time() - start_time
                    print("Tempo impiegato: %s secondi" % total_time)
                    time_sleep = 1 - total_time
                    time.sleep(time_sleep)

                else:
                    print("Orario: %s --- Il traffico di G1 sta rientrando nei parametri" % result)
                i += 1
            else:
                print("Orario: %s . Nuovo picco di traffico di G1" % result)
                i = 0
            print("precision:" + str(gigaBitsPerSecond[0]) + " Gbits/sec" + " --- G1:" + str(gigaBitsPerSecond[1]) + " Gbits/sec")
    else:
        print("Orario: %s . Traffico di G1 nella norma" %result)
        print("precision:" + str(gigaBitsPerSecond[0]) + " Gbits/sec " + "--- G1:" + str(
            gigaBitsPerSecond[1]) + " Gbits/sec")
        total_time = time.time() - start_time
        print("Tempo impiegato: %s secondi" % total_time)
        time_sleep = 1 - total_time
        time.sleep(time_sleep)
