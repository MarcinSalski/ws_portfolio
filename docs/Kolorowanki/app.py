
import streamlit as st
import os
import pandas as pd
import requests
import boto3
import io
from dotenv import load_dotenv
from IPython.display import Image
from openai import OpenAI
from openai import AuthenticationError
from botocore.exceptions import ClientError




#Checking if Open AI API Key is valid
def openai_api_key_check(api_key: str) -> bool:
    try:
        client = OpenAI(api_key=api_key)
        client.models.list()  
        return True  # Key is valid

    except AuthenticationError:
        return False  # Key is invalid

    except Exception:
        return False  # Any other unexpected error



#Getting Open AI access
def get_openai_client():
    return OpenAI(api_key=st.session_state["openai_api_key"])
    


# Checking if client's design list exists and creaiting a new list if necessary
def list_file_exists(bucket, key):
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise  # Inny błąd — rzuć dalej


# Saving design lists as public files
def save_df_as_public_csv(df, bucket, key):
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=buffer.getvalue(),
        ACL="public-read",
        ContentType="text/csv"
    )
    


# The function to generate design descriptions for kids
def get_description_for_kids(user_prompt):
    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """"
                    Jesteś projektantem kolorowanek dla dzieci. Na podstawie promptu wpisanego 
                    przez użytkownika zaproponuj tytuł kolorowanki oraz opis rysunku, który 
                    w następnym kroku zostanie utworzony. Rysunek ma być prosty i łatwy 
                    do pokolorowania. Postacie i przedmioty na rysunku powinny mieć wygląd 
                    dziecinny i bajkowy. Jeśli na rysunku występują sceny lub postacie z bajek, 
                    to nawiąż w swoim opisie do treści odpowiedniej bajki.
                    - Jeśli opis wprowadzony przez użytkownika jest dokładny i szczegółowy 
                    zaproponuj niewielkie modyfikacje w celu utworzenia wariantów. 
                    - Jeśli opis wprowadzony przez użytkownika jest uproszczony - rozwiń go 
                    dodając szczegóły, otoczenie, tło i tym podobne elementy. 
                    - W swoim opisie nie umieszczaj kolorów. To ma być opis czarno-białego szkicu.
                    - Opis rysunku powinien mieć formę promptu, na podstawie którego sztuczna inteligencja 
                    wygeneruje obraz w następnym kroku działania aplikacji
                    - Opis każdego rysunku nie powinien być dłuższy niż 50 słów.
                    - Zrób tyle opisów o ile projektów prosi klient.
                    - Każdy opis przedstaw w formacie jak poniżej. 
                        Projekt 1: 
                        Tytuł: 
                        Opis:  
                        
                        Projekt 2:  
                        Tytuł: 
                        Opis:
                        
                        itd.

                    - Nie używaj cudzysłowia przy podawaniu tytułu.
                    - Nie proponuj treści szokujących, strasznych, wulgarnych ani obscenicznych.
                """
             },
            {"role": "user", "content": user_prompt }           
        ]
    )

    return {
        "role": "assistant",
        "content": response.choices[0].message.content,
    }



