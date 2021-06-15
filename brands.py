import pandas as pd
import numpy as np
from sklearn import manifold
import matplotlib.pyplot as plt
import seaborn as sns

models = pd.read_csv(r"C:\Users\Nupur\OneDrive - McGill University\Desktop\McGill Notes\Text Analytics\models_new.csv",header=None)

models['lowered'] = models.apply(lambda row: row[1].lower(), axis=1)

lookup = dict(zip(models["lowered"],models[0]))

# TO CONVERT TO LIST AGAIN

huh = pd.read_csv(r"C:\Users\Nupur\OneDrive - McGill University\Desktop\McGill Notes\Text Analytics\preprocessed_comments2.csv")

huh['fun'] = np.empty(len(huh),dtype=list)

for i in range(len(huh)): 
    huh["fun"][i] = huh["normalized"][i].split("', u'")
    huh["fun"][i][-1] = huh["fun"][i][-1][:-2]
    huh["fun"][i][0] = huh["fun"][i][0][3:]

# get a list of potential words

unique_words = []

for i in huh["fun"]:
    for j in i:
        if not j in unique_words:
            unique_words.append(j)

# check if this worked
values, counts = np.unique(unique_words, return_counts=True)
sum(counts) == len(unique_words)


frequencies_words = pd.DataFrame()
frequencies_words = frequencies_words.assign(Brands = unique_words)
frequencies_words["count"] = 0


for i in huh["fun"]:
    for j in range(len(frequencies_words)):
        if frequencies_words["Brands"][j] in i:
            frequencies_words["count"][j] +=1

frequencies_words = frequencies_words.sort_values(by=["count"],ascending=False)

# to test counts
frequencies_words[frequencies_words["Brands"]=="front"]

# to test if sequences appear
# for sequences of 3
def check_sequence_3(arr,check):
    counter = 0
    for i in range(len(arr)):
        for j in range(len(arr[i])-2):
            if check == [arr[i][j],arr[i][j+1],arr[i][j+2]]:
                counter += 1
                break
    return counter

check_sequence_3(huh["fun"],["front","wheel","drive"])

# for sequences of 2
def check_sequence_2(arr,check):
    counter = 0
    for i in range(len(arr)):
        for j in range(len(arr[i])-1):
            if check == [arr[i][j],arr[i][j+1]]:
                counter += 1
                break
    return counter

check_sequence_2(huh["fun"],["hatch","back"])

huh['shrunk'] = np.empty(len(huh),dtype=list)

associations = {"fwd":"drivetrain", "awd":"drivetrain", "rwd":"drivetrain",
                "hp":"performance", "horsepower":"performance", "acceleration":"performance","torque":"performance","perform":"performance",
                "money":"price","cheap":"price","expensive":"price","value":"price","pricey":"price","overprice":"price",
                "cheaper":"price","costlier":"price","costly":"price","cheapest":"price","midprice":"price","cost":"price",
                "luxury":"price","premium":"price","inexpensive":"price","problematic":"problem","noisiest":"problem",
                "issue":"problem","lemon":"problem","repair":"problem","fix":"problem","trouble":"problem"}

for j in range(len(huh)):
    temp = []
    for p in huh["fun"][j]:
        if p in associations:
            temp.append(associations[p])
        else:
            temp.append(p)
    huh["shrunk"][j] = temp

#replace the sequences

def replace(sequence, replacement, lst, expand=False):
    out = list(lst)
    for i, e in enumerate(lst):
        if e == sequence[0]:
            i1 = i
            f = 1
            for e1, e2 in zip(sequence, lst[i:]):
                if e1 != e2:
                    f = 0
                    break
                i1 += 1
            if f == 1:
                del out[i:i1]
                if expand:
                    for x in list(replacement):
                        out.insert(i, x)
                else:
                    out.insert(i, replacement)
    return out


temp = []
for i in huh["shrunk"]:
    temp.append(replace(["front","wheel","drive"],"drivetrain",i))

