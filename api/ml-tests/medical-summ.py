from transformers import pipeline

summarizer = pipeline("summarization", model="Falconsai/medical_summarization")

MEDICAL_DOCUMENT = """ 
duplications of the alimentary tract are well - known but rare congenital malformations that can occur anywhere in the gastrointestinal ( gi ) tract from the tongue to the anus . while midgut duplications are the most common , foregut duplications such as oesophagus , stomach , and parts 1 and 2 of the duodenum account for approximately one - third of cases . 
 they are most commonly seen either in the thorax or abdomen or in both as congenital thoracoabdominal duplications . 
 cystic oesophageal duplication ( ced ) , the most common presentation , is often found in the lower third part ( 60 - 95% ) and on the right side [ 2 , 3 ] . hydatid cyst ( hc ) is still an important health problem throughout the world , particularly in latin america , africa , and mediterranean areas . 
 turkey , located in the mediterranean area , shares this problem , with an estimated incidence of 20/100 000 . 
 most commonly reported effected organ is liver , but in children the lungs are the second most frequent site of involvement [ 4 , 5 ] . in both ced and hc , the presentation depends on the site and the size of the cyst . 
 hydatid cysts are far more common than other cystic intrathoracic lesions , especially in endemic areas , so it is a challenge to differentiate ced from hc in these countries . here , 
 we present a 7-year - old girl with intrathoracic cystic mass lesion , who had been treated for hydatid cyst for 9 months , but who turned out to have oesophageal cystic duplication . 
 a 7-year - old girl was referred to our clinic with coincidentally established cystic intrathoracic lesion during the investigation of aetiology of anaemia . 
 the child was first admitted with loss of vision in another hospital ten months previously . 
 the patient 's complaints had been attributed to pseudotumour cerebri due to severe iron deficiency anaemia ( haemoglobin : 3 g / dl ) . 
 chest radiography and computed tomography ( ct ) images resulted in a diagnosis of cystic intrathoracic lesion ( fig . 
 the cystic mass was accepted as a type 1 hydatid cyst according to world health organization ( who ) classification . 
 after 9 months of medication , no regression was detected in ct images , so the patient was referred to our department . 
 an ondirect haemagglutination test result was again negative . during surgery , after left thoracotomy incision , a semi - mobile cystic lesion , which was almost seven centimetres in diameter , with smooth contour , was found above the diaphragm , below the lung , outside the pleura ( fig . 
 the entire fluid in the cyst was aspirated ; it was brown and bloody ( fig . 
 2 ) . the diagnosis of cystic oesophageal duplication was considered , and so an attachment point was searched for . 
 it was below the hiatus , on the lower third left side of the oesophagus , and it also was excised completely through the hiatus . 
 pathologic analysis of the specimen showed oesophageal mucosa with an underlying proper smooth muscle layer . 
 computed tomography image of the cystic intrathoracic lesion cystic lesion with brownish fluid in the cyst 
 compressible organs facilitate the growth of the cyst , and this has been proposed as a reason for the apparent prevalence of lung involvement in children . diagnosis is often incidental and can be made with serological tests and imaging [ 5 , 7 ] . 
 laboratory investigations include the casoni and weinberg skin tests , indirect haemagglutination test , elisa , and the presence of eosinophilia , but can be falsely negative because children may have a poor serological response to eg . 
 false - positive reactions are related to the antigenic commonality among cestodes and conversely seronegativity can not exclude hydatidosis . 
 false - negative results are observed when cysts are calcified , even if fertile [ 4 , 8 ] . in our patient iha levels were negative twice . 
 due to the relatively non - specific clinical signs , diagnosis can only be made confidently using appropriate imaging . 
 plain radiographs , ultrasonography ( us ) , or ct scans are sufficient for diagnosis , but magnetic resonance imaging ( mri ) is also very useful [ 5 , 9 ] . 
 computed tomography demonstrates cyst wall calcification , infection , peritoneal seeding , bone involvement fluid density of intact cysts , and the characteristic internal structure of both uncomplicated and ruptured cysts [ 5 , 9 ] . 
 the conventional treatment of hydatid cysts in all organs is surgical . in children , small hydatid cysts of the lungs 
 respond favourably to medical treatment with oral administration of certain antihelminthic drugs such as albendazole in certain selected patients . 
 the response to therapy differs according to age , cyst size , cyst structure ( presence of daughter cysts inside the mother cysts and thickness of the pericystic capsule allowing penetration of the drugs ) , and localization of the cyst . in children , small cysts with thin pericystic capsule localised in the brain and lungs respond favourably [ 6 , 11 ] . 
 respiratory symptoms are seen predominantly in cases before two years of age . in our patient , who has vision loss , the asymptomatic duplication cyst was found incidentally . 
 the lesion occupied the left hemithorax although the most common localisation reported in the literature is the lower and right oesophagus . 
 the presentation depends on the site and the size of the malformations , varying from dysphagia and respiratory distress to a lump and perforation or bleeding into the intestine , but cysts are mostly diagnosed incidentally . 
 if a cystic mass is suspected in the chest , the best technique for evaluation is ct . 
 magnetic resonance imaging can be used to detail the intimate nature of the cyst with the spinal canal . 
 duplications should have all three typical signs : first of all , they should be attached to at least one point of the alimentary tract ; second and third are that they should have a well - developed smooth muscle coat , and the epithelial lining of duplication should represent some portions of alimentary tract , respectively [ 2 , 10 , 12 ] . in summary , the cystic appearance of both can cause a misdiagnosis very easily due to the rarity of cystic oesophageal duplications as well as the higher incidence of hydatid cyst , especially in endemic areas . 
"""
print(summarizer(MEDICAL_DOCUMENT, max_length=2000, min_length=1500, do_sample=False))
