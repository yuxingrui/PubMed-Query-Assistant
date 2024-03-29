import json
from werkzeug.security import generate_password_hash
import random
import asyncio

def save_json(dict_:dict,file_name:str):
    with open(file_name, 'w') as fp:
        json.dump(dict_, fp)
        
        
def read_json(file_name:str):
    with open(file_name, 'r') as fp:
        data = json.load(fp)
    return data


def retirive_user(user_emails,token="_1265!"):
    users = {}
    for email in user_emails:
        password = email.split('@')[0] + token
        users[email] = {"password": generate_password_hash(password) }

    return users

# def extract_json(file_name:str="../../../ori_pqal.json",num=100):
#     test_set={}
#     bench_set={}
#     with open(file_name,'r') as f:
#         original_data=json.load(f)
#         #print(data)
#     keys = list(original_data.keys())

# # 从键中随机选择 100 个
#     random_keys = random.sample(keys, num)

# # 使用随机选择的键获取对应的值
#     data = {key:original_data[key] for key in random_keys}
#     for key,values in data.items():
#         bench_set[key]=values["LONG_ANSWER"]  
#         test_set[key]=values["QUESTION"]
             
#     return bench_set,test_set

# def split_sections(text):
#     # 检查文本中是否包含 "Literature Summary"，"TL;DR" 和 "References"
#     literature_summary_index = text.find("Literature Summary:")
#     tldr_index = text.find("TL;DR:")
#     references_index = text.find("References:")
    
#     # 提取各部分内容
#     literature_summary = text[literature_summary_index+20:tldr_index].strip() if literature_summary_index != -1 else None
#     tldr = text[tldr_index+7:references_index].strip() if tldr_index != -1 else None
    
#     return literature_summary, tldr

# async def storage(clinfo,num=10,bench_file:str="./bench.json",predict_file:str="./predict.json"):
#     bench,test=extract_json(num=num)
#     with open(bench_file,'w') as f:
#         json.dump(bench,f,indent=4)
#     new_data={}
#     for key,query in test.items():
#         print("query:",query)
#         astr,synthesis=await clinfo.forward(question=query)
#         lit,tldr=split_sections(synthesis)
#         #answer=clinfo.final_decision(query,synthesis)
#         new_data[key]={query:[lit,tldr,astr]}
#         await asyncio.sleep(10)
#     with open(predict_file,'w') as f:
#         json.dump(new_data,f,indent=4)
#     print("file has already storaged")

    
# async def generate_data(clinfo,predict_file:str="./new_predict.json"):
    
#     with open("D:/Clinfo.AI/src/notebooks/predict.json",'r',encoding='utf-8') as f:
#         data=json.load(f)
#     new_data={}
#     for key,values in data.items():
#         for query,_ in values.items():
#             print("query:",query)
#             astr,synthesis=await clinfo.forward(question=query)
#             lit,tldr=split_sections(synthesis)
#             #answer=clinfo.final_decision(query,synthesis)
#             new_data[key]={query:[lit,tldr,astr]}
#             await asyncio.sleep(10)
#     with open(predict_file,'w') as f:
#         json.dump(new_data,f,indent=4)
#     print("file has already storaged")