temp2 = []
for i in temp:
    temp2.append(replace(["rear","wheel","drive"],"drivetrain",i))

huh["morefun"] = temp2



# redo the list

unique_words = []

for i in huh["morefun"]:
    for j in i:
        if not j in unique_words:
            unique_words.append(j)

# check if this worked
values, counts = np.unique(unique_words, return_counts=True)
sum(counts) == len(unique_words)

frequencies_words = pd.DataFrame()
frequencies_words = frequencies_words.assign(Brands = unique_words)
frequencies_words["count"] = 0


for i in huh["morefun"]:
    for j in range(len(frequencies_words)):
        if frequencies_words["Brands"][j] in i:
            frequencies_words["count"][j] +=1

frequencies_words = frequencies_words.sort_values(by=["count"],ascending=False)

# make list of unique brands

unique_brands = []

for i in models[0]:
    if not i in unique_brands:
        unique_brands.append(i)

brand_counts = frequencies_words[frequencies_words.Brands.isin(unique_brands)]


# bunch of stuff in here that aren't brands

brand_counts.drop(brand_counts[brand_counts["Brands"]=="car"].index,inplace=True)
brand_counts.drop(brand_counts[brand_counts["Brands"]=="problem"].index,inplace=True)
brand_counts.drop(brand_counts[brand_counts["Brands"]=="seat"].index,inplace=True)
brand_counts.drop(brand_counts[brand_counts["Brands"]=="sedan"].index,inplace=True)

# THIS IS TOP TEN BRANDS BY FREQUENCY

TopTenBrands = brand_counts["Brands"].head(10).tolist()

BrandsForAssociation = ["bmw","chrysler","acura","honda","audi","infiniti","nissan","lexus","toyota","cadillac"]

so_confuse = pd.MultiIndex.from_product([TopTenBrands,BrandsForAssociation],names=["Brand1","Brand2"])

brand_associations = pd.DataFrame(index = so_confuse).reset_index()

brand_associations["comentions"] = 0



for i in huh["morefun"]:
    for j in range(len(brand_associations)):
        if brand_associations["Brand1"][j] in i and brand_associations["Brand2"][j] in i:
            brand_associations["comentions"][j] +=1

#brand_associations.to_csv(r"C:\Users\Nupur\OneDrive - McGill University\Desktop\McGill Notes\Text Analytics\Brand_associations.csv")

#Lift Ratios

sample = 5000

#Lift Ratios - BMW
LRBC = (brand_associations.iloc[1]["comentions"]*sample)/(brand_associations.iloc[0]["comentions"]*brand_associations.iloc[11]["comentions"])
LRBA = (brand_associations.iloc[2]["comentions"]*sample)/(brand_associations.iloc[0]["comentions"]*brand_associations.iloc[22]["comentions"])
LRBH = (brand_associations.iloc[3]["comentions"]*sample)/(brand_associations.iloc[0]["comentions"]*brand_associations.iloc[33]["comentions"])
LRBAU = (brand_associations.iloc[4]["comentions"]*sample)/(brand_associations.iloc[0]["comentions"]*brand_associations.iloc[44]["comentions"])
LRBI = (brand_associations.iloc[5]["comentions"]*sample)/(brand_associations.iloc[0]["comentions"]*brand_associations.iloc[55]["comentions"])
LRBN = (brand_associations.iloc[6]["comentions"]*sample)/(brand_associations.iloc[0]["comentions"]*brand_associations.iloc[66]["comentions"])
LRBL = (brand_associations.iloc[7]["comentions"]*sample)/(brand_associations.iloc[0]["comentions"]*brand_associations.iloc[77]["comentions"])
LRBT = (brand_associations.iloc[8]["comentions"]*sample)/(brand_associations.iloc[0]["comentions"]*brand_associations.iloc[88]["comentions"])
LRBCA = (brand_associations.iloc[9]["comentions"]*sample)/(brand_associations.iloc[0]["comentions"]*brand_associations.iloc[99]["comentions"])

