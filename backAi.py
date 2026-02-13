import nltk
import re
from nltk.tokenize import word_tokenize
from words2num import w2n
from nltk.tokenize.treebank import TreebankWordDetokenizer
import pypyodbc as podbc
import Levenshtein as lev
import unicodedata

global transform_prepositions
transform_prepositions = []

global words_food_array_desc
words_food_array_desc = []

global words_food_array_full
words_food_array_full = []

global words_food_array_definitive
words_food_array_definitive = []


def populateWordTokenDefinitive():
    conn = podbc.connect(
        "Driver={SQL Server Native Client 11.0};Server=LAPTOP-NMA04U3H\\SQLEXPRESS;Database=TFG;uid=sa;pwd=XXX;")

    cursor = conn.cursor()

    sql = (" select dino.comal_nombre "
           " ,dino.comal_descripcion "
           " ,dino.comal_img_url "
           " ,dino.caiw_brand "
           " ,dino.agc_caiw_category "
           " ,dino.caiw_name "
           " ,dino.comal_cantidad as comal_cantidad_dino "
           " ,dino.comal_precio as comal_precio_dino "
           " ,wal.comal_cantidad as comal_cantidad_wal "
           " ,wal.comal_precio as comal_precio_wal "
           " ,car.comal_cantidad as comal_cantidad_car "
           " ,car.comal_precio as comal_precio_car "
           " from (SELECT a.comal_nombre "
           " ,a.comal_descripcion "
           " ,a.comal_img_url "
           " ,a.comal_precio "
           " ,a.comal_cantidad "
           " ,b.caiw_brand "
           " ,d.agc_caiw_category "
           " ,b.caiw_name"
           " ,c.commar_nombre "
           " FROM [TFG].[dbo].[comercios_alimentos] a "
           " INNER JOIN [TFG].[dbo].[comercios_alimentos_items_web] b on b.caiw_id = a.caiw_id "
           " INNER JOIN [TFG].[dbo].[comercios_marcas] c on c.commar_id = a.commar_id "
           " INNER JOIN [TFG].[dbo].[alimentos_grupos_categorias] d on d.agc_id = b.agc_id "
           " WHERE c.commar_nombre = 'Super MaMi Dino' "
           " AND d.agc_category_group = 'Comestible') dino "
           " inner join (SELECT a.comal_nombre "
           " ,a.comal_descripcion "
           " ,a.comal_img_url "
           " ,a.comal_precio "
           " ,a.comal_cantidad "
           " ,b.caiw_brand "
           " ,d.agc_caiw_category "
           " ,b.caiw_name "
           " ,c.commar_nombre "
           " FROM [TFG].[dbo].[comercios_alimentos] a "
           " INNER JOIN [TFG].[dbo].[comercios_alimentos_items_web] b on b.caiw_id = a.caiw_id "
           " INNER JOIN [TFG].[dbo].[comercios_marcas] c on c.commar_id = a.commar_id "
           " INNER JOIN [TFG].[dbo].[alimentos_grupos_categorias] d on d.agc_id = b.agc_id "
           " WHERE c.commar_nombre = 'Walmart' "
           " AND d.agc_category_group = 'Comestible') wal on wal.comal_descripcion = dino.comal_descripcion "
           " inner join (SELECT a.comal_nombre "
           " ,a.comal_descripcion "
           " ,a.comal_img_url "
           " ,a.comal_precio "
           " ,a.comal_cantidad "
           " ,b.caiw_brand "
           " ,d.agc_caiw_category "
           " ,b.caiw_name"
           " ,c.commar_nombre "
           " FROM [TFG].[dbo].[comercios_alimentos] a "
           " INNER JOIN [TFG].[dbo].[comercios_alimentos_items_web] b on b.caiw_id = a.caiw_id "
           " INNER JOIN [TFG].[dbo].[comercios_marcas] c on c.commar_id = a.commar_id "
           " INNER JOIN [TFG].[dbo].[alimentos_grupos_categorias] d on d.agc_id = b.agc_id "
           " WHERE c.commar_nombre = 'Carrefour' "
           " AND d.agc_category_group = 'Comestible') car on car.comal_descripcion = dino.comal_descripcion ")
    cursor.execute(sql)
    data = cursor.fetchone()

    words_food_array = []
    while data:
        words_food_array.append(
            str(data[1].lower()) + " " + str(data[4].lower()))
        words_food_array_desc.append(str(data[1].lower()))
        words_food_array_full.append(str(data[0].lower()) + "|" + str(data[1].lower()) + "|" + str(data[2].lower()) + "|" + str(data[3].lower()) + "|" + str(data[4].lower()) + "|" + str(
            data[5].lower()) + "|" + str(data[6].lower()) + "|" + str(data[7].lower()) + "|" + str(data[8].lower()) + "|" + str(data[9].lower()) + "|" + str(data[10].lower()) + "|" + str(data[11].lower()))
        data = cursor.fetchone()
    conn.close()

    words_food_array_detokenize = TreebankWordDetokenizer().detokenize(words_food_array)
    words_food_array_tokenize = word_tokenize(words_food_array_detokenize)

    for palabra in words_food_array_tokenize:
        if not palabra.isnumeric():
            if not palabra in transform_prepositions:
                if palabra != "." and palabra != "x" and palabra != "gr" and palabra != "ml" and palabra != "cm" and palabra != "-" and palabra != "kg" and len(palabra) > 1:
                    words_food_array_definitive.append(palabra)


