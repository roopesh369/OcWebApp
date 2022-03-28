import requests
import pandas as pd
import streamlit as st


url1 = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
url2 = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'accept-encoding': 'gzip,deflate',
    'accept-language': 'en-US,en;q=0.9'
}
session = requests.Session()
request = session.get(url1, headers=headers)
cookies = dict(request.cookies)
response1 = session.get(url1, headers=headers).json()
#response1 = session.get(url1, headers=headers, cookies=cookies).json()
NiftyAllE = pd.DataFrame(response1)
NiftyNE = pd.DataFrame(NiftyAllE['filtered']['data']).fillna(0)

#response2 = session.get(url2, headers=headers, cookies=cookies).json()
response2 = session.get(url2, headers=headers).json()
BNiftyAllE = pd.DataFrame(response2)
BNiftyNE = pd.DataFrame(BNiftyAllE['filtered']['data']).fillna(0)


def rtm(number, multiple):
    return multiple * round(number / multiple)


def processOIdata(rawop):
    data = []
    for i in range(0, len(rawop)):
        calloi = callcoi = cltp = cvol = putoi = putcoi = pltp = pvol = uval = 0
        stp = rawop['strikePrice'][i]
        expdate = rawop['expiryDate'][i]
        if rawop['CE'][i] == 0:
            calloi = callcoi = 0
        else:
            calloi = rawop['CE'][i]['openInterest']
            callcoi = rawop['CE'][i]['changeinOpenInterest']
            cltp = rawop['CE'][i]['lastPrice']
            cvol = rawop['CE'][i]['totalTradedVolume']
            uval = rawop['CE'][i]['underlyingValue']
        if rawop['PE'][i] == 0:
            putoi = putcoi = 0
        else:
            putoi = rawop['PE'][i]['openInterest']
            putcoi = rawop['PE'][i]['changeinOpenInterest']
            pltp = rawop['PE'][i]['lastPrice']
            pvol = rawop['PE'][i]['totalTradedVolume']
        opdata = {
            'CE.oi': calloi, 'CE.coi': callcoi, 'CE.ltp': cltp, 'CE.vol': cvol,
            'PE.oi': putoi, 'PE.coi': putcoi, 'PE.ltp': pltp, 'PE.vol': pvol,
            'STP': stp, 'xdate': expdate, 'Uvalue': uval
        }
        data.append(opdata)
    processeddata = pd.DataFrame(data)
    return processeddata


def calPCR(ocdata, indx):
    data = []
    start = indx - 8
    end = indx + 8
    i = start
    while i <= end:
        calloi = callcoi = callvol = putoi = putcoi = putvol = stp = 0
        calloi = ocdata['CE.oi'][i]
        callcoi = ocdata['CE.coi'][i]
        callvol = ocdata['CE.vol'][i]
        putoi = ocdata['PE.oi'][i]
        putcoi = ocdata['PE.coi'][i]
        putvol = ocdata['PE.vol'][i]
        stp = ocdata['STP'][i]
        idata = {
            'CE.oi': calloi, 'CE.coi': callcoi, 'CE.vol': callvol, 'STP': stp,
            'PE.oi': putoi, 'PE.coi': putcoi, 'PE.vol': putvol
        }
        data.append(idata)
        i = i + 1
    resultdata = pd.DataFrame(data)
    return (resultdata)


st.write("Helo Roopesh Sharma")

niftyOC = processOIdata(NiftyNE)
bniftyOC = processOIdata(BNiftyNE)

# Find underlying value

uvNifty = niftyOC['Uvalue'][1]
uvBNifty = bniftyOC['Uvalue'][1]
nstp = rtm(uvNifty, 50)
bnstp = rtm(uvBNifty, 100)
niftyIN = niftyOC[niftyOC['STP'] == nstp].index.values.astype(int)[0]
bniftyIN = bniftyOC[bniftyOC['STP'] == bnstp].index.values.astype(int)[0]
# bniftyIN =bniftyOC.loc[bniftyOC['STP'] == bnstp].index.values.astype(int)
niftyrows = calPCR(niftyOC, niftyIN)
bniftyrows = calPCR(bniftyOC, bniftyIN)
tnCEcoi = niftyrows['CE.coi'].sum()
tnPEcoi = niftyrows['PE.coi'].sum()
nDiff = tnPEcoi - tnCEcoi
nPcr = abs(tnPEcoi / tnCEcoi)
tbnCEcoi = bniftyrows['CE.coi'].sum()
tbnPEcoi = bniftyrows['PE.coi'].sum()
bnDiff = tbnPEcoi - tbnCEcoi
bnPcr = abs(tbnPEcoi / tbnCEcoi)
# st.write(niftyOC)
# st.write(bniftyOC)
st.write("NIFTY", niftyrows)
st.write("Total CE.coi = ", tnCEcoi, "Total PE.coi = ", tnPEcoi, "Diff = ", nDiff)
st.write("PCR = ", nPcr)

st.write("BANK NIFTY", bniftyrows)
st.write("Total CE.coi = ", tbnCEcoi, "Total PE.coi = ", tbnPEcoi, "Diff = ", bnDiff)
st.write("PCR = ", bnPcr)