#Inverse Lift Ratios - BMW

INBC = 1/LRBC
INBA = 1/LRBA
INBH = 1/LRBH
INBAU = 1/LRBAU
INBI =1/LRBI
INBN= 1/LRBN
INBL= 1/LRBL
INBT = 1/LRBT
INBCA = 1/LRBCA

#Lift Ratios - Chrysler
LRCB = (brand_associations.iloc[10]["comentions"]*sample)/(brand_associations.iloc[11]["comentions"]*brand_associations.iloc[0]["comentions"])
LRCA = (brand_associations.iloc[12]["comentions"]*sample)/(brand_associations.iloc[11]["comentions"]*brand_associations.iloc[22]["comentions"])
LRCH = (brand_associations.iloc[13]["comentions"]*sample)/(brand_associations.iloc[11]["comentions"]*brand_associations.iloc[33]["comentions"])
LRCAU = (brand_associations.iloc[14]["comentions"]*sample)/(brand_associations.iloc[11]["comentions"]*brand_associations.iloc[44]["comentions"])
LRCI = (brand_associations.iloc[15]["comentions"]*sample)/(brand_associations.iloc[11]["comentions"]*brand_associations.iloc[55]["comentions"])
LRCN = (brand_associations.iloc[16]["comentions"]*sample)/(brand_associations.iloc[11]["comentions"]*brand_associations.iloc[66]["comentions"])
LRCL = (brand_associations.iloc[17]["comentions"]*sample)/(brand_associations.iloc[11]["comentions"]*brand_associations.iloc[77]["comentions"])
LRCT = (brand_associations.iloc[18]["comentions"]*sample)/(brand_associations.iloc[11]["comentions"]*brand_associations.iloc[88]["comentions"])
LRCCA = (brand_associations.iloc[19]["comentions"]*sample)/(brand_associations.iloc[11]["comentions"]*brand_associations.iloc[99]["comentions"])


#Inverse Lift Ratios - Chrysler

INCB = 1/LRCB
INCA = 1/LRCA
INCH = 1/LRCH
INCAU = 1/LRCAU
INCI =1/LRCI
INCN= 1/LRCN
INCL= 1/LRCL
INCT = 1/LRCT
INCCA = 1/LRCCA


#Lift Ratios - Acura
LRAB = (brand_associations.iloc[20]["comentions"]*sample)/(brand_associations.iloc[22]["comentions"]*brand_associations.iloc[0]["comentions"])
LRAC = (brand_associations.iloc[21]["comentions"]*sample)/(brand_associations.iloc[22]["comentions"]*brand_associations.iloc[11]["comentions"])
LRAH = (brand_associations.iloc[23]["comentions"]*sample)/(brand_associations.iloc[22]["comentions"]*brand_associations.iloc[33]["comentions"])
LRAAU = (brand_associations.iloc[24]["comentions"]*sample)/(brand_associations.iloc[22]["comentions"]*brand_associations.iloc[44]["comentions"])
LRAI = (brand_associations.iloc[25]["comentions"]*sample)/(brand_associations.iloc[22]["comentions"]*brand_associations.iloc[55]["comentions"])
LRAN = (brand_associations.iloc[26]["comentions"]*sample)/(brand_associations.iloc[22]["comentions"]*brand_associations.iloc[66]["comentions"])
LRAL = (brand_associations.iloc[27]["comentions"]*sample)/(brand_associations.iloc[22]["comentions"]*brand_associations.iloc[77]["comentions"])
LRAT = (brand_associations.iloc[28]["comentions"]*sample)/(brand_associations.iloc[22]["comentions"]*brand_associations.iloc[88]["comentions"])
LRACA = (brand_associations.iloc[29]["comentions"]*sample)/(brand_associations.iloc[22]["comentions"]*brand_associations.iloc[99]["comentions"])