# The function to generate design descriptions for adults
def get_description_for_adults(user_prompt):
    openai_client = get_openai_client()
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """"
                    Jesteś projektantem kolorowanek dla dorosłych. Na podstawie promptu wpisanego 
                    przez użytkownika zaproponuj tytuł kolorowanki oraz opis rysunku, który 
                    w następnym kroku zostanie utworzony. Rysunek powinien być dokładny, 
                    szczegółowy i jak najbardziej realistyczny. Postacie, zwierzęta, rośliny 
                    i przedmioty przedstawione na obrazku powinny mieć wygląd jak najbardziej zbliżony 
                    do rzeczywistego. Np: jeśli na rysunku przedstawione jest zwierze to niech 
                    ono wygląda tak jak w rzeczywistości, jeśli na rysunku przedstawiony jest 
                    samochód to niech to będzie konkretny typ i model - jak rzeczywisty. Jeśli na 
                    rysunku pojawiają sie ludzie, to niech to będą portrety osób (jak aktorzy) itp.
                    - Jeśli opis wprowadzony przez użytkownika jest dokładny i szczegółowy 
                    zaproponuj niewielkie modyfikacje w celu utworzenia wariantów. 
                    - Jeśli opis wprowadzony przez użytkownika jest uproszczony - rozwiń go 
                    dodając szczegóły, otoczenie, tło i tym podobne elementy. 
                    - W swoim opisie nie umieszczaj kolorów. To ma być opis czarno-białego szkicu.
                    - Opis rysunku powinien mieć formę promptu, na podstawie którego sztuczna inteligencja 
                    wygeneruje obraz w następnym kroku działania aplikacji
                    - Opis każdego rysunku nie powinien być dłuższy niż 50 słów.
                    - Zrób tyle opisów o ile projektów prosi klient.
                    - Każdy opis przedstaw w formacie jak poniżej. 
                        Projekt 1: 
                        Tytuł: 
                        Opis:  
                        
                        Projekt 2:  
                        Tytuł: 
                        Opis:
                        
                        itd.

                    - Nie używaj cudzysłowia przy podawaniu tytułu.
                """
             },
            {"role": "user", "content": user_prompt }           
        ]
    )

    return {
        "role": "assistant",
        "content": response.choices[0].message.content,
    }



# The function to generate design descriptions for kids
def get_description_for_fun(user_prompt):
    openai_client = get_openai_client()
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """"
                    Jesteś projektantem kolorowanek dowcipnych, satyrycznych. Na podstawie 
                    promptu wpisanego przez użytkownika zaproponuj tytuł kolorowanki oraz opis 
                    rysunku, który w następnym kroku zostanie utworzony. Przedmioty, sceny i 
                    postacie przedstawiaj w sposób satyryczny, karykaturalny np: karykaturalnie 
                    zmienione twarze i wygląd postaci, śmieszny ubiór, uszkodzone przedmioty, 
                    dziwne sceny na drugim planie (ktoś się przewraca, ktoś coś psuje) itp. Niech ten rysunek
                    będzie miał charakter komiksu z różnymi dziwnymi dodatkami.
                    - Jeśli opis wprowadzony przez użytkownika jest dokładny i szczegółowy 
                    zaproponuj niewielkie modyfikacje w celu utworzenia wariantów. 
                    - Jeśli opis wprowadzony przez użytkownika jest uproszczony - rozwiń go 
                    dodając szczegóły, otoczenie, tło i tym podobne elementy. 
                    - W swoim opisie nie umieszczaj kolorów. To ma być opis czarno-białego szkicu.
                    - Opis rysunku powinien mieć formę promptu, na podstawie którego sztuczna inteligencja 
                    wygeneruje obraz w następnym kroku działania aplikacji
                    - Opis każdego rysunku nie powinien być dłuższy niż 50 słów.
                    - Zrób tyle opisów o ile projektów prosi klient.
                    - Każdy opis przedstaw w formacie jak poniżej. 
                        Projekt 1: 
                        Tytuł: 
                        Opis:  
                        
                        Projekt 2:  
                        Tytuł: 
                        Opis:
                        
                        itd.

                    - Nie używaj cudzysłowia przy podawaniu tytułu.
                """
             },
            {"role": "user", "content": user_prompt }           
        ]
    )

    return {
        "role": "assistant",
        "content": response.choices[0].message.content,
    }

# Adding generated descriptions to the list
def add_description(title_text,description_type, description_text):
    description_df=st.session_state["descriptions_df"]
    if description_df['Nr projektu'].max()>0:
        new_data = {
        "Nr projektu": description_df["Nr projektu"].max() + 1, 
        "Tytuł": title_text, 
        "Rodzaj": description_type,
        "Opis": description_text  
        }
    else:
        new_data = {
        "Nr projektu": 1,
        "Tytuł": title_text, 
        "Rodzaj": description_type,
        "Opis": description_text  
        }
    new_row = pd.DataFrame([new_data])
    description_df = pd.concat([ description_df, new_row ], ignore_index=True)
    st.session_state["descriptions_df"]=description_df
    st.session_state['curr_proj_n']=description_df['Nr projektu'].max()
    


