import os
import re
import time
import nltk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from nltk.stem import WordNetLemmatizer

# Ensure necessary NLTK data is downloaded
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Preprocessing function
def preprocess_text(text):
    text = re.sub(r'\W', ' ', text)
    tokens = nltk.word_tokenize(text)
    tokens = [word.lower() for word in tokens]
    tokens = [word for word in tokens if word not in nltk.corpus.stopwords.words('english')]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

# Collect papers using Selenium
search_query = input("Enter your search query, you can use AND and OR between keywords: ")

load_dotenv()
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

catolicaLoginUrl = 'https://portal.catolicasc.org.br/FrameHTML/web/app/edu/PortalEducacional/login/'
driver.get(catolicaLoginUrl)

login = os.getenv('CATOLICA_LOGIN')
password = os.getenv('CATOLICA_PASS')

time.sleep(3)

# Login portal aluno
username_input = driver.find_element(By.CSS_SELECTOR, 'input#User')
password_input = driver.find_element(By.CSS_SELECTOR, 'input#Pass')
submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")

username_input.send_keys(login)
password_input.send_keys(password)
submit_button.click()

time.sleep(9)

# Visit the portal periodicals
driver.get(f'http://app.catolicasc.org.br/apps/csc_login?page=portalPeriodicos&Context=[CodSistema=S;Environment=PortalWeb;CodUsuario={login};CodUsuarioServico=-1;CodColigada=1;CodFilial=2;DataSistema=19/06/2024%2000:00:00;IdPrj=-1;CodTipoCurso=1;CodUnidadeBib=-1;CodLocPrt=-1;EduTipoUsr=A;RhTipoUsr=-1;ChapaFuncionario=-1;CodigoExterno=-1;ExercicioFiscal=-1]&key=L\FF\09\28B\FDc\DF\A4\21s\14\E75\40\E65\FF\B3\850\1Ec\D2\DFO\C8\12\B0\074\DD\C5\15G\22\EA\E4\0EPk\A1\D8\81\88\A8\CB\1D\2Df\2ERj\F4\99\ACW\7C\A6\92WcG\14\93\16\88\DDc\F3\CC\2E\F4\17\D8\97\1F\8E\DF\AE\2F\841\C8\BBD\92on\8CY\BD\F2\28\FF\B7\CD\14\9F\F1\A5\D1\27\E3W\90\D8\3Fk\7B\C0\EF\D5\7D\11r\ABL\AF\EC\91\9D\CA\AD\3Dg\15N\C5\D8\019\5B\9A\0Dl\3A\F4S\071\B5\F4\F6')

time.sleep(10)

# Input de busca
search_input = driver.find_element(By.CSS_SELECTOR, 'input#SearchTerm1')
search_button = driver.find_element(By.CSS_SELECTOR, 'input#SearchButton')

search_input.send_keys(search_query)
search_button.click()

time.sleep(10)

english_results_input = driver.find_element(By.CSS_SELECTOR, 'input[id*="cluster_Language%24english"]')
driver.execute_script("arguments[0].click();", english_results_input)

time.sleep(7)

radio_info = driver.find_element(By.CSS_SELECTOR, "label[for='results-format-d']")
driver.execute_script("arguments[0].click();", radio_info)

select_article_number = driver.find_element(By.CSS_SELECTOR, "select[name='1$pageOptionsResultsPerPageSelect']")
driver.execute_script("arguments[0].value = 50;", select_article_number)

filter_btn = driver.find_element(By.CSS_SELECTOR, 'button#pageOptionsUpdateButton')
driver.execute_script("arguments[0].click();", filter_btn)

time.sleep(5)

result_count_string = driver.find_element(By.CSS_SELECTOR, 'h1.page-title.alt')
result_count = re.search(r'[\d,]+$', result_count_string.text)

print(f"Found {result_count.group()} results")

# Collect and classify papers
papers = []

while True:
    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul.result-list h3.title-link-wrapper a')))
        
        titles = driver.find_elements(By.CSS_SELECTOR, 'ul.result-list h3.title-link-wrapper a')
        descriptions = driver.find_elements(By.CSS_SELECTOR, '.display-info')
        
        for title, description in zip(titles, descriptions):
            title_text = driver.execute_script("return arguments[0].textContent;", title)
            description_text = driver.execute_script("return arguments[0].textContent.replace(/\s+/g, ' ').trim();", description)
            papers.append({
                'title': title_text.strip(),
                'description': description_text.strip()
            })

        next_btn = driver.find_elements(By.CSS_SELECTOR, 'a[title="Next"]')
        if next_btn:
            next_btn[0].click()
            wait.until(EC.staleness_of(next_btn[0]))
        else:
            break

    except TimeoutException:
        print("Timeout while loading elements.")
        break
    except NoSuchElementException:
        print("Required elements not found.")
        break

driver.quit()

# Prepare the dataset for classification
if len(papers) < 2:
    print("Not enough data to train and test the classifier.")
    exit(1)

train_papers, test_papers = train_test_split(papers, test_size=0.3, random_state=42)

# Create labeled dataset for training
labeled_papers = [
    {'text': paper['description'], 'label': 'relevant' if i < len(train_papers) / 2 else 'irrelevant'}
    for i, paper in enumerate(train_papers)
]

texts = [preprocess_text(paper['text']) for paper in labeled_papers]
labels = [paper['label'] for paper in labeled_papers]

# Using TF-IDF and SVM pipeline
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
    ('svm', SVC(kernel='linear', probability=True))
])

# Hyperparameter tuning
param_grid = {'svm__C': [0.01, 0.1, 1, 10, 100]}
grid_search = GridSearchCV(pipeline, param_grid, cv=5)
grid_search.fit(texts, labels)

best_model = grid_search.best_estimator_

# Classify and filter test papers
test_texts = [preprocess_text(paper['description']) for paper in test_papers]
test_labels = best_model.predict(test_texts)

relevant_papers = [paper for paper, label in zip(test_papers, test_labels) if label == 'relevant']

# Print classified relevant papers
for paper in relevant_papers:
    print(f"Title: {paper['title']}")
    print(f"Description: {paper['description']}\n")

# Write collected and filtered data to a text file
with open('papers.txt', 'w', encoding='utf-8') as file:
    for paper in relevant_papers:
        file.write(f"Title: {paper['title']}\n")
        file.write(f"Description: {paper['description']}\n\n")

print("Data written to papers.txt")