#Inverse Lift Ratios - Acura

INAB = 1/LRAB
INAC = 1/LRAC
INAH = 1/LRAH
INAAU = 1/LRAAU
INAI =1/LRAI
INAN= 1/LRAN
INAL= 1/LRAL
INAT = 1/LRAT
INACA = 1/LRACA

#Lift Ratios - Honda
LRHB = (brand_associations.iloc[30]["comentions"]*sample)/(brand_associations.iloc[33]["comentions"]*brand_associations.iloc[0]["comentions"])
LRHC = (brand_associations.iloc[31]["comentions"]*sample)/(brand_associations.iloc[33]["comentions"]*brand_associations.iloc[11]["comentions"])
LRHA = (brand_associations.iloc[32]["comentions"]*sample)/(brand_associations.iloc[33]["comentions"]*brand_associations.iloc[22]["comentions"])
LRHAU = (brand_associations.iloc[34]["comentions"]*sample)/(brand_associations.iloc[33]["comentions"]*brand_associations.iloc[44]["comentions"])
LRHI = (brand_associations.iloc[35]["comentions"]*sample)/(brand_associations.iloc[33]["comentions"]*brand_associations.iloc[55]["comentions"])
LRHN = (brand_associations.iloc[36]["comentions"]*sample)/(brand_associations.iloc[33]["comentions"]*brand_associations.iloc[66]["comentions"])
LRHL = (brand_associations.iloc[37]["comentions"]*sample)/(brand_associations.iloc[33]["comentions"]*brand_associations.iloc[77]["comentions"])
LRHT = (brand_associations.iloc[38]["comentions"]*sample)/(brand_associations.iloc[33]["comentions"]*brand_associations.iloc[88]["comentions"])
LRHCA = (brand_associations.iloc[39]["comentions"]*sample)/(brand_associations.iloc[33]["comentions"]*brand_associations.iloc[99]["comentions"])

#Inverse Lift Ratios - Honda

INHB = 1/LRHB
INHC = 1/LRHC
INHA = 1/LRHA
INHAU = 1/LRHAU
INHI =1/LRHI
INHN= 1/LRHN
INHL= 1/LRHL
INHT = 1/LRHT
INHCA = 1/LRHCA



#Lift Ratios - Audi
LRAUB = (brand_associations.iloc[40]["comentions"]*sample)/(brand_associations.iloc[44]["comentions"]*brand_associations.iloc[0]["comentions"])
LRAUC = (brand_associations.iloc[41]["comentions"]*sample)/(brand_associations.iloc[44]["comentions"]*brand_associations.iloc[11]["comentions"])
LRAUA = (brand_associations.iloc[42]["comentions"]*sample)/(brand_associations.iloc[44]["comentions"]*brand_associations.iloc[22]["comentions"])
LRAUH = (brand_associations.iloc[43]["comentions"]*sample)/(brand_associations.iloc[44]["comentions"]*brand_associations.iloc[33]["comentions"])
LRAUI = (brand_associations.iloc[45]["comentions"]*sample)/(brand_associations.iloc[44]["comentions"]*brand_associations.iloc[55]["comentions"])
LRAUN = (brand_associations.iloc[46]["comentions"]*sample)/(brand_associations.iloc[44]["comentions"]*brand_associations.iloc[66]["comentions"])
LRAUL = (brand_associations.iloc[47]["comentions"]*sample)/(brand_associations.iloc[44]["comentions"]*brand_associations.iloc[77]["comentions"])
LRAUT = (brand_associations.iloc[48]["comentions"]*sample)/(brand_associations.iloc[44]["comentions"]*brand_associations.iloc[88]["comentions"])
LRAUCA = (brand_associations.iloc[49]["comentions"]*sample)/(brand_associations.iloc[44]["comentions"]*brand_associations.iloc[99]["comentions"])


#Inverse Lift Ratios - Audi