# Creating autput file name without spaces and new line signs
def clear_output_path(text: str) -> str:
    text=text.replace("\n","")
    text=text.replace(" ", "")
    return text




# Preparing prompt for image generation
def prepare_image_prompt(project_id):
    descriptions_df=st.session_state["descriptions_df"]
    selected_project_df = descriptions_df[descriptions_df['Nr projektu'] == project_id]
    image_title = selected_project_df.iat[0,1]
    image_type = selected_project_df.iat[0,2]
    image_description = selected_project_df.iat[0,3]
    curr_img_n=f"{image_title}.png"
    curr_img_n=clear_output_path(curr_img_n)
    st.session_state['curr_img_n']=curr_img_n
    st.session_state['curr_img_dir']=f'{img_fold_n}/{curr_img_n}'
    st.session_state['curr_img_full']=f'{PATH_TO_DO}{img_fold_n}/{curr_img_n}'
    get_unique_filename(s3, BUCKET_NAME, img_fold_n, curr_img_n)
    curr_img_n=st.session_state['curr_img_n']
    output_path=st.session_state['curr_img_dir']
    if image_type=="dla dzieci":
        system_text="""Jesteś wytwórcą kolorowanek dla dzieci. Tworzysz czarno białe rysunki 
        konturowe, które będzie można pokolorować kredkami lub  mazakami. Przy rysowaniu nie 
        wypełniaj żadnym kolorem (także czarnym) żadnych obiektów ani postaci przedstawionych
        na rysunku. Narysuj tylko kontury. 
        Na podstawie opisu wpisanego przez użytkownika wykonaj czarno-biały szkic, który po 
        wydrukowaniu będzie nadawał się do pokolorowania. Rysunek ma być prosty i łatwy do 
        pokolorowania. Postacie i przedmioty na rysunku powinny mieć wygląd dziecinny i bajkowy. 
        Jeśli na rysunku występują sceny lub postacie z bajek, to nawiąż do treści odpowiedniej 
        bajki.
        - Jeśli opis wprowadzony przez użytkownika jest dokładny i szczegółowy zastosuj się dokładnie 
            do instrukcji.
        - Jeśli opis wprowadzony przez użytkownika jest uproszczony - rozwiń go dodając szczegóły, 
            otoczenie, tło i tym podobne elementy. 
        - Wykonaj rysunek cienkimi kreskami, tak aby w czasie kolorowania można było pogrubić 
            niektóre z nich lub zmienić ich kolor.
        - Nie wypełniaj obiektów na rysunku kolorem szarym ani czarnym. 
        - Nie używaj kolorów innych niż czerń i biel
        - Rysuj tylko kontury i zostaw do pokolorowania.
        - Nie rysuj treści szokujących, strasznych, wulgarnych ani obscenicznych. Jeśli takie 
        treści pojawią się w prompcie zignoruj je i wykonaj rysunek bez tych treści.
        """

    elif image_type=="dla dorosłych":
        system_text="""Jesteś wytwórcą kolorowanek dla dorosłych. Tworzysz czarno białe rysunki 
        konturowe, które będzie można pokolorować kredkami lub  mazakami. Przy rysowaniu nie 
        wypełniaj żadnym kolorem (także czarnym) żadnych obiektów ani postaci przedstawionych
        na rysunku. Narysuj tylko kontury.  
        Na podstawie opisu wpisanego przez użytkownika wykonaj czarno-biały szkic, który 
        po wydrukowaniu będzie nadawał się do pokolorowania. Rysunek powinien być dokładny, 
        szczegółowy i jak najbardziej realistyczny. Postacie, zwierzęta, rośliny i przedmioty 
        przedstawione na obrazku powinny mieć wygląd jak najbardziej zbliżony do rzeczywistego 
        np: jeśli na rysunku przedstawione jest zwierzę to niech ono wygląda tak jak w 
        rzeczywistości, jeśli na rysunku przedstawiony jest samochód to niech to będzie konkretny 
        typ i model - jak rzeczywisty. Jeśli na rysunku pojawiają sie ludzie, to niech to będą 
        portrety osób (jak aktorzy) itp.
        - Jeśli opis wprowadzony przez użytkownika jest dokładny i szczegółowy zastosuj się dokładnie 
            do instrukcji.
        - Jeśli opis wprowadzony przez użytkownika jest uproszczony - rozwiń go dodając szczegóły, 
            otoczenie, tło i tym podobne elementy. 
        - Wykonaj rysunek cienkimi kreskami, tak aby w czasie kolorowania można było pogrubić 
            niektóre z nich lub zmienić ich kolor.
        - Nie wypełniaj obiektów na rysunku kolorem szarym ani czarnym. 
        - Nie używaj kolorów innych niż czerń i biel
        - Rysuj tylko kontury i zostaw do pokolorowania.
        - Nie rysuj treści szokujących, wulgarnych ani obscenicznych. Jeśli takie 
        treści pojawią się w prompcie zignoruj je i wykonaj rysunek bez tych treści.
        """

    else:
        system_text="""Jesteś wytwórcą kolorowanek dla dzieci. Tworzysz czarno białe rysunki 
        konturowe, które będzie można pokolorować kredkami lub  mazakami. Przy rysowaniu nie 
        wypełniaj żadnym kolorem (także czarnym) żadnych obiektów ani postaci przedstawionych
        na rysunku. Narysuj tylko kontury.  Na podstawie opisu wpisanego przez użytkownika 
        wykonaj czarno-biały szkic, który po wydrukowaniu będzie nadawał się do pokolorowania. 
        Przedmioty, sceny i postacie przedstawiaj w sposób satyryczny, karykaturalny np: 
        karykaturalnie zmienione twarze i wygląd postaci, śmieszny ubiór, uszkodzone przedmioty, 
        dziwne sceny na drugim planie (ktoś się przewraca, ktoś coś psuje) itp. Niech ten rysunek 
        będzie miał charakter komiksu z różnymi dziwnymi dodatkami.
        - Jeśli opis wprowadzony przez użytkownika jest dokładny i szczegółowy zastosuj się dokładnie 
            do instrukcji.
        - Jeśli opis wprowadzony przez użytkownika jest uproszczony - rozwiń go dodając szczegóły, 
            otoczenie, tło i tym podobne elementy. 
        - Wykonaj rysunek cienkimi kreskami, tak aby w czasie kolorowania można było pogrubić 
            niektóre z nich lub zmienić ich kolor.
        - Nie wypełniaj obiektów na rysunku kolorem szarym ani czarnym. 
        - Nie używaj kolorów innych niż czerń i biel
        - Rysuj tylko kontury i zostaw do pokolorowania.
        - Nie rysuj treści szokujących, wulgarnych ani obscenicznych. Jeśli takie treści 
            pojawią się w prompcie zignoruj je i wykonaj rysunek bez tych treści.
        """

    prompt_text=f"{system_text} Tytuł kolorowanki: {image_title} Opis podany przez użytkownika: {image_description}"
    st.session_state['prompt_text']=prompt_text
    st.session_state['output_path']=output_path
    
   