def populateTransformPrepositions():
    conn = podbc.connect(
        "Driver={SQL Server Native Client 11.0};Server=LAPTOP-NMA04U3H\\SQLEXPRESS;Database=TFG;uid=sa;pwd=XXX;")

    cursor = conn.cursor()
    sql = (" select * from [TFG].[dbo].[transform_prepositions] ")
    cursor.execute(sql)
    data = cursor.fetchone()

    while data:
        transform_prepositions.append(data[1].lower())
        data = cursor.fetchone()


def doBackAi(text):
    MortySmith = ""

    texto = text
    texto = strip_accents(texto)
    punctuation = re.compile(r'[\W_]+')
    texto_limpio1 = punctuation.sub(" ", texto)
    texto_token_limpio = word_tokenize(texto_limpio1)
    if "MortySmith" in texto_token_limpio:
        MortySmith = "MortySmith"
    texto_token_letras_a_numeros = []

    for palabra in texto_token_limpio:
        texto_token_letras_a_numeros.append(
            conversorFracciones(conversorPalabras(palabra)))

    texto_tokenize = TreebankWordDetokenizer().detokenize(texto_token_letras_a_numeros)
    texto_token_limpio = word_tokenize(texto_tokenize)
    texto_token_letras_a_numeros = texto_token_limpio

    print(texto_token_letras_a_numeros)

    texto_token_prev = []
    for palabra in texto_token_letras_a_numeros:
        if not palabra in transform_prepositions:
            for palabra2 in words_food_array_definitive:
                Ratio = lev.ratio(palabra.lower(), palabra2.lower())
                if Ratio > 0.90:
                    texto_token_prev.append(palabra)
    texto_token_prev = list(set(texto_token_prev))

    texto_token_definitivo = []
    for palabra in texto_token_letras_a_numeros:
        for palabra2 in texto_token_prev:
            if palabra.lower() == palabra2.lower():
                texto_token_definitivo.append(palabra)

    print(texto_token_definitivo)

    quotes_ngrams3 = list(nltk.ngrams(texto_token_letras_a_numeros, 3))
    alimentos = []
    if len(texto_token_letras_a_numeros) > 2:
        for word1, word2, word3 in quotes_ngrams3:
            if (comprobadorDeAlimentosUnaPalabra(word1, words_food_array_definitive) != None) and (comprobadorDeAlimentosUnaPalabra(word1, words_food_array_definitive) >= 0.9) and word2 in transform_prepositions and (comprobadorDeAlimentosUnaPalabra(word3, words_food_array_definitive) != None) and (comprobadorDeAlimentosUnaPalabra(word3, words_food_array_definitive) >= 0.9):
                if (comprobadorDeAlimentosDesc(word1 + " " + word2 + " " + word3, words_food_array_desc, transform_prepositions) == True):
                    alimentos.append(word1 + " " + word2 + " " + word3)

    quotes_ngrams2 = list(nltk.ngrams(texto_token_letras_a_numeros, 2))
    if len(texto_token_letras_a_numeros) > 1:
        for word1, word2 in quotes_ngrams2:
            if (comprobadorDeAlimentosUnaPalabra(word1, words_food_array_definitive) != None) and (comprobadorDeAlimentosUnaPalabra(word1, words_food_array_definitive) >= 0.9) and (comprobadorDeAlimentosUnaPalabra(word2, words_food_array_definitive) != None) and (comprobadorDeAlimentosUnaPalabra(word2, words_food_array_definitive) >= 0.9):
                if (comprobadorDeAlimentosDesc(word1 + " " + word2, words_food_array_desc, transform_prepositions) == True):
                    alimentos.append(word1 + " " + word2)

    quotes_ngrams3 = list(nltk.ngrams(texto_token_letras_a_numeros, 3))
    if len(texto_token_letras_a_numeros) > 2:
        for word1, word2, word3 in quotes_ngrams3:
            if (comprobadorDeAlimentosUnaPalabra(word1, words_food_array_definitive) != None) and (comprobadorDeAlimentosUnaPalabra(word1, words_food_array_definitive) >= 0.9) and (comprobadorDeAlimentosUnaPalabra(word2, words_food_array_definitive) != None) and (comprobadorDeAlimentosUnaPalabra(word2, words_food_array_definitive) >= 0.9) and (comprobadorDeAlimentosUnaPalabra(word3, words_food_array_definitive) != None) and (comprobadorDeAlimentosUnaPalabra(word3, words_food_array_definitive) >= 0.9):
                if (comprobadorDeAlimentosDesc(word1 + " " + word2 + " " + word3, words_food_array_desc, transform_prepositions) == True):
                    alimentos.append(word1 + " " + word2 + " " + word3)

    quotes_ngrams4 = list(nltk.ngrams(texto_token_letras_a_numeros, 4))
    if len(texto_token_letras_a_numeros) > 3:
        for word1, word2, word3, word4 in quotes_ngrams4:
            if (comprobadorDeAlimentosUnaPalabra(word1, words_food_array_definitive) != None) and (comprobadorDeAlimentosUnaPalabra(word1, words_food_array_definitive) >= 0.9) and word2 in transform_prepositions and (comprobadorDeAlimentosUnaPalabra(word3, words_food_array_definitive) != None) and (comprobadorDeAlimentosUnaPalabra(word3, words_food_array_definitive) >= 0.9) and (comprobadorDeAlimentosUnaPalabra(word4, words_food_array_definitive) != None) and (comprobadorDeAlimentosUnaPalabra(word4, words_food_array_definitive) >= 0.9):
                if (comprobadorDeAlimentosDesc(word1 + " " + word2 + " " + word3 + " " + word4, words_food_array_desc, transform_prepositions) == True):
                    alimentos.append(word1 + " " + word2 +
                                     " " + word3 + " " + word4)

    lista_definitiva = []
    for palabra in texto_token_definitivo:
        lista_definitiva.append(palabra)
    for palabra in alimentos:
        lista_definitiva.append(palabra)

    lista_alimentos_definitiva = eliminoPreposicionesInicioFinal(
        list(set(lista_definitiva)))

    lista_alimentos_return = []
    lista_comidas = []
    for alimento in lista_alimentos_definitiva:
        comida = comparaComidaListaAlimentosDefinitiva(
            alimento, words_food_array_full, transform_prepositions)
        dev = dejarListaUnicaParaRetornar(lista_comidas, comida)
        if dev == 0:
            lista_alimentos_return.append("1|" + alimento + "|" + comida)
        elif MortySmith == "MortySmith":
            lista_alimentos_return.append("1|" + alimento + "|" + comida)
        lista_comidas.append(comida)
        lista_comidas = list(set(lista_comidas))

    for lar in lista_alimentos_return:
        print(lar)
    return lista_alimentos_return