INAUB = 1/LRAUB
INAUC = 1/LRAUC
INAUA = 1/LRAUA
INAUH = 1/LRAUH
INAUI =1/LRAUI
INAUN= 1/LRAUN
INAUL= 1/LRAUL
INAUT = 1/LRAUT
INAUCA = 1/LRAUCA



#Lift Ratios - Infiniti
LRIB = (brand_associations.iloc[50]["comentions"]*sample)/(brand_associations.iloc[55]["comentions"]*brand_associations.iloc[0]["comentions"])
LRIC = (brand_associations.iloc[51]["comentions"]*sample)/(brand_associations.iloc[55]["comentions"]*brand_associations.iloc[11]["comentions"])
LRIA = (brand_associations.iloc[52]["comentions"]*sample)/(brand_associations.iloc[55]["comentions"]*brand_associations.iloc[22]["comentions"])
LRIH = (brand_associations.iloc[53]["comentions"]*sample)/(brand_associations.iloc[55]["comentions"]*brand_associations.iloc[33]["comentions"])
LRIAU = (brand_associations.iloc[54]["comentions"]*sample)/(brand_associations.iloc[55]["comentions"]*brand_associations.iloc[44]["comentions"])
LRIN = (brand_associations.iloc[56]["comentions"]*sample)/(brand_associations.iloc[55]["comentions"]*brand_associations.iloc[66]["comentions"])
LRIL = (brand_associations.iloc[57]["comentions"]*sample)/(brand_associations.iloc[55]["comentions"]*brand_associations.iloc[77]["comentions"])
LRIT = (brand_associations.iloc[58]["comentions"]*sample)/(brand_associations.iloc[55]["comentions"]*brand_associations.iloc[88]["comentions"])
LRICA = (brand_associations.iloc[59]["comentions"]*sample)/(brand_associations.iloc[55]["comentions"]*brand_associations.iloc[99]["comentions"])

#Inverse Lift Ratios - Infiniti

INIB = 1/LRIB
INIC = 1/LRIC
INIA = 1/LRIA
INIH = 1/LRIH
INIAU =1/LRIAU
ININ= 1/LRIN
INIL= 1/LRIL
INIT = 1/LRIT
INICA = 1/LRICA


#Lift Ratios - Nissan
LRNB = (brand_associations.iloc[60]["comentions"]*sample)/(brand_associations.iloc[66]["comentions"]*brand_associations.iloc[0]["comentions"])
LRNC = (brand_associations.iloc[61]["comentions"]*sample)/(brand_associations.iloc[66]["comentions"]*brand_associations.iloc[11]["comentions"])
LRNA = (brand_associations.iloc[62]["comentions"]*sample)/(brand_associations.iloc[66]["comentions"]*brand_associations.iloc[22]["comentions"])
LRNH = (brand_associations.iloc[63]["comentions"]*sample)/(brand_associations.iloc[66]["comentions"]*brand_associations.iloc[33]["comentions"])
LRNAU = (brand_associations.iloc[64]["comentions"]*sample)/(brand_associations.iloc[66]["comentions"]*brand_associations.iloc[44]["comentions"])
LRNI = (brand_associations.iloc[65]["comentions"]*sample)/(brand_associations.iloc[66]["comentions"]*brand_associations.iloc[55]["comentions"])
LRNL = (brand_associations.iloc[67]["comentions"]*sample)/(brand_associations.iloc[66]["comentions"]*brand_associations.iloc[77]["comentions"])
LRNT = (brand_associations.iloc[68]["comentions"]*sample)/(brand_associations.iloc[66]["comentions"]*brand_associations.iloc[88]["comentions"])
LRNCA = (brand_associations.iloc[69]["comentions"]*sample)/(brand_associations.iloc[66]["comentions"]*brand_associations.iloc[99]["comentions"])


#Inverse Lift Ratios - Nissan