# Creating the colouring page according to the selected description
def generate_image(text, output_path):
    
    fallback_url = f"{img_fold_n}/{refuse_image_name}"
    
    try:
        openai_client = get_openai_client()
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=text,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        image_bytes = requests.get(image_url).content
        buffer = io.BytesIO(image_bytes)
        s3.upload_fileobj(buffer, BUCKET_NAME, output_path, ExtraArgs={"ACL": "public-read"})
        return Image(output_path)

    except Exception as e:
        st.session_state["output_path"]=fallback_url
        st.session_state["curr_img_n"]=refuse_image_name
        st.session_state['curr_img_dir']=f"{img_fold_n}/{refuse_image_name}"
        st.session_state['curr_img_full']=f"{PATH_TO_DO}{img_fold_n}/{refuse_image_name}"
        output_path=st.session_state["curr_img_dir"]
        image_url = st.session_state["curr_img_full"]
        image_bytes = requests.get(image_url).content
        buffer = io.BytesIO(image_bytes)
        s3.upload_fileobj(buffer, BUCKET_NAME, output_path, ExtraArgs={"ACL": "public-read"})
        
        return Image(st.session_state["curr_img_dir"])
    


def quick_image_generate(project_id):
    prepare_image_prompt(project_id)
    prompt_text=st.session_state['prompt_text']
    output_path=st.session_state['output_path']
    generate_image(prompt_text, output_path)


