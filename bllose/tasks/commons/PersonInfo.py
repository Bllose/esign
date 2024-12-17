from bllose.esign.Client import eqb_sign


client = eqb_sign()

result = client.person_info_v3(psnIDCardNum='431026198801130018')

print(result)

result = client.person_info_v1(thirdPartyUserId='431026198801130018')

print(result)