INNB = 1/LRNB
INNC = 1/LRNC
INNA = 1/LRNA
INNH = 1/LRNH
INNAU =1/LRNAU
INNI= 1/LRNI
INNL= 1/LRNL
INNT = 1/LRNT
INNCA = 1/LRNCA


#Lift Ratios - Lexus
LRLB = (brand_associations.iloc[70]["comentions"]*sample)/(brand_associations.iloc[77]["comentions"]*brand_associations.iloc[0]["comentions"])
LRLC = (brand_associations.iloc[71]["comentions"]*sample)/(brand_associations.iloc[77]["comentions"]*brand_associations.iloc[11]["comentions"])
LRLA = (brand_associations.iloc[72]["comentions"]*sample)/(brand_associations.iloc[77]["comentions"]*brand_associations.iloc[22]["comentions"])
LRLH = (brand_associations.iloc[73]["comentions"]*sample)/(brand_associations.iloc[77]["comentions"]*brand_associations.iloc[33]["comentions"])
LRLAU = (brand_associations.iloc[74]["comentions"]*sample)/(brand_associations.iloc[77]["comentions"]*brand_associations.iloc[44]["comentions"])
LRLI = (brand_associations.iloc[75]["comentions"]*sample)/(brand_associations.iloc[77]["comentions"]*brand_associations.iloc[55]["comentions"])
LRLN = (brand_associations.iloc[76]["comentions"]*sample)/(brand_associations.iloc[77]["comentions"]*brand_associations.iloc[66]["comentions"])
LRLT = (brand_associations.iloc[78]["comentions"]*sample)/(brand_associations.iloc[77]["comentions"]*brand_associations.iloc[88]["comentions"])
LRLCA = (brand_associations.iloc[79]["comentions"]*sample)/(brand_associations.iloc[77]["comentions"]*brand_associations.iloc[99]["comentions"])

#Inverse Lift Ratios - Lexus

INLB = 1/LRLB
INLC = 1/LRLC
INLA = 1/LRLA
INLH = 1/LRLH
INLAU =1/LRLAU
INLI= 1/LRLI
INLN= 1/LRLN
INLT = 1/LRLT
INLCA = 1/LRLCA


#Lift Ratios - Toyota
LRTB = (brand_associations.iloc[80]["comentions"]*sample)/(brand_associations.iloc[88]["comentions"]*brand_associations.iloc[0]["comentions"])
LRTC = (brand_associations.iloc[81]["comentions"]*sample)/(brand_associations.iloc[88]["comentions"]*brand_associations.iloc[11]["comentions"])
LRTA = (brand_associations.iloc[82]["comentions"]*sample)/(brand_associations.iloc[88]["comentions"]*brand_associations.iloc[22]["comentions"])
LRTH = (brand_associations.iloc[83]["comentions"]*sample)/(brand_associations.iloc[88]["comentions"]*brand_associations.iloc[33]["comentions"])
LRTAU = (brand_associations.iloc[84]["comentions"]*sample)/(brand_associations.iloc[88]["comentions"]*brand_associations.iloc[44]["comentions"])
LRTI = (brand_associations.iloc[85]["comentions"]*sample)/(brand_associations.iloc[88]["comentions"]*brand_associations.iloc[55]["comentions"])
LRTN = (brand_associations.iloc[86]["comentions"]*sample)/(brand_associations.iloc[88]["comentions"]*brand_associations.iloc[66]["comentions"])
LRTL = (brand_associations.iloc[87]["comentions"]*sample)/(brand_associations.iloc[88]["comentions"]*brand_associations.iloc[77]["comentions"])
LRTCA = (brand_associations.iloc[89]["comentions"]*sample)/(brand_associations.iloc[88]["comentions"]*brand_associations.iloc[99]["comentions"])

#Inverse Lift Ratios - Toyota

INTB = 1/LRTB
INTC = 1/LRTC
INTA = 1/LRTA
INTH = 1/LRTH
INTAU =1/LRTAU
INTI= 1/LRTI
INTN= 1/LRTN
INTL = 1/LRTL
INTCA = 1/LRTCA


