import google.generativeai as genai

API_KEY = "AIzaSyC0Bse9MriADspLnHVVwnfKfSUwnojvDJI"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

# prompt='''
# 1.You are a Named Entity Recognition in English Language.
# 2.Do some analysis to extract the Entity from the text for some categories, i.e., Person, Organization, Location, Date/Time, their activities, relations and other as Miscellaneous.
# 3.Output Person category as PER, Organization category as ORG, Location category as LOC, Date/Time category as DT, and Miscellaneous category as MISC.
# 4.Return this result as JSON for each entity with character offset from each result.
# Analyze the sentences as follow: "'
# '''

prompt='''
1.You are a Named Keyword Extractor in English Language.
2.Do some analysis to extract the Keyword from the text for some categories, i.e., Person, Organization, Location, Date/Time, their activities, relations and other as Miscellaneous. 
3.Output Person category as PER, Organization category as ORG, Location category as LOC, Date/Time category as DT, Action and Activity as ACT and Miscellaneous category as MISC. 
4.Return this result as JSON for each entity with character offset from each result.
Analyze the sentences as follow: "'
'''

query ='''
The finance adviser said that the local industries were needed to be got rid of tax exemption facility to face the challenges the country’s graduation from the least developed countries’ bloc in 2026 would bring.
Many local export-oriented industries which are now enjoying duty preferences in developed and developing countries may lose the benefit, he said.
The finance adviser was also critical about the tax evasion for which the country’s tax-GDP ratio has been ridiculed as one of the lowest in the world.
He suggested that tax officials should be friendly to taxpayers.
He called upon all to pay taxes so that the government is able to increase allocation to health and education sectors.
A World Bank report said the county’s income from value-added tax in 2018-19 could have been at least three times higher than the collection of Tk 85,000 crore had the government implemented the VAT law properly.
Presided over by NBR chairman Md Abdur Rahman Khan, Finance Division secretary Md Khairuzzaman Mozumder and Federation of Bangladesh Chambers of Commerce and Industry administrator Md Hafizur Rahman spoke at the seminar.
The finance secretary said the development partners often raised the issue of low tax-GDP ratio.
The revenue board should conduct strong efforts to augment revenue mobilisation, he said.
'''
response = model.generate_content(prompt+query +'"')
print(response.parts[0].text)
print(response.parts[0])