def dejarListaUnicaParaRetornar(lista_comidas, comida):
    dev = 0
    for comida1 in lista_comidas:
        if comida1 == comida:
            dev = 1
            return dev
    return dev


def eliminoPreposicionesInicioFinal(lista_definitiva):
    lista_alimentos_definitiva = []
    for palabra in lista_definitiva:
        p = palabra.split()
        if not (len(p) > 1 and (p[0] in transform_prepositions or p[len(p) - 1] in transform_prepositions)):
            lista_alimentos_definitiva.append(palabra)
    return lista_alimentos_definitiva


def conversorFracciones(i):
    if i == '¼':
        return 'un cuarto'
    else:
        if i == '½':
            return 'medio'
        else:
            if i == '¾':
                return 'tres cuartos'
            else:
                return i


def conversorPalabras(i):
    if i == 'clara':
        return 'huevo'
    else:
        if i == 'claras':
            return 'huevos'
        else:
            if i == 'yema':
                return 'huevo'
            else:
                return i


def comprobadorDePalabrasExacto(word1, word2):
    Ratio = lev.ratio(word1.lower(), word2.lower())
    if Ratio >= 0.9:
        return Ratio


def comprobadorDePalabras(word1, word2):
    Ratio = lev.ratio(word1.lower(), word2.lower())
    if Ratio != None:
        return Ratio