#Lift Ratios - Cadillac
LRCAB = (brand_associations.iloc[90]["comentions"]*sample)/(brand_associations.iloc[99]["comentions"]*brand_associations.iloc[0]["comentions"])
LRCAC = (brand_associations.iloc[91]["comentions"]*sample)/(brand_associations.iloc[99]["comentions"]*brand_associations.iloc[11]["comentions"])
LRCAA = (brand_associations.iloc[92]["comentions"]*sample)/(brand_associations.iloc[99]["comentions"]*brand_associations.iloc[22]["comentions"])
LRCAH = (brand_associations.iloc[93]["comentions"]*sample)/(brand_associations.iloc[99]["comentions"]*brand_associations.iloc[33]["comentions"])
LRCAAU = (brand_associations.iloc[94]["comentions"]*sample)/(brand_associations.iloc[99]["comentions"]*brand_associations.iloc[44]["comentions"])
LRCAI = (brand_associations.iloc[95]["comentions"]*sample)/(brand_associations.iloc[99]["comentions"]*brand_associations.iloc[55]["comentions"])
LRCAN = (brand_associations.iloc[96]["comentions"]*sample)/(brand_associations.iloc[99]["comentions"]*brand_associations.iloc[66]["comentions"])
LRCAL = (brand_associations.iloc[97]["comentions"]*sample)/(brand_associations.iloc[99]["comentions"]*brand_associations.iloc[77]["comentions"])
LRCAT = (brand_associations.iloc[98]["comentions"]*sample)/(brand_associations.iloc[99]["comentions"]*brand_associations.iloc[88]["comentions"])

#Inverse Lift Ratios - Cadillac

INCAB = 1/LRCAB
INCAC = 1/LRCAC
INCAA = 1/LRCAA
INCAH = 1/LRCAH
INCAAU =1/LRCAAU
INCAI= 1/LRCAI
INCAN= 1/LRCAN
INCAL = 1/LRCAL
INCAT = 1/LRCAT


#Lift Ratios Matrix

data = {"BMW": [0,LRBC, LRBA,LRBH,LRBAU,LRBI,LRBL,LRBN,LRBT,LRBCA],
        "Chrysler": [LRCB,0,LRCA,LRCH,LRCAU,LRCI,LRCN,LRCL,LRCT,LRCCA],
        "Acura": [LRAB,LRAC,0,LRAH,LRAAU,LRAI,LRAN,LRAL,LRAT,LRACA],
        "Honda": [LRHB,LRHC,LRHA,0,LRHAU,LRHI,LRHN,LRHL,LRHT,LRHCA],
        "Audi": [LRAUB,LRAUC,LRAUA,LRAUH,0,LRAUI,LRAUN,LRAUL,LRAUT,LRAUCA],
        "Infiniti": [LRIB,LRIC,LRIA,LRIH,LRIAU,0,LRIN,LRIL,LRIT,LRICA],
        "Nissan": [LRNB,LRNC,LRNA,LRNH,LRNAU,LRNI,0,LRNL,LRNT,LRNCA],
        "Lexus": [LRLB,LRLC,LRLA,LRLH,LRLAU,LRLI,LRLN,0,LRLT,LRLCA],
        "Toyota": [LRTB,LRTC,LRTA,LRTH,LRTAU,LRTI,LRTN,LRTL,0,LRTCA],
        "Cadillac": [LRCAB,LRCAC,LRCAA,LRCAH,LRCAAU,LRCI,LRCN,LRCL,LRCT,0]}


Lift_Ratios = pd.DataFrame(data,columns = ["BMW","Chrysler","Acura","Honda","Audi","Infiniti","Nissan","Lexus","Toyota","Cadillac"], index = ["BMW","Chrysler","Acura","Honda","Audi","Infiniti","Nissan","Lexus","Toyota","Cadillac"])