def get_unique_filename(s3, BUCKET_NAME, img_fold_n, curr_img_n):
    name, ext = os.path.splitext(curr_img_n)
    counter = st.session_state['counter']
    candidate = f"{img_fold_n}/{curr_img_n}" #if folder_name else base_filename
    
    # Sprawdzaj istnienie pliku
    while True:
        try:
            s3.head_object(Bucket=BUCKET_NAME, Key=candidate)
            # Jeśli nie wyrzuci błędu, to plik istnieje → generuj nową nazwę
            candidate=f"{img_fold_n}/{name}{counter}{ext}"
            curr_img_n = f"{name}{counter}{ext}" #if folder_name else f"{name}-{counter}{ext}"
            st.session_state['curr_img_n']=curr_img_n
            st.session_state['curr_img_dir']=candidate
            st.session_state['curr_img_full']=f'{PATH_TO_DO}{candidate}'
            st.session_state['counter'] = counter+1
            
        except s3.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                # Plik nie istnieje — ta nazwa jest wolna
                break
            else:
                raise e  # Coś innego poszło nie tak
        
    return curr_img_n



def list_images():
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=img_fold_n + "/")
    sorted_files = sorted(
        response['Contents'],
        key=lambda x: x['LastModified'],
        reverse=True
    )

    # Zwracaj tylko klucze (ścieżki do obrazków)
    return [item['Key'] for item in sorted_files if item['Key'].lower().endswith((".png", ".jpg", ".jpeg"))]



def display_images_with_download():
    image_keys = list_images()

    if not image_keys:
        st.info("Brak obrazków w katalogu.")
        return

    for key in image_keys:
        url = f"{SPACES_URL}/{key}"

        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(url, caption=key.split("/")[-1], width=200)
        with col2:
            st.markdown(f"[Pobierz]({url})", unsafe_allow_html=True)





# Main



# OpenAI API key protection and geting user name


load_dotenv()

s3 = boto3.client(
    's3',
    region_name='fra1',
    endpoint_url='https://fra1.digitaloceanspaces.com',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)    


BUCKET_NAME="kolorowanki"
img_fold_n='images'
list_folder_name='lists'
ENDPOINT = "https://fra1.digitaloceanspaces.com"  
PATH_TO_DO=f"https://{BUCKET_NAME}.fra1.digitaloceanspaces.com/"
SPACES_URL = f"https://{BUCKET_NAME}.fra1.digitaloceanspaces.com"
opening_image_name="KolorowySwiat.png"
place_image_name="Tutaj.png"
refuse_image_name="Nie_moge.png"

c0, c1, = st.columns([0.7,0.3])
with c0:
    st.title('Moje kolorowanki')
    st.markdown("""Przy pomocy tej aplikacji, w ciągu kilku minut stworzysz dla swojego dziecka 
                czy wnuka kolorowankę, jakiej nikt inny nie ma. Wystarczy ją wydrukować 
                i pokolorować. Miłej zabawy!""")
        
with c1:
    opening_image=f"{PATH_TO_DO}{img_fold_n}/{opening_image_name}"
    st.image(opening_image,use_container_width=True)

if not st.session_state.get("user_name"):
    st.info("Wprowadź swoje imię")
    st.session_state["user_name"] = st.text_input(" ", type="default")
    if st.session_state["user_name"]:
        user_name=st.session_state["user_name"]
        list_name=f"{list_folder_name}/{user_name}_design_list.csv"
        if list_file_exists(BUCKET_NAME, list_name):
            list_file=f"{PATH_TO_DO}{list_name}"
            st.session_state["full_list_df"]=pd.read_csv(f"{PATH_TO_DO}{list_name}")
            descriptions_df=st.session_state["full_list_df"]
            st.session_state["descriptions_df"]=descriptions_df
            st.session_state['descr_counter']=descriptions_df['Nr projektu'].max()
            st.session_state["list_file"]=list_file
            st.session_state["list_name"]=list_name
            st.rerun()
        else:
            descriptions_df=pd.DataFrame([{"Nr projektu":0, "Tytuł":"","Rodzaj":"", "Opis":""}])
            save_df_as_public_csv(descriptions_df, BUCKET_NAME, list_name)
            st.session_state["list_name"]=list_name
            st.session_state["full_list_df"]=descriptions_df
            st.session_state["descriptions_df"]=descriptions_df
            st.session_state['descr_counter']=descriptions_df['Nr projektu'].max()
            st.session_state["list_name"]=list_name
            st.rerun()

