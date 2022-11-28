import pandas as pd
import xml.etree.cElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import sys
import time
import re
import signal


def extract():
    pizza_types = pd.read_csv('pizza_types.csv', encoding='latin1')
    orders = pd.read_csv('orders_2016.csv', encoding='latin1', sep=';')
    order_details = pd.read_csv(
        'order_details_2016.csv', encoding='latin1', sep=';')
    pizza = pd.read_csv(
        'pizzas.csv', encoding='latin1')
    predict = pd.read_csv('compra_semanal_2017.csv')
    return [pizza_types, orders, order_details, pizza], predict


def handler(signal, frame):
    entrada = input('Has pulsado ctrl+c. Quieres salir del programa(Y/n): ')
    if entrada == 'Y':
        print('Saliendo de manera controlada')
        sys.exit(1)
    else:
        print('Continuando con la ejecucion')


def crear_xml():
    csvs, prediccion = extract()
    raiz = Element('Informe_Pizzeria_Maven')
    tipo = SubElement(raiz, 'Tipologia_Datos_Pizzeria_Maven')
    pred = SubElement(raiz, 'Prediccion_Semanal')
    pizzas = SubElement(tipo, 'pizzas.csv', {'rows': '96'})
    orders = SubElement(tipo, 'orders.csv', {'rows': '21350'})
    order_details = SubElement(tipo, 'order_details.csv', {'rows': '48620'})
    pizza_types = SubElement(tipo, 'pizza_types.csv', {'rows': '32'})
    return raiz, pizzas, orders, order_details, pizza_types, csvs, pred, prediccion


def load(raiz):
    arbol = ET.ElementTree(raiz)
    arbol.write('informe_pizzeria.xml')


def crear_ramas_tipo(pizzas, pizza_types, orders, order_details, csvs):
    jerar_xml = [pizza_types, orders, order_details, pizzas]
    for i in range(len(csvs)):
        columnas = csvs[i].columns.values
        for j in columnas:
            col1 = SubElement(jerar_xml[i], str(j))
            tipo = csvs[i][j].dtype
            a = csvs[i][j].isnull().value_counts()
            # si no ha encontrado ningun null que el numero total sea cero.
            n_nulls = a[1] if len(a) > 1 else 0
            atribs1 = SubElement(col1, 'ingredient', {
                                 'type': f'{tipo}', 'nulls': f'{n_nulls}'})


def crear_ramas_pred(prediccion, pred):
    for i in range(len(prediccion)):
        col1 = SubElement(pred, f'Week-{i+1}')
        for j in prediccion.columns.values:
            cant = prediccion.loc[i, j]
            if re.search('salami', j, re.IGNORECASE):
                j = 'salami'
            j = re.sub(' |-|&|<|>', '_', j)  # Caracteres que no acepta xml
            atribs = SubElement(col1, 'atribs', {f'{j}': f'{cant}'})


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)
    raiz, pizzas, orders, order_details, pizza_types, csvs, pred, prediccion = crear_xml()
    crear_ramas_tipo(pizzas, pizza_types, orders, order_details, csvs)
    crear_ramas_pred(prediccion, pred)
    load(raiz)