def comprobadorDeAlimentosUnaPalabra(word1, words_food_array_definitive):
    for palabra2 in words_food_array_definitive:
        Ratio = lev.ratio(word1.lower(), palabra2.lower())
        if Ratio >= 0.9:
            return Ratio


def comprobadorDeAlimentosCat(word1, words_food_array_cat):
    for palabra2 in words_food_array_cat:
        Ratio = lev.ratio(word1.lower(), palabra2.lower())
        if Ratio != None:
            return Ratio


def comprobadorDeAlimentosDesc(word1, words_food_array_desc, transform_prepositions):
    for palabra2 in words_food_array_desc:
        Ratio = lev.ratio(word1.lower(), palabra2.lower())
        if Ratio != None:
            word1Split = word1.split()
            palabra2Split = palabra2.split()
            if comprobarPalabras(word1Split, palabra2Split, transform_prepositions) == True:
                return True


def comprobarPalabras(word1Split, palabra2Split, transform_prepositions):
    existe = []
    for word in word1Split:
        if not word in transform_prepositions:
            existe.append(comprobarUnaPalabra(
                word, palabra2Split, transform_prepositions))
    if 0 in existe:
        return False
    else:
        return True


def comprobarUnaPalabra(word, palabra2Split, transform_prepositions):
    for palabra in palabra2Split:
        if not palabra in transform_prepositions:
            Ratio = comprobadorDePalabrasExacto(word.lower(), palabra.lower())
            if Ratio != None and Ratio >= 0.90:
                return 1
    return 0


def comprobarUnaPalabraExacto(word, palabra2Split, transform_prepositions):
    for palabra in palabra2Split:
        if not palabra in transform_prepositions:
            Ratio = comprobadorDePalabrasExacto(
                word.lower(), palabra.lower())
            if Ratio != None and Ratio == 1:
                return 1
    return 0


def comprobarVariasPalabraExacto(wordSplit, palabra2Split, transform_prepositions):
    palabra1reservada = ""
    palabra2reservada = ""
    primero = 0
    for palabra2 in palabra2Split:
        if not palabra2 in transform_prepositions:
            for palabra1 in wordSplit:
                if not palabra1 in transform_prepositions:
                    Ratio = comprobadorDePalabrasExacto(
                        palabra1.lower(), palabra2.lower())
                    if Ratio != None and Ratio == 1:
                        if palabra2reservada == "" and palabra1reservada != "" and primero == 1:
                            palabra2reservada = palabra1
                        if palabra1reservada == "":
                            palabra1reservada = palabra1
                            primero = 1
                        if palabra1reservada != "" and palabra2reservada != "":
                            return 1
    return 0