if not st.session_state.get("user_name"):
    st.stop()



if not st.session_state.get("openai_api_key"):
    if "OPENAI_API_KEY" in os.environ:
        st.session_state["openai_api_key"] = os.environ["OPENAI_API_KEY"]

    else:
        st.info("Podaj klucz Open AI API Key")
        st.session_state["openai_api_key"] = st.text_input(" ", type="password")
        openai_api_key=st.session_state["openai_api_key"]
        if st.session_state["openai_api_key"]:
            if openai_api_key_check(openai_api_key) == True:
                st.rerun()
            else:
                st.markdown("Niepoprawny klucz Open AI")
                st.session_state["openai_api_key"]=""
                st.stop()

if not st.session_state.get("openai_api_key"):
    st.stop()


# Main section after login

# Session state initial config



if "page_descriptions" not in st.session_state:
    st.session_state["page_descriptions"] = []

if "descriptions_df" not in st.session_state:
    list_file=st.session_state["list_file"]
    descriptions_df=pd.read_csv(list_file)
    st.session_state["descriptions_df"]=descriptions_df
    st.session_state['descr_counter']=descriptions_df['Nr projektu'].max()

if 'curr_proj_n' not in st.session_state:
    st.session_state['curr_proj_n']=0
    
if 'curr_img_n' not in st.session_state:
    st.session_state['curr_img_n']=place_image_name
    st.session_state['curr_img_dir']=f"{img_fold_n}/{place_image_name}"
    st.session_state['curr_img_full']=f"{PATH_TO_DO}{img_fold_n}/{place_image_name}"
   
if 'counter' not in st.session_state:
    st.session_state['counter']=1

if 'title' not in st.session_state:
    st.session_state['title']='title'

if 'description' not in st.session_state:
    st.session_state['description']='description'

if 'prompt_text' not in st.session_state:
    st.session_state['prompt_text']=''

if 'output_path' not in st.session_state:
    st.session_state['output_path']=''

if 'buffer' not in st.session_state:
    st.session_state['buffer']=io.BytesIO()




# First screen

user_name=st.session_state["user_name"]
st.markdown(f"Jesteś zalogowany jako {user_name}")  

design_tab, list_tab, image_tab, gallery_tab, logout_tab = st.tabs(
    ["Zaprojektuj kolorowankę", 
     'Lista opisów',
     'Popraw opis',
     'Galeria kolorowanek',
     'Wyloguj się'])