ax = sns.heatmap(Lift_Ratios,linewidth = 0.25, annot=True, cmap = "YlGnBu")
plt.show()

# Inverse Lift Ratios Matrix

data_inv = {"BMW": [0,INBC, INBA,INBH,INBAU,INBI,INBL,INBN,INBT,INBCA],
        "Chrysler": [INCB,0,INCA,INCH,INCAU,INCI,INCN,INCL,INCT,INCCA],
        "Acura": [INAB,INAC,0,INAH,INAAU,INAI,INAN,INAL,INAT,INACA],
        "Honda": [INHB,INHC,INHA,0,INHAU,INHI,INHN,INHL,INHT,INHCA],
        "Audi": [INAUB,INAUC,INAUA,INAUH,0,INAUI,INAUN,INAUL,INAUT,INAUCA],
        "Infiniti": [INIB,INIC,INIA,INIH,INIAU,0,ININ,INIL,INIT,INICA],
        "Nissan": [INNB,INNC,INNA,INNH,INNAU,INNI,0,INNL,INNT,INNCA],
        "Lexus": [INLB,INLC,INLA,INLH,INLAU,INLI,INLN,0,INLT,INLCA],
        "Toyota": [INTB,INTC,INTA,INTH,INTAU,INTI,INTN,INTL,0,INTCA],
        "Cadillac": [INCAB,INCAC,INCAA,INCAH,INCAAU,INCI,INCN,INCL,INCT,0]}


Inv_Lift_Ratios = pd.DataFrame(data_inv,columns = ["BMW","Chrysler","Acura","Honda","Audi","Infiniti","Nissan","Lexus","Toyota","Cadillac"], index = ["BMW","Chrysler","Acura","Honda","Audi","Infiniti","Nissan","Lexus","Toyota","Cadillac"])

ax = sns.heatmap(Inv_Lift_Ratios,linewidth = 0.25, annot=True, cmap = 'rocket_r')
plt.show()


#MDS PLot

mds = manifold.MDS(n_components=2, dissimilarity="euclidean", random_state=0)
results = mds.fit(Inv_Lift_Ratios.values)

car_brands = Inv_Lift_Ratios.columns
car_brands
coords = results.embedding_
coords

sizes = [16,16,16,16,16,16,16,16,16,16]
fig = plt.figure(figsize=(17,26))

plt.subplots_adjust(bottom = 0.5)
plt.scatter(coords[:, 0], coords[:, 1], marker='s')

for label, x, y, size in zip(car_brands, coords[:, 0], coords[:, 1], sizes):
    plt.annotate(
        label,
        xy = (x, y), 
        xytext = (-20, 20),
        textcoords = 'offset points', fontsize = size
    )
plt.show()


#K-Means Clustering

#Finding optimal K
from sklearn.cluster import KMeans
withinss = []
for i in range(2,8):
    kmeans = KMeans(n_clusters=i)
    model = kmeans.fit(Inv_Lift_Ratios)
    withinss.append(model.inertia_)
    print(i,withinss)
  
plt.plot([2,3,4,5,6,7],withinss)

#Applying K-means to generate three cluster map

from sklearn.decomposition import PCA

kmeans= KMeans(n_clusters = 3, precompute_distances = "auto",random_state=0)
Inv_Lift_Ratios['cluster'] = kmeans.fit_predict(Inv_Lift_Ratios)

reduced_data = PCA(n_components=2).fit_transform(Inv_Lift_Ratios)
results = pd.DataFrame(reduced_data,columns=['pca1','pca2'])
cluster_ = kmeans.labels_

sns.scatterplot(x="pca1", y="pca2", hue = cluster_,data=results, palette = 'colorblind')
plt.legend(title = "Clusters",loc='lower right')
plt.title('K-means Clustering with 2 dimensions')
plt.show()

#Inv_Lift_Ratios.to_csv(r"C:\Users\Nupur\OneDrive - McGill University\Desktop\McGill Notes\Text Analytics\clusters.csv")