def comparaComidaListaAlimentosDefinitiva(alimento, words_food_array_full, transform_prepositions):
    foodReturn = ""
    precio = 99999999.999
    coincidenciaExacta1 = 0
    coincidenciaExacta2 = 0
    for food in words_food_array_full:
        foodVector = food.split("|")
        if comprobadorDePalabrasExacto(alimento, foodVector[4]) != None and comprobadorDePalabrasExacto(alimento, foodVector[4]) >= 0:
            if comprobadorDePalabrasExacto(alimento, foodVector[4]) != None and comprobadorDePalabrasExacto(alimento, foodVector[4]) == 1:
                coincidenciaExacta1 = 1
                precio = 99999999.999
            if float(foodVector[7]) < precio:
                precio = float(foodVector[7])
                foodReturn = food
            elif float(foodVector[9]) < precio:
                precio = float(foodVector[9])
                foodReturn = food
            elif float(foodVector[11]) < precio:
                precio = float(foodVector[11])
                foodReturn = food
            else:
                precio = precio
                foodReturn = foodReturn
        if comprobadorDePalabrasExacto(alimento, foodVector[0]) != None and comprobadorDePalabrasExacto(alimento, foodVector[0]) >= 0:
            if comprobadorDePalabrasExacto(alimento, foodVector[0]) != None and comprobadorDePalabrasExacto(alimento, foodVector[0]) == 1:
                coincidenciaExacta2 = 1
                precio = 99999999.999
            if float(foodVector[7]) < precio:
                precio = float(foodVector[7])
                foodReturn = food
            elif float(foodVector[9]) < precio:
                precio = float(foodVector[9])
                foodReturn = food
            elif float(foodVector[11]) < precio:
                precio = float(foodVector[11])
                foodReturn = food
            else:
                precio = precio
                foodReturn = foodReturn
        if comprobadorDePalabras(alimento, foodVector[1]) != None and comprobadorDePalabras(alimento, foodVector[1]) >= 0 and comprobarUnaPalabraExacto(alimento, foodVector[1].split(), transform_prepositions) == 1:
            if float(foodVector[7]) < precio and coincidenciaExacta1 == 0 and coincidenciaExacta2 == 0:
                precio = float(foodVector[7])
                foodReturn = food
            elif float(foodVector[9]) < precio and coincidenciaExacta1 == 0 and coincidenciaExacta2 == 0:
                precio = float(foodVector[9])
                foodReturn = food
            elif float(foodVector[11]) < precio and coincidenciaExacta1 == 0 and coincidenciaExacta2 == 0:
                precio = float(foodVector[11])
                foodReturn = food
            else:
                precio = precio
                foodReturn = foodReturn
        if comprobadorDePalabras(alimento, foodVector[1]) != None and comprobadorDePalabras(alimento, foodVector[1]) >= 0 and len(alimento.split()) > 1 and comprobarVariasPalabraExacto(alimento.split(), foodVector[1].split(), transform_prepositions) == 1:
            if float(foodVector[7]) < precio and coincidenciaExacta1 == 0 and coincidenciaExacta2 == 0:
                precio = float(foodVector[7])
                foodReturn = food
            elif float(foodVector[9]) < precio and coincidenciaExacta1 == 0 and coincidenciaExacta2 == 0:
                precio = float(foodVector[9])
                foodReturn = food
            elif float(foodVector[11]) < precio and coincidenciaExacta1 == 0 and coincidenciaExacta2 == 0:
                precio = float(foodVector[11])
                foodReturn = food
            else:
                precio = precio
                foodReturn = foodReturn
        if comprobadorDePalabras(alimento, foodVector[1]) != None and comprobadorDePalabras(alimento, foodVector[1]) >= 0 and comprobarUnaPalabraNOExacto(alimento, foodVector[1].split(), transform_prepositions) == 1:
            if float(foodVector[7]) < precio and coincidenciaExacta1 == 0 and coincidenciaExacta2 == 0:
                precio = float(foodVector[7])
                foodReturn = food
            elif float(foodVector[9]) < precio and coincidenciaExacta1 == 0 and coincidenciaExacta2 == 0:
                precio = float(foodVector[9])
                foodReturn = food
            elif float(foodVector[11]) < precio and coincidenciaExacta1 == 0 and coincidenciaExacta2 == 0:
                precio = float(foodVector[11])
                foodReturn = food
            else:
                precio = precio
                foodReturn = foodReturn
        else:
            precio = precio
            foodReturn = foodReturn
    return foodReturn


def comprobarUnaPalabraNOExacto(word, palabra2Split, transform_prepositions):
    for palabra in palabra2Split:
        if not palabra in transform_prepositions:
            Ratio = comprobadorDePalabrasNOExacto(
                word.lower(), palabra.lower())
            if Ratio != None and Ratio > 0.90:
                return 1
    return 0


def comprobadorDePalabrasNOExacto(word1, word2):
    Ratio = lev.ratio(word1.lower(), word2.lower())
    if Ratio >= 0.90:
        return Ratio


def strip_accents(text):

    try:
        text = unicode(text, 'utf-8')
    except NameError:  # unicode is a default on python 3
        pass

    text = unicodedata.normalize('NFD', text)\
        .encode('ascii', 'ignore')\
        .decode("utf-8")

    return str(text)