# Generating image descriptions
with design_tab:
    c0, c1 = st.columns([0.3,0.7])
    
    with c0:
        number_of_descriptions = st.selectbox("Ile zrobić projektów?", ["1","2","3","4","5"]) 
        design_type=st.selectbox('Rodzaj kolorowanki',['dla dzieci','dla dorosłych','satyryczny'])  
    
    with c1:
        for page_description in st.session_state["page_descriptions"]:
            with st.chat_message(page_description["role"]):
                st.markdown(page_description["content"])
        prompt = st.text_area("Napisz co ma być na obrazku",height=124)
    if st.button("Przygotuj opisy",use_container_width=True):
        user_message = {"role": "user", "content": f"{prompt}. Liczba projektów: {number_of_descriptions}"}
        with st.chat_message("user"):
            st.markdown(user_message["content"])
                
        with st.chat_message("assistant"):
            with st.spinner ("Przygotowuję opisy rysunków..."):
                st.session_state['curr_img_n']=place_image_name
                st.session_state['curr_img_dir']=f"{img_fold_n}/{place_image_name}"
                st.session_state['curr_img_full']=f"{PATH_TO_DO}{img_fold_n}/{place_image_name}"
                if design_type=='dla dzieci':
                    chatbot_message = get_description_for_kids(f"Poproszę o {number_of_descriptions} projektów. Opis projektu:{prompt}")
                elif design_type=='dla dorosłych':
                    chatbot_message = get_description_for_adults(f"Poproszę o {number_of_descriptions} projektów. Opis projektu:{prompt}")
                else:
                    chatbot_message = get_description_for_fun(f"Poproszę o {number_of_descriptions} projektów. Opis projektu:{prompt}")
    
        text=chatbot_message["content"]
        projects = text.split("Projekt")
        del projects[0]
        for project in projects:
            parts=project.split(": ")
            title=parts[2].replace("Opis","")
            description=parts[3]
            add_description(title, design_type, description)
            
        descriptions_df=st.session_state["descriptions_df"]
        max_id=descriptions_df["Nr projektu"].max()
        min_id=descriptions_df["Nr projektu"].max()-int(number_of_descriptions)
        current_projects_df=descriptions_df[(descriptions_df['Nr projektu'] > min_id) & (descriptions_df['Nr projektu'] <= max_id)]
        for i, row in current_projects_df.iterrows():
            projekt_id = row['Nr projektu']
            title = row['Tytuł']
            type = row['Rodzaj']
            description = row['Opis']

            with st.container():
                col1, col2 = st.columns([8, 2])
                with col1:
                    st.markdown(f"#### {title}")
                    st.markdown(f'{type}')
                    st.markdown(f"{description}")
                with col2:
                    st.button(label=f"Stwórz kolorowankę: {title}",
                              key=projekt_id,
                              on_click=quick_image_generate,
                              args=(projekt_id,))
                        
                               
    
    with st.spinner("Zaraz pojawi się Twoja kolorowanka ..."):            
        curr_img_n=st.session_state["curr_img_n"]
        curr_img_dir=st.session_state['curr_img_dir']
        curr_img_full=st.session_state['curr_img_full']
        st.image(curr_img_full,use_container_width=True)

    buffer = io.BytesIO()
    s3.download_fileobj(BUCKET_NAME,curr_img_dir, buffer)
    buffer.seek(0)  # Bardzo ważne — ustawiamy początek pliku
        
    st.download_button(
        label="Pobierz ten obraz",
        data=buffer,
        file_name=curr_img_dir,
        mime="image/png"
    )
        
                          

# List of descriptions
with list_tab:
    filtered_descriptions_df = st.session_state["descriptions_df"]
    filtered_descriptions_df = filtered_descriptions_df[filtered_descriptions_df['Nr projektu'] != 0]
    st.dataframe(filtered_descriptions_df, hide_index=True)

    c0, c1, = st.columns([0.5,0.5])
    with c0:
        if st.button("Zapamiętaj te projekty",use_container_width=True):
            list_name=st.session_state["list_name"]
            list_file=f"{PATH_TO_DO}{list_name}"
            descriptions_df=st.session_state["descriptions_df"]
            save_df_as_public_csv(descriptions_df, BUCKET_NAME, list_file)
            st.success('Lista zapisana do pliku')
            st.rerun()
    with c1:
        if st.button("Usuń wszystkie swoje projekty",use_container_width=True):
            descriptions_df=pd.DataFrame([{"Nr projektu":0, "Tytuł":"","Rodzaj":"", "Opis":""}])
            list_name=st.session_state["list_name"]
            st.session_state["descriptions_df"]=descriptions_df
            save_df_as_public_csv(descriptions_df, BUCKET_NAME, list_name)
            st.success('Lista usunięta')
            st.rerun()


