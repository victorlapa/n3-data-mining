from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import os
import time

driver = webdriver.Chrome()

load_dotenv()

# Setup
for i in range(1):
    print('Digite a Palavra-Chave 1 para busca: ')
    input("Press Enter to continue...")

catolicaLoginUrl = 'https://portal.catolicasc.org.br/FrameHTML/web/app/edu/PortalEducacional/login/'
login = os.getenv('CATOLICA_LOGIN')
password = os.getenv('CATOLICA_PASS')

driver.get(catolicaLoginUrl)

time.sleep(3)

# Login portal aluno
username_input = driver.find_element(By.CSS_SELECTOR, 'input#User')
password_input = driver.find_element(By.CSS_SELECTOR, 'input#Pass')
submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")

username_input.send_keys(login)
password_input.send_keys(password)

submit_button.click()

time.sleep(9)

# Visita ao portal periodicos
driver.get('http://app.catolicasc.org.br/apps/csc_login?page=portalPeriodicos&Context=[CodSistema=S;Environment=PortalWeb;CodUsuario=victor.lapa;CodUsuarioServico=-1;CodColigada=1;CodFilial=2;DataSistema=19/06/2024%2000:00:00;IdPrj=-1;CodTipoCurso=1;CodUnidadeBib=-1;CodLocPrt=-1;EduTipoUsr=A;RhTipoUsr=-1;ChapaFuncionario=-1;CodigoExterno=-1;ExercicioFiscal=-1]&key=L\FF\09\28B\FDc\DF\A4\21s\14\E75\40\E65\FF\B3\850\1Ec\D2\DFO\C8\12\B0\074\DD\C5\15G\22\EA\E4\0EPk\A1\D8\81\88\A8\CB\1D\2Df\2ERj\F4\99\ACW\7C\A6\92WcG\14\93\16\88\DDc\F3\CC\2E\F4\17\D8\97\1F\8E\DF\AE\2F\841\C8\BBD\92on\8CY\BD\F2\28\FF\B7\CD\14\9F\F1\A5\D1\27\E3W\90\D8\3Fk\7B\C0\EF\D5\7D\11r\ABL\AF\EC\91\9D\CA\AD\3Dg\15N\C5\D8\019\5B\9A\0Dl\3A\F4S\071\B5\F4\F6')


time.sleep(10)

# Input de busca
search_input = driver.find_element(By.CSS_SELECTOR, 'input#SearchTerm1')
search_button = driver.find_element(By.CSS_SELECTOR, 'input#SearchButton')

search_input.send_keys(keyword1)
search_button.click()

time.sleep(10)

driver.quit()