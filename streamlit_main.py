#############################################################################
##########  "Parfois nous sommes sur le chemin mais on l'ignore    ##########
##########    jusqu'à ce qu'on atteigne notre destination"         ##########
##########                              Brice KENGNI ZANGUIM.      ##########
#############################################################################

#############################################################################
###########           URL de déployement sur Streamlit            ###########
#############################################################################

# 

###################################################################
##########    Importation de bibliothèque utilitaires    ##########
###################################################################

import streamlit as st
import numpy as np
import requests
import pandas as pd
from io import BytesIO



########################################################################################
##########         conversion de chaine de caractères en DataFrame             #########
########################################################################################

def str_bytes_encode_to_dataframe( myencode ) :
    """
    - Description :
    --------------
        La fonction prends en entrée une chaine de caractères ou un objet Bytes et renvois un DataFrame

        En effet dans l'API streamlit j'ai besoin de DataFrame des articles déjà lu et à recommander à l'utilisateur
        D'un autre côté les fonction lambda d'Azur ne renvoient que des chaines de caractère au terme d'une requêtte http.

        Pour contourner le problème j'ai donc eu l'idée de transformer mon DataFrame en chaine de caractère sous le format "<valeur_0> <valeur_1> <valeur_2> ... <valeur_n>"
    
    - Paramètres :
    --------------
        myencode : str or Bytes
            Chaine de caractères contenant les données de mon DataFrame
            
    - Return : DataFrame
    ---------
    
    """
    output = myencode
    if type(output) == str :
        # Si je reçois une chaine de caractères je transforme en Bytes
        output = output.encode()

    output = BytesIO(output)
    #output.seek(0)
    return pd.read_csv(output)


############################################################################
##########    paramétrisation des caractéristiques des buttons    ##########
############################################################################
st.title("Recommandation de Livres")
st.markdown("""
<style>
    .stButton button {
        background-color: green ;
        #font-weight: bold;
    }

</style>
""", unsafe_allow_html=True)


with st.sidebar:
   
    ###############################################################################################################
    ############################    Afficher un message pour expliquer l'application    ###########################
    ###############################################################################################################

	st.write("# Interface graphique de test de l'application de recommandation d'articles réalisée par Brice KENGNI ZANGUIM")


#############################################################################################################
#############################     acquisition du nom de modèle à utiliser       #############################
#############################################################################################################


	st.write("###  1 - Quels models voudriez vous utiliser  ?")
	st.write("###### plusieurs choix sont possibles")

	content_base = st.checkbox("Content-based Recommandation", True)
	SVD = st.checkbox("Collaborative Filtering - SVD")
	distance = st.checkbox("Embedding - Distance Similarité")
	cosinus = st.checkbox("Embedding - Cosinus Similarité")


#############################################################################################################
###########     Actualisation de la variable models contenant la liste des modèles à utiliser     ###########
#############################################################################################################

	models = []
	
	if content_base :
		models.append("Cb")
	if SVD :
		models.append("Svd")
	if distance :
		models.append("Distance")
	if cosinus :
		models.append("Cosinus")


#############################################################################################################
###########        Nombre de recommandation à proposer à l'utilisateur pour chaque modèle         ###########
#############################################################################################################

	st.write("###  2 - Quel est le nombre d'articles à recommander  ?")
	n = st.slider( label ="",
				   min_value = 1, 
				   max_value = 25, 
				   value = 10
				 )

#############################################################################################################
######################          Acquisition de l'identifiant de l'utilisateur          ######################
#############################################################################################################
	data = pd.read_csv("DataFrames/data.csv")
	user_list = np.unique( data.user_id.values )

	st.write("###  3 - Quel est l'identifiant de l' utilisateur à qui recommander les articles  ?")

	user_id =  st.slider( label ="",
				   min_value = 0, 
				   max_value = len(user_list) -1, 
				   value = 5
				 )

	user_id = user_list[user_id]

	recomand = st.button("Recommander" )


############################################################################
############      Url d'accès à l'application Azur fonction      ###########
############################################################################

azur_function_url = "https://recommandationserverlessapp.azurewebsites.net/api/HttpTrigger1/"
parameters = {  "user_id"         :   user_id, 
                "recommand_count" :   n,
                "if_recommand"    :   0
             }


#######################################################################################
######   Affichage de la liste des articles déjà consultés par l'utilisateur    #######
#######################################################################################
if recomand :
	user_articles_list = requests.get( azur_function_url, params = parameters ).text
	user_articles_list = str_bytes_encode_to_dataframe(user_articles_list)


	if len(user_articles_list) == 1:
		st.write("###  A - Article déjà consulté par l'utilisateur")
	elif len(user_articles_list) > 1:
		st.write("###  A - Articles déjà consultés par l'utilisateur")

	st.write( user_articles_list )


######################################################################################
################            Effectuation des recommandation             ##############
######################################################################################

	parameters["if_recommand"] = 1
    
    #  Pour chacun des modèles, on effectue une requête pour acquérir des recommandations de livres
	recommandation = []
	for mod in models :
		parameters["models"] = mod
		articles_recommandes = requests.get( azur_function_url, params = parameters ).text
		articles_recommandes = str_bytes_encode_to_dataframe( articles_recommandes )
		
		recommandation.append( articles_recommandes )


	#######################################################################################
	###########            Affichage des recommandations d'articles             ###########
	#######################################################################################

	st.write(f"###  B - Recommandations d'articles à l'utilisateur")

	columns = st.columns(len(models))
	for i in range(len(models)) :
		with columns[i] :
		    st.write(f"###### {i+1} - {models[i]}")
		    st.write(recommandation[i])
		
#st.balloons()