# Editing descriptions and image generation
with image_tab:
    descriptions_df=st.session_state["descriptions_df"]
    max_id=descriptions_df["Nr projektu"].max()
    project_id = st.number_input(
        "Sprawdź numer projektu na liście i wpisz go tutaj", 
        min_value=0, max_value=max_id, value=max_id, step=1
        )
    selected_project_df=pd.DataFrame([{"Nr projektu":1, "Tytuł":"", "Rodzaj":"", "Opis":""}])
    if project_id in descriptions_df["Nr projektu"].values:
        selected_project_df = descriptions_df[descriptions_df['Nr projektu'] == project_id]
        title = selected_project_df.iat[0,1]
        description_type = selected_project_df.iat[0,2]
        description_text = selected_project_df.iat[0,3]
                
    else:
        project_id=1
        st.markdown("Nie ma takiego projektu na liście")
        st.stop()

    c0, c1, = st.columns([0.2,0.8])
    with c0:
        st.session_state["corrected_title"] = st.text_area("Popraw tytuł", value=title)
        corrected_title=st.session_state["corrected_title"]
        st.markdown(f"Rysunek {description_type}")
            
    with c1:  
        st.session_state['description_text']=description_text
        st.session_state["corrected_description_text"] = st.text_area("Popraw i uzupełnij opis ",value=st.session_state["description_text"], height=150)
        corrected_description_text=st.session_state["corrected_description_text"]
        
    
    c0, c1, c2 = st.columns([0.333,0.333,0.333])
    with c0:
        if st.button('Zapisz zmiany', use_container_width=True):
            descriptions_df=st.session_state["descriptions_df"]
            descriptions_df.loc[descriptions_df['Nr projektu'] == project_id, 'Tytuł'] = corrected_title
            descriptions_df.loc[descriptions_df['Nr projektu'] == project_id, 'Rodzaj'] = description_type
            descriptions_df.loc[descriptions_df['Nr projektu'] == project_id, 'Opis'] = corrected_description_text
            st.session_state["descriptions_df"]=descriptions_df
            st.success('Zmiany zapisane')
            st.rerun()
    
    with c1:
        if st.button('Usuń ten opis',use_container_width=True):
            descriptions_df=st.session_state["descriptions_df"]
            list_name=st.session_state["list_name"]
            if project_id>0:
                descriptions_df = descriptions_df[descriptions_df['Nr projektu'] != project_id]
                st.session_state["descriptions_df"]=descriptions_df
                save_df_as_public_csv(descriptions_df, BUCKET_NAME, list_name)
                st.success('Opis usunięty')
                st.rerun()
            else:
                st.markdown("Nie ma nic do usunięcia")
                st.rerun()
            
    
    with c2:
        if st.button("Stwórz kolorowankę", use_container_width=True):
            with st.spinner("Zaraz pojawi się Twoja kolorowanka ..."):
                descriptions_df=st.session_state["descriptions_df"]
                descriptions_df.loc[descriptions_df['Nr projektu'] == project_id, 'Tytuł'] = corrected_title
                descriptions_df.loc[descriptions_df['Nr projektu'] == project_id, 'Rodzaj'] = description_type
                descriptions_df.loc[descriptions_df['Nr projektu'] == project_id, 'Opis'] = corrected_description_text
                st.session_state["descriptions_df"]=descriptions_df
                prepare_image_prompt(project_id)
                prompt_text=st.session_state['prompt_text']
                output_path=st.session_state['output_path']
                generate_image(prompt_text, output_path)
     
               
    curr_img_n=st.session_state["curr_img_n"]
    curr_img_dir=st.session_state['curr_img_dir']
    curr_img_full=st.session_state['curr_img_full']
    st.image(curr_img_full,use_container_width=True)
    
    buffer = io.BytesIO()
    s3.download_fileobj(BUCKET_NAME,curr_img_dir, buffer)
    buffer.seek(0)  # Bardzo ważne — ustawiamy początek pliku
        
    st.download_button(
        label="Pobierz obraz",
        data=buffer,
        file_name=curr_img_dir,
        mime="image/png"
    )

    

# Gallery
with gallery_tab:
    display_images_with_download()



# Save and logout
with logout_tab:
    if st.button("Wyloguj się", use_container_width=True):
        list_name=st.session_state["list_name"]
        save_df_as_public_csv(descriptions_df, BUCKET_NAME, list_name)
        st.session_state["user_name"]=""
        st.session_state["openai_api_key"]=""
        st.rerun()
   
    

    