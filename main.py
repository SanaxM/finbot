from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import tkinter as tk
from tkinter import filedialog
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import PyPDF2


load_dotenv()


class FinancialBot:
    def __init__(self):
        self.state = "initial"
        self.income = None
        self.investment_amount = None
        self.stock = None

    def reset_inputs(self):
        self.income = None
        self.investment_amount = None
        self.stock = None

    def perform_investment_analysis(self):
        llm = OpenAI(temperature=0.5) #creativity

        prompt_template_investment = PromptTemplate(
            input_variables=['income', 'investment_amount', 'stock'],
            template="I am conducting an Investment Analysis. The customer's income is {income}, the investment amount is {investment_amount}, and the stock of interest is {stock}.")

        investment_chain = LLMChain(llm=llm, prompt=prompt_template_investment, output_key="investment_analysis_result")

        response = investment_chain({'income': self.income, 'investment_amount': self.investment_amount, 'stock': self.stock})

        return response['investment_analysis_result']
    
    def chat(self, message):
        llm = OpenAI(temperature=0.7)

        prompt_template = PromptTemplate(
            input_variables=['rep'],
            template=message
        )

        chain = LLMChain(llm=llm, prompt=prompt_template, output_key="bot_response")
        example = None
        response = chain({'rep': example})

        return response['bot_response']
    


def cus_info(message_area, flag):
    flag = True
    path = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("pdf files","*.pdf"),("all files","*.*")))
    pdf = open(path, 'rb')
    # extract the text
    if pdf is not None:
        pdf_reader = PyPDF2.PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    # split into chunks
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
    
        # create embeddings
        embeddings = OpenAIEmbeddings()
        knowledge_base = FAISS.from_texts(chunks, embeddings)
    message_area.insert('end', text)

    
def send(input, message_area, fin_bot):
    #display the user entered message
    message = input.get()
    message_area.insert('end', message.strip() + '\n', "human")
    message_area.insert('end', '\n')
    input.delete(0, 'end')
    
    result = fin_bot.chat(message)
    message_area.insert('end', result.strip() + '\n', "bot")
    message_area.insert('end', '\n')

input_button = None

def main():
    fin_bot = FinancialBot()
    cus_info_analysis = False

    #create the window
    window = tk.Tk()
    window.title("FinBot")
    window.geometry("600x600")
    window.config(bg='white')
    window.resizable(width=False, height=False)

    #logo + header
    logo = tk.PhotoImage(file='logo.png')
    logo_lbl = tk.Label(window, image=logo, border=0, justify="left")
    logo_lbl.pack(pady=5, side='top', anchor='w', padx=10)

    header_frame = tk.Frame(window, bg='#D9D9D9', width=1000, height=50)
    header = tk.Label(header_frame, bg='#D9D9D9', text="InvestiBuddy", 
                      width=len("Investibuddy                                                        "), 
                      height=2,
                      font=('Source Sans Pro', 13, 'bold'), justify="left", anchor='w')
    header_frame.pack(pady=5)
    header.pack(side='top', anchor='w', padx=10, fill="x")

    #chat area
    frame = tk.Frame(window, border=0)
    frame.pack(padx=5)

    message_area = tk.Text(frame, font=('Source sans pro', 13), wrap='word', borderwidth=0)
    message_area.pack(side='left')
    message_area.tag_configure("bot", background="#5236AB", foreground="white")
    message_area.tag_configure("human", background="#E31937", foreground="white", justify="right")

    entry_frame = tk.Frame(window, bg='white')
    entry_frame.pack(padx=5)

    input = tk.Entry(entry_frame, font=('Source sans pro', 13), width=58, justify="left")
    input.insert(0, "Type here...")
    input.pack(fill='x', pady=2, side='left', anchor='w')

    btn_img = tk.PhotoImage(file='arrow.png')
    input_button = tk.Button(entry_frame, text=">", image=btn_img, borderwidth=0, command=lambda: send(input, message_area, fin_bot))
    input_button.pack(padx=2, side='right')

    upload_img = tk.PhotoImage(file='Upload.PNG')
    upload_button = tk.Button(entry_frame, text=".", borderwidth=0, image=upload_img, command=lambda: cus_info(message_area, cus_info_analysis))
    upload_button.pack(padx=2, side='right')

    input.bind("<FocusIn>", lambda args: input.delete('0', 'end'))

    window.mainloop()

if __name__ == "__main__":
    main()
