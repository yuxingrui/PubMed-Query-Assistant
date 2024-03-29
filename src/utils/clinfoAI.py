import sys
import os 
sys.path.append("..")
from  pathlib  import  Path
from  utils.pubmed_utils     import Neural_Retriever_PubMed
from  utils.bm25              import bm25_ranked
from fastapi import WebSocket

async def stream_output(type, output, websocket:WebSocket=None, logging=True):
    """
    Streams output to the websocket
    Args:
        type:
        output:

    Returns:
        None
    """
    if not websocket or logging:
        print(output)

    if websocket:
        await websocket.send_json({"type": type, "output": output})


class ClinfoAI:
    def __init__(self,openai_key, email,websocket=None,engine="PubMed",verbose=False) -> None:
        self.engine             = engine
        self.email              = email
        self.openai_key         = openai_key
        self.verbose            = verbose
        self.architecture_path  = self.init_engine()
        self.websocket=websocket


    def init_engine(self):
        if self.engine  == "PubMed":
            ARCHITECTURE_PATH = Path('../prompts/PubMed/Architecture_1/master.json')
            self.NEURAL_RETRIVER   = Neural_Retriever_PubMed(architecture_path=ARCHITECTURE_PATH ,verbose=False,debug=False,open_ai_key=self.openai_key,email=self.email)
            print("PubMed Retriever Initialized")
        else:
            raise Exception("Invalid Engine")

        ARCHITECTURE_PATH_STR = str(ARCHITECTURE_PATH)
        return   ARCHITECTURE_PATH_STR 
    

    def retrive_articles(self,question,restriction_date = None, ignore=None):
        try:

            queries, article_ids = self.NEURAL_RETRIVER.search_pubmed(question             = question,
                                                                        num_results        = 10,
                                                                        num_query_attempts = 10,
                                                                        restriction_date   = restriction_date) 
                

           
        except: 
            print(f"Internal Service Error, {self.engine } might be down ")
         
       
        

        if ignore != None:
            try:
                print("Article dropped")
                article_ids.remove(ignore)
            except:
                pass




        if (not article_ids) or (not queries) or (len(article_ids) == 0) or (len(queries) == 0):
            print(f"Sorry, we weren't able to find any articles in {self.engine} relevant to your question. Please try again.")
            return
    
        try:
            if self.engine == "PubMed":
                articles = self.NEURAL_RETRIVER.fetch_article_data(article_ids)
            
            if  self.verbose:
                print(f'Retrieved {len(articles)} articles. Identifying the relevant ones and summarizing them (this may take a minute)')
            

        except:
            print('error',f"Articles could not be fetched from {self.engine}")
        

        
        if len(articles) ==0:
            print(f"Articles could not be fetched from {self.engine}, 0")
           
        return articles,queries
    

    def summarize_relevant(self,articles,question):
        article_summaries,irrelevant_articles = self.NEURAL_RETRIVER.summarize_each_article(articles, question)
        print("article_summary:",article_summaries)
        print("irevelant:",irrelevant_articles)
        return   article_summaries,irrelevant_articles 
    
    def final_decision(self,question,synthesis):
        answer=self.NEURAL_RETRIVER.final_decision(question,synthesis)
        return answer

    def synthesis_task(self,article_summaries, question,USE_BM25=True,with_url=True ):
        if USE_BM25:
            if len(article_summaries) > 11:
                print("Using BM25 to rank articles")
                corpus            = [article['abstract'] for article in article_summaries]
                article_summaries = bm25_ranked(list_to_oganize= article_summaries,corpus =  corpus,query = question,n = 10)

        astr,synthesis = self.NEURAL_RETRIVER.agent_output(article_summaries, question, prompt_dict={"type":"automatic"} ,with_url=with_url)
        return astr,synthesis
    


    async def forward(self,question,restriction_date = None, ignore=None,return_articles=False): 
        print(f"🔎 Running research for '{question}'...")
        try:
            articles,queries                              = self.retrive_articles(question,restriction_date , ignore)
            await stream_output("logs", f"Pubmed query is {queries},and Articles searched are listed as below:\n\n{articles}\n\n", self.websocket)
            
            article_summaries,irrelevant_articles  = self.summarize_relevant(articles=articles,question=question)
            
            # print("article_summaries:",article_summaries)
            astr,synthesis                              = self.synthesis_task(article_summaries, question)
            await stream_output("logs",f"Here is the summary of all articles:{astr}")
            await stream_output("logs",f"Here is the sythesis:{synthesis}")

        except:
            astr=""
            synthesis = "Internal Error"
        
        if return_articles:
            return astr,synthesis,irrelevant_articles,queries
        
        return astr,synthesis 

        
