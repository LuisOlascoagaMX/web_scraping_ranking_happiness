from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import csv

class RankingHappiness():

    def __init__(self):
        self.url = "https://es.theglobaleconomy.com/rankings/happiness/"

    
    def __get_html(self, url):
        #Inicializamos el web driver
        driver_path = "/chromedriver.exe"
        
        #Pruebas de uso del userAgent
        driver = webdriver.Chrome(executable_path=driver_path)
        print(driver.execute_script("return navigator.userAgent;"))
        
        #obtenemos la sesión con chrome para la url proporcionada
        driver.get(url=url)
        return driver

    def __get_html_element(self, page_source):
        #HAcemos la busqueda y obtenemos la sección donde estan los datos referentes a los indices de felicidad
        element = page_source.find_element(value="benchmarkTable")
        return element.text


    def __cleanup_html_element(self, element_text, page_source):
        #Obtenemos todos los años en donde se ha aplicado el estudio.
        regions = []
        selectEle = page_source.find_element(value="regions")
        options=selectEle.find_elements(By.XPATH, "option")
        for optionEle in options:
            regions.append(optionEle.text)

        #Comenzamos con el encabezado del csv    
        row_values = "country_name, Index_of_happiness, global_rank, available_data_date, regions"
        row_values_csv = row_values
        
        #Iteramos por cada año en donde se haya aplicado el estudio, obtenemos los datos. Por medio de selenium hacemos esto de forma automática
        for region in regions:  
            #Obtenemos los valores del combobox referente a los años
            selectEle = page_source.find_element(value="regions")
            options=selectEle.find_elements(By.XPATH, "option")
            for optionEle in options:
                if optionEle.text == region:        
                    #Por medio de selenium, hacemos click en el combo y escogemos el año de forma automática
                    optionEle.click()
                    #Cuidamos de no saturar las peticiones el web server
                    sleep(2)
                    element = page_source.find_element(value="benchmarkTable")

                    #Obtenemos todos los valores de los indices y sus rankings.
                    element_text = element.text
                    v_is_first_column = True

                    #Se comienza con la separación de datos obtenidos de la página.
                    for line in element_text.splitlines():    
                        if v_is_first_column:
                            pass
                        else:
                            pivote = 0
                            for letter in line:
                                if letter.isnumeric():
                                    break
                                else:
                                    pivote = pivote + 1
                            
                            #Limpiamos los campos de caracteres de "," que continen los datos de los indices y rankings
                            country_name = line[0:pivote] 
                            hapiness_ranking = line.replace(country_name, "")
                            hapiness_ranking = hapiness_ranking.replace(" - ", "-")
                            hapiness_ranking = hapiness_ranking.replace(" ", ",")
                            country_name = country_name.replace(",", " ")
                            country_name = country_name[0:len(country_name)-1] + ","
                            row_values = country_name + hapiness_ranking + "," + region
                            row_values_csv = row_values_csv + "\n" + row_values    
                        v_is_first_column = False
                        print(row_values)
                    print("""""" + row_values_csv + """""")
                    break              
        return row_values_csv

    def __create_csv_file(self, data_to_export):
        #Se construye el csv con en la carpeta "dataset"
        with open("../dataset/happiness_ranking.csv", "w") as file:
            file.write("""""" + data_to_export + """""")        
        return True

    def generate_ranking_happiness(self):
        page_source = self.__get_html(self.url)
        page_source_elements = self.__get_html_element(page_source)
        values_to_export = self.__cleanup_html_element(page_source_elements, page_source)
        is_file_generated = self.__create_csv_file(values_to_export)
        return self
